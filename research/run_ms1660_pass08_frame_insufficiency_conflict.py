from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,direct_lookup
OUT=Path(__file__).with_name('MS1660_PASS08_FRAME_INSUFFICIENCY_CONFLICT.json')

def main():
 rows=[]
 def add(tag,s,a,e):rows.append(Transition(digest((tag,s,a,e)),digest(('o',tag,s,a,e)),s,a,e))
 # Same visible start/action has incompatible effects across episodes because a hidden/suppressed context differs.
 for i in range(6):
  add(f'a{i}','S0','A','S1'); add(f'c{i}','S0','C','S2' if i%2==0 else 'S3')
 # add a second stable start so positive recurrence elsewhere cannot excuse the conflict
 for i in range(6):
  add(f'a2-{i}','S4','A','S5'); add(f'aa2-{i}','S5','A','S6'); add(f'c2-{i}','S4','C','S6')
 comps=construct_global_compositions(rows,2); lookup=direct_lookup(rows)
 target=[r for r in comps if r.direct_action=='C' and r.first_action=='A' and r.second_action=='A']
 checks={
  'conflicting_visible_key_not_collapsed_to_direct_lookup':('S0','C') not in lookup,
  'no_global_AA_equals_C_relation_from_partial_positive_support':len(target)==0,
 }
 out={'milestone':'MS1660','pass':8,'checks':checks,'pass_all':all(checks.values()),'disposition':'FRAME_INSUFFICIENT_OR_STOCHASTIC__NO_DETERMINISTIC_ALGEBRA_NOMINATED','scar':'SAME_VISIBLE_START_ACTION_CONFLICT_NE_LICENSE_TO_AVERAGE_A_FRAME'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
