from __future__ import annotations
import json
from pathlib import Path

def declared_roots(obs): return set(obs.get('lineage',())) or ({'SOURCE:'+obs['origin']} if obs.get('origin') else set())
def independent(a,b):
    ra,rb=declared_roots(a),declared_roots(b)
    return bool(ra and rb and ra.isdisjoint(rb))

def main():
    cases={
      'same_source_different_event':({'origin':'A','lineage':['ROOT-A']},{'origin':'A','lineage':['ROOT-A']}),
      'different_source_shared_root':({'origin':'A','lineage':['ROOT-X']},{'origin':'B','lineage':['ROOT-X']}),
      'overlapping_multi_root':({'origin':'A','lineage':['ROOT-X','ROOT-A']},{'origin':'B','lineage':['ROOT-X','ROOT-B']}),
      'declared_disjoint':({'origin':'A','lineage':['ROOT-A']},{'origin':'B','lineage':['ROOT-B']}),
      # Evaluator knows these share HIDDEN-COMMON, but interface declarations lie.
      'spoofed_disjoint_hidden_common':({'origin':'A','lineage':['CLAIM-A']},{'origin':'B','lineage':['CLAIM-B']}),
    }
    results={k:independent(*v) for k,v in cases.items()}
    out={'pass':'MS1589_PASS12','declared_independence_results':results,'hidden_common_case_true_independence':False,'result':'EXISTING_ORIGIN_LINEAGE_FIELDS_CAN_BLOCK_DECLARED_OVERLAP__BUT_CANNOT_SELF_AUTHENTICATE_ROOT_TRUTH','authority':'RESEARCH_ONLY'}
    Path('research/MS1589_PASS12_DECLARED_LINEAGE_INDEPENDENCE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
