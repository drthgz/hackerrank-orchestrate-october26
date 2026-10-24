import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
from client import Client


class BudgetTests(unittest.TestCase):
    def test_budget_blocks_network_before_spend(self):
        with tempfile.TemporaryDirectory() as directory:
            client=Client(directory)
            client.ledger.write_text(json.dumps([{'reserved_usd':.999,'status':'uncertain_failure'}]))
            with patch('urllib.request.urlopen') as network:
                with self.assertRaisesRegex(RuntimeError,'budget'):
                    client.call('x',[],{})
                network.assert_not_called()

    def test_failure_reservation_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ,{'OPENAI_API_KEY':'fictional-test-key'}):
                with patch('urllib.request.urlopen',side_effect=TimeoutError):
                    with self.assertRaisesRegex(RuntimeError,'reservation retained'):
                        Client(directory).call('x',[],{})
            ledger=json.loads((Path(directory)/'usage.json').read_text())
            self.assertEqual(ledger[0]['status'],'uncertain_failure')
            self.assertGreater(ledger[0]['reserved_usd'],0)
            self.assertNotIn('fictional-test-key',(Path(directory)/'usage.json').read_text())
            self.assertFalse((Path(directory)/'budget.lock').exists())

    def test_cache_avoids_paid_request(self):
        with tempfile.TemporaryDirectory() as directory:
            expected={'usage':{'prompt_tokens':1}}
            (Path(directory)/'x.json').write_text(json.dumps(expected))
            with patch('urllib.request.urlopen') as network:
                self.assertEqual(Client(directory).call('x',[],{}),expected)
                network.assert_not_called()




class ValidationTests(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        from datetime import datetime,timezone,timedelta
        self.cutoff=datetime(2026,1,2,tzinfo=timezone.utc)
        self.request=SimpleNamespace(case_id='custom',audit_at=self.cutoff,request_text='Delete my account')
        self.inputs=SimpleNamespace(citation_times=lambda:{'proof':self.cutoff,'future':self.cutoff+timedelta(days=1)},
                                    rules=[],activity=[])
        self.bundle={'artifacts':[{'file_id':'proof','content':'account_service resource_custom'}],'activity':[]}
        self.proposal={'deletion_status':'INCOMPLETE','steps':[
            {'step_no':i,'phase':phase,'system_id':'account_service','resource_id':'resource_custom',
             'operation':op,'state':state,'evidence_id':'proof' if i==1 else ''}
            for i,(phase,op,state) in enumerate([
                ('FINDING','REPORT_REMAINING_RECORD','PRESENT'),
                ('REMEDIATION','DELETE_RECORD','ABSENT'),
                ('VERIFICATION','VERIFY_RECORD_ABSENT','ABSENT')],1)]}

    def test_invented_resource_rejected(self):
        from run import basic_validate,AuditError
        for s in self.proposal['steps']:s['resource_id']='fabricated'
        with self.assertRaisesRegex(AuditError,'Unsupported resource'):
            basic_validate(self.proposal,self.request,self.inputs,self.bundle)

    def test_future_citation_rejected(self):
        from run import basic_validate,AuditError
        self.proposal['steps'][0]['evidence_id']='future'
        with self.assertRaisesRegex(AuditError,'future evidence'):
            basic_validate(self.proposal,self.request,self.inputs,self.bundle)

    def test_wrong_state_rejected(self):
        from run import basic_validate,AuditError
        self.proposal['steps'][0]['state']='ABSENT'
        with self.assertRaisesRegex(AuditError,'Invalid phase'):
            basic_validate(self.proposal,self.request,self.inputs,self.bundle)

    def test_citation_existence_does_not_establish_resource(self):
        from run import basic_validate,AuditError
        self.bundle['artifacts'][0]['content']='different_resource'
        with self.assertRaisesRegex(AuditError,'Unsupported resource'):
            basic_validate(self.proposal,self.request,self.inputs,self.bundle)

    def test_semantic_gate_rejects_unproved_policy(self):
        from run import basic_validate,hybrid_validate,AuditError
        result=basic_validate(self.proposal,self.request,self.inputs,self.bundle)
        with self.assertRaisesRegex(AuditError,'Policy/provenance'):
            hybrid_validate(result,self.request,self.inputs,())


if __name__=='__main__': unittest.main()
