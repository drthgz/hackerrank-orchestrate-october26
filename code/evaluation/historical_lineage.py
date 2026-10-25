"""Reproduce the isolated historical-lineage experiment, without model calls.

Baseline CSVs/sidecars are generated first with code/main.py. Public reference
labels enter only after independent candidate files have been written. No root
submission artifact is a write target.
"""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, replace
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit.contract import read_output, validate_result, order_steps
from audit.identity import resolve_subject
from audit.inputs import load_inputs
from audit.models import AuditError, Step
from audit.prediction import write_predictions
from evaluation.accuracy_changes import content, integrity, load, metrics
from evaluation.lineage import LineageIndex, collect, check_resource, serial


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=serial)+'\n')


def validators(results, inputs):
    requests = {r.case_id:r for r in inputs.requests}
    failures = {}
    for r in results:
        try:
            validate_result(r, requests[r.case_id], inputs.citation_times())
        except AuditError as exc:
            failures[r.case_id] = str(exc)
    return failures


def investigate_split(directory, split, inputs, index):
    baseline = directory/f'baseline-{split}.csv'
    sidecar = directory/f'baseline-{split}.json'
    details = json.loads(sidecar.read_text())['cases']
    predictions = load(baseline)
    additional, new_targets, case_ledgers = [], [], {}
    for request in inputs.requests:
        if predictions[request.case_id]['status'] == 'NOT_APPLICABLE':
            continue
        subject = resolve_subject(request.email, request.audit_at, inputs.identities, inputs.history)
        edges, rejected = index.edges_at(request.audit_at)
        own = [e for e in edges if e.subject == subject.user_id]
        old = {(o['system_id'],o['resource_id']) for o in details[request.case_id].get('observations',[])}
        new = [e for e in own if (e.system,e.resource) not in old]
        grouped = defaultdict(list)
        for edge in new:
            grouped[edge.system,edge.resource].append(edge)
        for (system,resource), es in grouped.items():
            check = check_resource(index,edges,subject.user_id,system,resource,request.audit_at,inputs.rules)
            already_discovered = any(x.get('resource_id') == resource
                for x in details[request.case_id].get('omissions',[]))
            additional.append(dict(case_id=request.case_id, subject=subject.user_id,
                system=system, resource=resource, edges=[asdict(e) for e in es], check=check,
                already_in_baseline_activity_omissions=already_discovered))
        # Inventory every admissible target record previously missing in the
        # baseline. Does not need, load, or consult sample_output.csv.
        unlinked = []
        for o in index.observations:
            if (o.category not in {'USER_PROFILE','ANALYTICS_PROFILE'} or o.observed_at > request.audit_at
                    or o.available_at > request.audit_at or (o.system_id,o.resource_id) in old):
                continue
            owners = index.lineage_for(edges,o)
            if any(e.subject == subject.user_id for e in owners):
                key = (request.case_id,o.system_id,o.resource_id)
                if key not in {(x['case_id'],x['system'],x['resource']) for x in new_targets}:
                    new_targets.append(dict(case_id=request.case_id,system=o.system_id,resource=o.resource_id,
                        check=check_resource(index,edges,subject.user_id,o.system_id,o.resource_id,request.audit_at,inputs.rules)))
            elif not owners:
                unlinked.append((o.system_id,o.resource_id,o.evidence_id))
        case_ledgers[request.case_id] = dict(subject=subject.user_id,audit_at=request.audit_at,
            lineage_edges=[asdict(e) for e in own], globally_unlinked_target_observations=sorted(set(unlinked)),
            rejected_observations=rejected)
    target_recoverable = [x for x in new_targets if x['check']['recoverable']]
    # This is a bounded investigation, not an automatic policy change. If an
    # admissible new target appears, require its explicit proof review first.
    if new_targets:
        write_json(directory/f'review-required-{split}.json',new_targets)
        raise AuditError('New target lineage requires proof review before candidate emission')
    # Reviewed, explicit stable subject selectors in disabled SQL connector
    # configurations establish a separate, non-target adapter omission. No
    # historical transfer or guessed resource ID is needed for these checks.
    recoverable = [x for x in additional if x['check']['recoverable']
                   and x['check']['operation'] == 'VERIFY_DATA_FLOW_DISABLED']
    new_citation_checks = []
    requests_by_id = {r.case_id:r for r in inputs.requests}
    for x in recoverable:
        check=x['check']; request=requests_by_id[x['case_id']]
        proof_rows = [o for o in index.observations
                      if (o.system_id,o.resource_id,o.evidence_id)==(x['system'],x['resource'],check['evidence_id'])
                      and any(c['copy_id']==o.copy_id and c['observed_at']==o.observed_at for c in check['copies'])]
        valid = (bool(proof_rows) and len(proof_rows)==len(check['copies'])
                 and all(o.category=='DATA_FLOW' and o.facts.get('subject_selector')==x['subject']
                         and o.facts.get('enabled') is False and o.observed_at<=request.audit_at
                         and o.available_at<=request.audit_at for o in proof_rows))
        assert valid, 'New connector verification lacks direct, admissible citation proof'
        new_citation_checks.append(dict(case_id=x['case_id'],system=x['system'],resource=x['resource'],
            evidence_id=check['evidence_id'],physical_copies=len(proof_rows),correct=True))
    baseline_results = read_output(baseline)
    results = []
    changed = []
    for result in baseline_results:
        additions = [x for x in recoverable if x['case_id'] == result.case_id]
        if additions:
            steps = list(result.steps)
            for x in additions:
                check = x['check']
                steps.append(Step(0,'VERIFICATION',x['system'],x['resource'],check['operation'],
                                  check['final_state'],check['evidence_id'] if result.deletion_status=='COMPLETE' else ''))
                detail = details[result.case_id]
                for o in index.observations:
                    if (o.system_id,o.resource_id) != (x['system'],x['resource']):
                        continue
                    if not any(c['evidence_id']==o.evidence_id and c['copy_id']==o.copy_id
                               and c['observed_at']==o.observed_at for c in check['copies']):
                        continue
                    row = asdict(replace(o,subject_id=x['subject']))
                    detail.setdefault('observations',[]).append(row)
                    detail.setdefault('latest_copy_states',[]).append(row)
                detail.setdefault('lineage_experiment_added_checks',[]).append(x)
            result = replace(result,steps=order_steps(steps))
            changed.append(result.case_id)
        results.append(result)
    candidate = directory/f'candidate-{split}.csv'
    write_predictions(candidate,results,inputs.requests,inputs.citation_times())
    candidate_sidecar = directory/f'candidate-{split}.json'
    saved = json.loads(sidecar.read_text())
    saved['cases'] = details
    saved['summary']['output_sha256'] = digest(candidate)
    saved['summary']['lineage_experiment_changed_cases'] = changed
    write_json(candidate_sidecar,saved)
    failures = validators(read_output(candidate),inputs)
    before_failures = validators(baseline_results,inputs)
    baseline_rows, candidate_rows = load(baseline), load(candidate)
    report = dict(requests=len(inputs.requests), newly_indexed_resource_links=additional,
        newly_indexed_resource_link_count=len(additional), newly_linked_target_resources=new_targets,
        additional_link_witness_count=sum(len(x['edges']) for x in additional),
        links_absent_from_observation_and_omission_ledgers=sum(not x['already_in_baseline_activity_omissions'] for x in additional),
        new_direct_record_link_count=sum(any(e['basis']!='explicit catalog link' for e in x['edges']) for x in additional),
        catalog_links_absent_from_observation_ledger=sum(all(e['basis']=='explicit catalog link' for e in x['edges']) for x in additional),
        newly_recoverable_verification_steps=recoverable, newly_recoverable_target_steps=target_recoverable,
        new_citation_checks=new_citation_checks,
        changed_rows=changed,
        row_changes={cid:dict(before_status=baseline_rows[cid]['status'],
            after_status=candidate_rows[cid]['status'],
            added_steps=[json.loads(s) for s in (content(candidate_rows[cid]['steps'])-content(baseline_rows[cid]['steps'])).elements()],
            removed_steps=[json.loads(s) for s in (content(baseline_rows[cid]['steps'])-content(candidate_rows[cid]['steps'])).elements()])
            for cid in changed},
        strong_audit_validator_failures=failures,
        new_audit_validator_failures={k:v for k,v in failures.items() if before_failures.get(k)!=v},
        integrity=integrity(candidate,candidate_sidecar,inputs),
        baseline_sha256=digest(baseline), candidate_sha256=digest(candidate))
    write_json(directory/f'lineage-{split}.json',dict(report=report,cases=case_ledgers))
    return report


def evaluate_gaps(directory, inputs, index, labels):
    """Public labels identify omission targets only after candidate generation."""
    predictions = load(directory/'candidate-public.csv')
    texts = {}
    for f in inputs.evidence:
        if f.path.suffix in {'.sql','.json','.log','.txt'}:
            texts[f.file_id] = f.path.read_text()
        elif f.path.suffix == '.pdf':
            from audit.pdf_evidence import read_pdf
            texts[f.file_id] = '\n'.join(read_pdf(f).pages)
        else:
            from audit.reviewed_images import review
            texts[f.file_id] = json.dumps(review(f) or {})
    omissions = []
    for request in inputs.requests:
        missing = content(labels[request.case_id]['steps'])-content(predictions[request.case_id]['steps'])
        subject = resolve_subject(request.email,request.audit_at,inputs.identities,inputs.history)
        edges,_ = index.edges_at(request.audit_at)
        for encoded,count in missing.items():
            step = json.loads(encoded)
            if (step['system_id'],step['operation']) not in {
                ('account_service','VERIFY_RECORD_ABSENT'),('analytics_platform','VERIFY_RECORD_ANONYMIZED')}:
                continue
            check = check_resource(index,edges,subject.user_id,step['system_id'],step['resource_id'],request.audit_at,inputs.rules)
            pattern = re.compile(r'(?<!\w)'+re.escape(step['resource_id'])+r'(?!\w)')
            hits = [dict(evidence_id=f.file_id,captured_at=f.captured_at,
                         available_by_audit=f.captured_at <= request.audit_at)
                    for f in inputs.evidence if pattern.search(texts[f.file_id])]
            omissions.append(dict(case_id=request.case_id,count=count,missing_step=step,proof=check,
                                  raw_token_locations_not_ownership_proof=hits))
    return omissions


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]; dataset=root/'dataset'
    p=args.directory.resolve(); p.mkdir(parents=True,exist_ok=True)
    if p == root:
        parser.error('Use a separate experiment directory')
    preserved={name:digest(root/name) for name in ('output.csv','code.zip')}
    public=load_inputs(dataset,dataset/'sample_deletion_requests.csv')
    full=load_inputs(dataset,dataset/'deletion_requests.csv')
    observations,coverage=collect(public.evidence)
    index=LineageIndex(public.identities,public.history,observations,public.activity)
    final_cutoff=max(r.audit_at for r in (*public.requests,*full.requests))
    edges,rejected=index.edges_at(final_cutoff)
    write_json(p/'index.json',dict(cutoff=final_cutoff,aliases=[asdict(a) for a in index.aliases],
        edges=[asdict(e) for e in edges],rejected=rejected,coverage=coverage))
    report=dict(base_commit='054aca8',prediction_baseline='91a8faf',observations=len(observations),
        edge_witnesses_at_max_cutoff=len(edges),edges_by_basis=dict(Counter(e.basis for e in edges)),
        coverage_files=len(coverage), max_cutoff=final_cutoff,
        public=investigate_split(p,'public',public,index),full=investigate_split(p,'full',full,index))
    # Labels are opened only after both isolated candidate files exist.
    labels=load(dataset/'sample_output.csv')
    for split in ['public']:
        report[split]['metrics']=metrics(load(p/f'candidate-{split}.csv'),labels)
        report[split]['baseline_metrics']=metrics(load(p/f'baseline-{split}.csv'),labels)
        report[split]['exact_case_ids']=[cid for cid,row in load(p/f'candidate-{split}.csv').items() if row==labels[cid]]
    report['public_target_omissions']=evaluate_gaps(p,public,index,labels)
    report['preserved_artifacts']={name:dict(sha256=before,unchanged=digest(root/name)==before)
                                   for name,before in preserved.items()}
    assert all(x['unchanged'] for x in report['preserved_artifacts'].values())
    report['runtime_usage']=dict(model_calls=0,model_providers=[],model_names=[],input_tokens=0,
        output_tokens=0,total_tokens=0,average_tokens_per_request=0,total_cost_usd=0,per_request_cost_usd=0,
        excludes_coding_assistant_usage=True)
    write_json(p/'report.json',report)
    print(json.dumps(dict(observations=len(observations),edge_witnesses=len(edges),
        new_links={s:report[s]['newly_indexed_resource_link_count'] for s in ('public','full')},
        recovered_steps={s:len(report[s]['newly_recoverable_verification_steps']) for s in ('public','full')},
        changed_rows={s:len(report[s]['changed_rows']) for s in ('public','full')},
        target_omissions=len(report['public_target_omissions'])),indent=2))


if __name__ == '__main__':
    main()
