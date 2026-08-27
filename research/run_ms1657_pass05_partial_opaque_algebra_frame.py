from __future__ import annotations
import json,sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,construct_identity,construct_inverses,predict_via_composition,direct_lookup
OUT=Path(__file__).with_name('MS1657_PASS05_PARTIAL_OPAQUE_ALGEBRA_FRAME.json')

def fixture(seed=1657):
 rng=random.Random(seed);states=[f'E{i}' for i in range(8)];rng.shuffle(states); actions=['I','A','B','C']; rng.shuffle(actions);I,A,B,C=actions
 shift={I:0,A:1,B:-1,C:2}; rows=[]
 def add(s,a,e,tag):rows.append(Transition(digest((tag,s,a,e)),digest(('origin',tag,s,a,e)),s,a,e))
 for i,s in enumerate(states):
  for a in (I,A,B):add(s,a,states[(i+shift[a])%8],'component')
 # Direct C only on 4 states; relation A∘A=C can generalize to remaining 4.
 for s in states[:4]:
  i=states.index(s);add(s,C,states[(i+2)%8],'direct')
 return states,(I,A,B,C),rows

def main():
 states,(I,A,B,C),rows=fixture();comps=construct_global_compositions(rows,3);ids=construct_identity(rows,3);invs=construct_inverses(rows,3)
 lookup=direct_lookup(rows); hold=[s for s in states if (s,C) not in lookup];pred=[]
 for s in hold:
  truth=states[(states.index(s)+2)%8];p,status,_=predict_via_composition(s,C,comps,rows);pred.append((s,p,status,truth,p==truth))
 expressions={(r.direct_action,r.first_action,r.second_action) for r in comps}
 inverse_pairs={(r.first_action,r.second_action) for r in invs}; identities={r.action for r in ids}
 checks={
  'identity_relation_discovered':I in identities,
  'inverse_pair_discovered':(A,B) in inverse_pairs and (B,A) in inverse_pairs,
  'composition_relation_discovered':(C,A,A) in expressions,
  'heldout_composed_action_predicted':all(x[-1] for x in pred),
  'no_truth_execution_authority':all(r.truth_authority=='NONE' and r.execution_authority=='NONE' for r in comps),
 }
 result={'milestone':'MS1657','pass':5,'opaque_action_handles':{'identity':I,'forward':A,'inverse':B,'composed':C},'identity_relations':[r.__dict__ for r in ids],'inverse_relations':[r.__dict__ for r in invs],'composition_relations':[r.__dict__ for r in comps],'holdout_predictions':pred,'checks':checks,'pass_all':all(checks.values()),
 'disposition':'SURVIVED_PARTIAL_OPAQUE_RELATIONAL_ALGEBRA','nonclaim':'Observed identity/inverse/composition topology does not imply a group, global closure, external coordinate meaning, or unobserved executable actions.'}
 OUT.write_text(json.dumps(result,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'n_compositions':len(comps),'n_inverses':len(invs),'n_identities':len(ids),'holdout':pred},indent=2))
if __name__=='__main__':main()
