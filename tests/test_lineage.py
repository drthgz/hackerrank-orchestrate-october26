"""Adversarial ownership and state proofs for the isolated lineage experiment."""
import unittest
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))

from audit.models import Observation, timestamp
from evaluation.lineage import LineageIndex, check_resource
from evaluation.historical_lineage import investigate_split
from audit.inputs import Inputs
from audit.models import Request, Result, EvidenceFile
from audit.prediction import write_predictions
from audit.contract import read_output


EARLY = '2026-01-01T00:00:00Z'
MIDDLE = '2026-02-01T00:00:00Z'
LATE = '2026-03-01T00:00:00Z'
AFTER = '2026-04-01T00:00:00Z'
T = timestamp
RULES = [dict(rule_id='rule-account',data_category='USER_PROFILE',condition='Always',required_action='DELETE'),
         dict(rule_id='rule-analytics',data_category='ANALYTICS_PROFILE',
              condition='Record is still attributable to a user',required_action='ANONYMIZE')]


def identity(uid='subject-amber', email='amber@example.invalid'):
    return dict(user_id=uid,email=email,phone='',email_hash='',name='',updated_at=EARLY)


def obs(when=MIDDLE, resource='resource-copper', system='account_service', category='USER_PROFILE',
        present=True, copy='copy-primary', evidence='witness-green', source='profile_lookups', **facts):
    return Observation(system,resource,category,copy,present,T(when),None,evidence,T(when),source,(),facts)


def catalog(when=MIDDLE, uid='subject-amber',email='amber@example.invalid',resource='resource-copper'):
    return dict(activity_id='catalog-witness',event_time=when,event_type='LINK_RESOURCE_IDENTITY',
        source_system='data_catalog',target_system='account_service',resource_id=resource,
        reported_result='SUCCESS',details=f'Data catalog linked {resource} ({resource}) to {email} and {uid}.')


class LineageTests(unittest.TestCase):
    def index(self, observations=(), history=(), identities=None, activity=()):
        return LineageIndex(identities or [identity()],history,observations,activity)

    def test_explicit_catalog_links_only_ownership(self):
        i=self.index(activity=[catalog()]); e,r=i.edges_at(T(LATE))
        self.assertEqual(len(e),1); self.assertFalse(r)
        self.assertEqual(e[0].provenance[0],'catalog-witness')
        check=check_resource(i,e,'subject-amber','account_service','resource-copper',T(LATE),RULES)
        self.assertTrue(check['lineage_proven']); self.assertFalse(check['state_proven'])

    def test_workflow_success_cannot_link_identity(self):
        a={**catalog(), 'event_type':'DELETE_RECORD'}
        self.assertEqual(self.index(activity=[a]).edges_at(T(LATE))[0],())

    def test_shared_email_does_not_link_either_person(self):
        people=[identity(),identity('subject-blue','amber@example.invalid')]
        i=self.index([obs(email='amber@example.invalid')],identities=people)
        self.assertEqual(i.edges_at(T(LATE))[0],())

    def test_shared_alias_with_stable_reference_is_disambiguated(self):
        people=[identity(),identity('subject-blue','amber@example.invalid')]
        i=self.index([obs(email='amber@example.invalid',user_id='subject-amber')],identities=people)
        self.assertEqual({e.subject for e in i.edges_at(T(LATE))[0]},{'subject-amber'})

    def test_conflicting_stable_and_alias_is_rejected(self):
        people=[identity(),identity('subject-blue','blue@example.invalid')]
        i=self.index([obs(email='blue@example.invalid',user_id='subject-amber')],identities=people)
        e,r=i.edges_at(T(LATE)); self.assertFalse(e); self.assertIn('conflicts',r[0]['reason'])

    def test_identifier_rotation_preserves_historical_provenance(self):
        history=[dict(audit_id='rotation-witness',user_id='subject-amber',field_name='email',
                      event_time=MIDDLE,old_value='old@example.invalid',new_value='amber@example.invalid')]
        i=self.index([obs(when=LATE,email='old@example.invalid')],history)
        e,_=i.edges_at(T(LATE)); self.assertEqual(len(e),1)
        self.assertIn('rotation-witness',e[0].provenance)
        old=[a for a in i.aliases if a.value=='old@example.invalid'][0]
        self.assertIsNone(old.valid_from); self.assertEqual(old.valid_until,T(MIDDLE))

    def test_reused_identifier_stays_ambiguous(self):
        people=[identity(),{**identity('subject-blue'), 'updated_at':LATE}]
        i=self.index([obs(when=LATE,email='amber@example.invalid')],identities=people)
        self.assertFalse(i.edges_at(T(AFTER))[0])

    def test_future_snapshot_does_not_backfill_ownership(self):
        i=self.index([obs(when=MIDDLE,email='amber@example.invalid')],identities=[{**identity(),'updated_at':LATE}])
        self.assertFalse(i.edges_at(T(AFTER))[0])

    def test_reassignment_ends_old_resource_interval(self):
        people=[identity(),identity('subject-blue','blue@example.invalid')]
        rows=[obs(user_id='subject-amber'),obs(when=LATE,user_id='subject-blue')]
        i=self.index(rows,identities=people); e,_=i.edges_at(T(AFTER))
        old=next(x for x in e if x.subject=='subject-amber')
        self.assertEqual(old.valid_until,T(LATE))
        self.assertEqual({x.subject for x in i.lineage_for(e,obs(when=AFTER))},{'subject-blue'})

    def test_simultaneous_ownership_conflict_blocks_clean_state(self):
        people=[identity(),identity('subject-blue','blue@example.invalid')]
        rows=[obs(user_id='subject-amber'),obs(user_id='subject-blue',copy='replica',evidence='witness-blue')]
        i=self.index(rows,identities=people); e,_=i.edges_at(T(LATE))
        self.assertFalse(i.lineage_for(e,obs(when=LATE,present=False)))

    def test_late_conflict_does_not_change_earlier_query(self):
        people=[identity(),identity('subject-blue','blue@example.invalid')]
        rows=[obs(user_id='subject-amber'),replace(obs(user_id='subject-blue'),available_at=T(AFTER))]
        i=self.index(rows,identities=people); e,_=i.edges_at(T(LATE))
        self.assertEqual({x.subject for x in i.lineage_for(e,obs(when=LATE))},{'subject-amber'})

    def test_late_evidence_capture_cannot_establish_old_link(self):
        i=self.index([replace(obs(user_id='subject-amber'),available_at=T(AFTER))])
        self.assertFalse(i.edges_at(T(LATE))[0])

    def test_identity_free_404_is_not_subject_absence(self):
        i=self.index([obs(present=False,status_code=404)])
        e,_=i.edges_at(T(LATE))
        check=check_resource(i,e,'subject-amber','account_service','resource-copper',T(LATE),RULES)
        self.assertTrue(check['state_proven']); self.assertTrue(check['scope_proven'])
        self.assertFalse(check['lineage_proven']); self.assertFalse(check['recoverable'])

    def test_historical_link_plus_authoritative_404_can_recover_check(self):
        rows=[obs(when=EARLY,user_id='subject-amber'),obs(present=False,status_code=404)]
        i=self.index(rows); e,_=i.edges_at(T(LATE))
        check=check_resource(i,e,'subject-amber','account_service','resource-copper',T(LATE),RULES)
        self.assertTrue(check['recoverable']); self.assertEqual(check['operation'],'VERIFY_RECORD_ABSENT')

    def test_link_plus_unscoped_missing_claim_cannot_recover_check(self):
        rows=[obs(when=EARLY,user_id='subject-amber'),obs(present=False,source='workflow-reply')]
        i=self.index(rows); e,_=i.edges_at(T(LATE))
        check=check_resource(i,e,'subject-amber','account_service','resource-copper',T(LATE),RULES)
        self.assertTrue(check['lineage_proven']); self.assertFalse(check['scope_proven']); self.assertFalse(check['recoverable'])

    def test_primary_replica_disagreement_cannot_verify_logical_absence(self):
        rows=[obs(when=EARLY,user_id='subject-amber'),obs(present=False),
              obs(copy='replica',user_id='subject-amber',evidence='replica-witness')]
        i=self.index(rows); e,_=i.edges_at(T(LATE))
        check=check_resource(i,e,'subject-amber','account_service','resource-copper',T(LATE),RULES)
        self.assertFalse(check['recoverable']); self.assertEqual(len(check['copies']),2)

    def test_fully_anonymized_row_without_prior_ownership_is_not_a_check(self):
        i=self.index([obs(system='analytics_platform',category='ANALYTICS_PROFILE',source='profiles',
                          customer_reference=None,email=None,phone=None,email_hash=None)])
        e,_=i.edges_at(T(LATE))
        self.assertFalse(check_resource(i,e,'subject-amber','analytics_platform','resource-copper',T(LATE),RULES)['recoverable'])

    def test_prior_analytics_owner_plus_complete_cleared_payload_recovers_check(self):
        rows=[obs(when=EARLY,system='analytics_platform',category='ANALYTICS_PROFILE',source='profiles',user_id='subject-amber'),
              obs(system='analytics_platform',category='ANALYTICS_PROFILE',source='profiles',
                  user_id=None,email=None,phone=None,email_hash=None)]
        i=self.index(rows); e,_=i.edges_at(T(LATE))
        check=check_resource(i,e,'subject-amber','analytics_platform','resource-copper',T(LATE),RULES)
        self.assertTrue(check['recoverable']); self.assertEqual(check['operation'],'VERIFY_RECORD_ANONYMIZED')

    def test_cross_system_lookup_key_has_explicit_parent_provenance(self):
        rows=[obs(when=EARLY,user_id='subject-amber'),
              obs(system='analytics_platform',category='ANALYTICS_PROFILE',resource='resource-teal',
                  _lookup_values=('resource-copper',))]
        i=self.index(rows); e,_=i.edges_at(T(LATE))
        child=[x for x in e if x.resource=='resource-teal']
        self.assertEqual(len(child),1); self.assertEqual(child[0].basis,'explicit resource lookup key')

    def test_same_resource_token_in_two_systems_is_not_unique_lookup(self):
        rows=[obs(when=EARLY,user_id='subject-amber'),
              obs(when=MIDDLE,system='support_platform',user_id='subject-amber'),
              obs(when=LATE,system='analytics_platform',resource='resource-teal',_lookup_values=('resource-copper',))]
        i=self.index(rows); e,_=i.edges_at(T(AFTER))
        self.assertFalse([x for x in e if x.resource=='resource-teal'])

    def test_resource_number_row_order_and_cohort_never_link(self):
        rows=[obs(user_id='subject-amber'),obs(resource='resource-copper-next',audience_cohort='general_shopper')]
        i=self.index(list(reversed(rows))); e,_=i.edges_at(T(LATE))
        self.assertEqual({x.resource for x in e},{'resource-copper'})

    def test_newer_workflow_claim_requires_new_readback(self):
        a={**catalog(when=LATE),'event_type':'RESTORE_RECORD'}
        rows=[obs(when=EARLY,user_id='subject-amber'),obs(present=False)]
        i=self.index(rows,activity=[a]); e,_=i.edges_at(T(AFTER))
        self.assertFalse(check_resource(i,e,'subject-amber','account_service','resource-copper',T(AFTER),RULES)['recoverable'])

    def test_edge_availability_includes_later_historical_alias_witness(self):
        history=[dict(audit_id='rotation-witness',user_id='subject-amber',field_name='email',
                      event_time=LATE,old_value='old@example.invalid',new_value='amber@example.invalid')]
        i=self.index([obs(email='old@example.invalid')],history)
        self.assertFalse(i.edges_at(T(MIDDLE))[0])
        edge=i.edges_at(T(AFTER))[0][0]
        self.assertEqual(edge.valid_from,T(MIDDLE)); self.assertEqual(edge.available_at,T(LATE))

    def test_stable_connector_selector_is_explicit_lineage(self):
        rules=[] # DATA_FLOW treatment is defined directly by the contract.
        row=obs(system='integration_service',category='DATA_FLOW',source='connector_subscriptions',
                subject_selector='subject-amber',enabled=False)
        i=self.index([row]); edges,_=i.edges_at(T(LATE))
        check=check_resource(i,edges,'subject-amber','integration_service','resource-copper',T(LATE),rules)
        self.assertTrue(check['recoverable']); self.assertEqual(check['operation'],'VERIFY_DATA_FLOW_DISABLED')

    def test_partial_analytics_fields_cannot_prove_anonymization(self):
        rows=[obs(when=EARLY,system='analytics_platform',category='ANALYTICS_PROFILE',source='profiles',user_id='subject-amber'),
              obs(system='analytics_platform',category='ANALYTICS_PROFILE',source='profiles',user_id=None,email=None)]
        i=self.index(rows); edges,_=i.edges_at(T(LATE))
        self.assertFalse(check_resource(i,edges,'subject-amber','analytics_platform','resource-copper',T(LATE),RULES)['recoverable'])

    def test_candidate_adds_only_cited_selector_check_without_any_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            request=Request('fixture-request','amber@example.invalid',T(EARLY),'COMPLETE',T(EARLY),T(LATE),'Delete my account')
            row=obs(system='integration_service',category='DATA_FLOW',source='connector_subscriptions',
                    subject_selector='subject-amber',enabled=False)
            inputs=Inputs((request,),[identity()],[],[],[],
                          (EvidenceFile('witness-green',directory/'unused.sql','fixture',T(MIDDLE)),))
            write_predictions(directory/'baseline-fixture.csv',[Result('fixture-request','COMPLETE',())],
                              inputs.requests,inputs.citation_times())
            (directory/'baseline-fixture.json').write_text(json.dumps(dict(summary={},cases={'fixture-request':{}})))
            index=self.index([row])
            report=investigate_split(directory,'fixture',inputs,index)
            candidate=read_output(directory/'candidate-fixture.csv')[0]
            self.assertEqual(candidate.deletion_status,'COMPLETE')
            self.assertEqual(len(candidate.steps),1)
            step=candidate.steps[0]
            self.assertEqual((step.system_id,step.resource_id,step.operation,step.evidence_id),
                             ('integration_service','resource-copper','VERIFY_DATA_FLOW_DISABLED','witness-green'))
            self.assertEqual(report['changed_rows'],['fixture-request'])
            self.assertEqual(report['new_audit_validator_failures'],{})


if __name__ == '__main__':
    unittest.main()
