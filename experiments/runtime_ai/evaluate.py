"""Label-reading evaluator only; never imported by runtime inference."""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'code'))
from audit.models import Result,Step
from evaluation.main import compare


def content(s):
    return json.dumps({k:v for k,v in s.items() if k!='step_no'},sort_keys=True)


def evaluate():
    predictions=json.loads((HERE/'predictions.json').read_text())
    with (ROOT/'dataset/sample_output.csv').open() as f:
        labels={r['case_id']:r for r in csv.DictReader(f)}
    report={'arms':{},'cases':{},'notes':'Raw arms are diagnostics, not accepted outputs'}
    for arm in ('A','B','C','B_raw','C_raw'):
        counts=Counter();details={}
        for cid,arms in predictions.items():
            expected=json.loads(labels[cid]['steps_json'])
            if arm=='A': p=arms['A'] if 'error' not in arms['A'] else None
            elif arm.endswith('_raw'): p=arms[arm[0]].get('proposal')
            else:p=arms[arm].get('accepted')
            if p and p.get('deletion_status')=='UNRESOLVED':p=None
            steps=p['steps'] if p else []
            result=Result(cid,p['deletion_status'],tuple(Step(**s) for s in steps)) if p else None
            c=compare(result,{'status':labels[cid]['deletion_status'],'steps':expected}) if result else {}
            counts['field_matches']+=c.get('field_matches',0)
            counts['field_comparisons']+=max(len(steps),len(expected))*7
            counts['status_correct']+=bool(c.get('deletion_status_matches'))
            counts['exact_cases']+=bool(c.get('deletion_status_matches') and c.get('step_ordering_matches'))
            counts['sequence_correct']+=bool(c.get('step_ordering_matches'))
            counts['step_matches']+=c.get('step_matches',0)
            counts['predicted_steps']+=len(steps)
            counts['expected_steps']+=len(expected)
            counts['accepted_cases']+=p is not None
            counts['emitted_citations']+=sum(bool(s['evidence_id']) for s in steps)
            expected_content={content(s) for s in expected}
            counts['correct_cited_steps']+=sum(bool(s['evidence_id']) and content(s) in expected_content for s in steps)
            verifications={content(s) for s in steps if s['phase']=='VERIFICATION'}
            counts['missing_verification']+=sum(s['phase']=='VERIFICATION' and content(s) not in verifications for s in expected)
            base=arms['A'].get('steps',[])
            base_content={content(s) for s in base}
            added=[s for s in steps if content(s) in expected_content and content(s) not in base_content]
            lost=[s for s in base if content(s) in expected_content and content(s) not in {content(a) for a in steps}]
            counts['new_matching_steps']+=len(added)
            counts['lost_matching_steps']+=len(lost)
            details[cid]={'status_correct':bool(c.get('deletion_status_matches')),
                          'exact':bool(c.get('deletion_status_matches') and c.get('step_ordering_matches')),
                          'matches':c.get('step_matches',0),'steps':len(steps),'new_matching_steps':added,'lost_matching_steps':lost}
        report['arms'][arm]=dict(counts)
        report['cases'][arm]=details
    ledger=json.loads((HERE/'calls/usage.json').read_text())
    report['usage']={'attempts':len(ledger),'successful_calls':sum(x['status']=='completed' for x in ledger),
                     'input_tokens':sum(x.get('usage',{}).get('prompt_tokens',0) for x in ledger),
                     'cached_tokens':sum(x.get('usage',{}).get('prompt_tokens_details',{}).get('cached_tokens',0) for x in ledger),
                     'output_tokens':sum(x.get('usage',{}).get('completion_tokens',0) for x in ledger),
                     'estimated_cost_usd':sum(x.get('estimated_cost_usd',0) for x in ledger),
                     'conservative_reserved_usd':sum(x['reserved_usd'] for x in ledger),
                     'latency_seconds':sum(x.get('latency_seconds',0) for x in ledger)}
    report['validation_failures']={cid:{arm:v['validation_failure'] for arm,v in arms.items() if arm!='A' and 'validation_failure' in v} for cid,arms in predictions.items()}
    report['fallback_cases']=[cid for cid,arms in predictions.items() if arms['C'].get('fallback')]
    (HERE/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'cases','validation_failures'}},indent=2))
    return report

if __name__=='__main__':evaluate()
