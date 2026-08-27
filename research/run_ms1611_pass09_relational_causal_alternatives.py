from __future__ import annotations
import json,hashlib
from collections import defaultdict
from pathlib import Path

# Strip-for-parts reuse of the deferred MS1570-1572 research survivor only:
# recurrent opaque conjunctions become proposal handles. No semantic causal label is installed.

def unitize(rows,min_unique_support=4):
    groups=defaultdict(set)
    for r in rows:
        key=(r['intervention_token'],r['target_change_token'],r['control_change_token'])
        groups[key].add(r['evidence_id'])
    out=[]
    for key,eids in sorted(groups.items()):
        if len(eids)>=min_unique_support:
            digest=hashlib.sha256(repr(key).encode()).hexdigest()
            out.append({'proposal_id':'REL-'+digest[:16],'relation':list(key),'unique_evidence_ids':sorted(eids),'support':len(eids),'truth_authority':'NONE','execution_authority':'NONE'})
    return out

def main():
    rows=[]
    for i in range(8):
        rows.append({'intervention_token':'P','target_change_token':'CHANGED','control_change_token':'STABLE','evidence_id':f'C{i}'})
    for i in range(7):
        rows.append({'intervention_token':'P','target_change_token':'CHANGED','control_change_token':'CHANGED','evidence_id':f'X{i}'})
    # duplicate copies cannot inflate support
    rows += [dict(rows[0]) for _ in range(20)]
    props=unitize(rows)
    out={'pass':'MS1611_PASS09','proposals':props,'count':len(props),'result':'DEFERRED_RELATIONAL_UNITIZATION_CAN_FORM_OPAQUE_CAUSAL_VS_EXOGENOUS_PATTERN_HANDLES_FROM_UNIQUE_EVIDENCE_WITH_ZERO_AUTHORITY','boundary':'RELATION_TOKENS_AND_NEGATIVE_CONTROL_COVERAGE_ARE_STILL_OPERATIONAL_FIXTURE_STRUCTURE','authority':'RESEARCH_ONLY'}
    Path('research/MS1611_PASS09_RELATIONAL_CAUSAL_ALTERNATIVES.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
