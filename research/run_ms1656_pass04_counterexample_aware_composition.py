from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions
OUT=Path(__file__).with_name('MS1656_PASS04_COUNTEREXAMPLE_AWARE_COMPOSITION.json')
def rows(partial=False):
 s=[f'Q{i}' for i in range(6)];r=[]
 def add(x,a,y):r.append(Transition(digest((x,a,y)),digest(('o',x,a,y)),x,a,y))
 for i,x in enumerate(s):
  add(x,'A',s[(i+1)%6]);add(x,'B',s[(i+1)%6]);add(x,'C',s[(i+2 if (not partial or i<3) else i+3)%6])
 return r

def main():
 clean=construct_global_compositions(rows(False),2);partial=construct_global_compositions(rows(True),2)
 key=lambda x:(x.direct_action,x.first_action,x.second_action)
 target=('C','A','B')
 result={'milestone':'MS1656','pass':4,'clean_has_target':target in {key(x) for x in clean},'partial_has_target':target in {key(x) for x in partial},
 'checks':{'clean_global_relation_survives':target in {key(x) for x in clean},'observed_counterexample_blocks_global_relation':target not in {key(x) for x in partial},'zero_authority':all(x.truth_authority=='NONE' and x.execution_authority=='NONE' for x in clean+partial)},
 'scar':'OBSERVED_COUNTEREXAMPLE_BLOCKS_GLOBAL_ALGEBRA__LOCAL_SCOPE_REMAINS_UNRESOLVED'}
 result['pass_all']=all(result['checks'].values());OUT.write_text(json.dumps(result,indent=2,sort_keys=True));print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
