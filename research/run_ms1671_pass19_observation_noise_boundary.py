from __future__ import annotations
import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions
OUT=Path(__file__).with_name('MS1671_PASS19_OBSERVATION_NOISE_BOUNDARY.json')
def run(seed,n=8,noise=.08):
 rng=random.Random(seed);states=[f'S{i}' for i in range(n)];rows=[]
 def truth(s,a):
  i=states.index(s);return states[(i+{'A':1,'B':2,'C':3}[a])%n]
 t=0
 for s in states:
  for a in ('A','B','C'):
   e=truth(s,a)
   if rng.random()<noise:e=rng.choice([x for x in states if x!=e])
   rows.append(Transition(digest((seed,t,s,a,e)),digest((seed,'o',t)),s,a,e));t+=1
 rel=construct_global_compositions(rows,3);target=any((r.direct_action,r.first_action,r.second_action)==('C','A','B') for r in rel)
 return target
def main():
 clean=[run(167100+i,noise=0.0) for i in range(64)];noisy=[run(167200+i,noise=.08) for i in range(64)]
 # This pass is a boundary probe, not a goal to maximize noisy nominations.
 checks={'clean_relation_available_all':all(clean),'noise_materially_reduces_exact_relation_availability':sum(noisy)<sum(clean)}
 out={'milestone':'MS1671','pass':19,'clean_nominations':sum(clean),'noisy_nominations':sum(noisy),'checks':checks,'pass_all':all(checks.values()),'disposition':'EXACT_RELATIONAL_ALGEBRA_DEPENDS_ON_ASSURED_OBSERVATION_OR_SEPARATE_STOCHASTIC_TREATMENT','scar':'OBSERVATION_NOISE_NE_LICENSE_TO_RELAX_STRUCTURAL_EQUALITY_BY_THRESHOLD_SWEEP'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
