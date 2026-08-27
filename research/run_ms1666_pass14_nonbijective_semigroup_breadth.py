from __future__ import annotations
import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,predict_via_composition,direct_lookup
OUT=Path(__file__).with_name('MS1666_PASS14_NONBIJECTIVE_SEMIGROUP_BREADTH.json')
def compose(p,q):return {x:q[p[x]] for x in p}
def run(seed,n=9):
 rng=random.Random(seed);states=[f'S{seed}-{i}' for i in range(n)]; A={s:rng.choice(states) for s in states}; B={s:rng.choice(states) for s in states}; C=compose(A,B); rows=[]
 def add(s,a,e,t):rows.append(Transition(digest((seed,t,s,a,e)),digest((seed,'o',t,s,a,e)),s,a,e))
 for s in states:add(s,'A',A[s],'component');add(s,'B',B[s],'component')
 train=rng.sample(states,n-2)
 for s in train:add(s,'C',C[s],'direct')
 rels=construct_global_compositions(rows,4);lookup=direct_lookup(rows);hold=[s for s in states if s not in train];correct=unknown=0
 for s in hold:
  p,status,_=predict_via_composition(s,'C',rels,rows);correct+=p==C[s];unknown+=status.startswith('UNKNOWN')
 return {'correct':correct,'unknown':unknown,'hold':len(hold),'baseline':sum(lookup.get((s,'C'))==C[s] for s in hold)}
def main():
 xs=[run(166600+i) for i in range(64)];checks={'no_wrong_predictions':all(x['correct']+x['unknown']==x['hold'] for x in xs),'lift_or_lawful_unknown_all':all(x['correct']>x['baseline'] or x['unknown']==x['hold'] for x in xs),'useful_in_majority':sum(x['correct']>0 for x in xs)>=48}
 out={'milestone':'MS1666','pass':14,'worlds':xs,'checks':checks,'pass_all':all(checks.values()),'disposition':'RELATIONAL_COMPOSITION_NOT_GROUP_SPECIFIC'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'useful':sum(x['correct']>0 for x in xs),'all_unknown':sum(x['unknown']==x['hold'] for x in xs)},indent=2))
if __name__=='__main__':main()
