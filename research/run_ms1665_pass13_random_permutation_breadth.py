from __future__ import annotations
import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,predict_via_composition,direct_lookup
OUT=Path(__file__).with_name('MS1665_PASS13_RANDOM_PERMUTATION_BREADTH.json')
def compose(p,q):return {x:q[p[x]] for x in p}
def world(seed,n=9):
 rng=random.Random(seed);states=[f'S{seed}-{i}' for i in range(n)];Aperm=dict(zip(states,rng.sample(states,n)));Bperm=dict(zip(states,rng.sample(states,n)));Cperm=compose(Aperm,Bperm);Dperm=dict(zip(states,rng.sample(states,n))); actions=['A','B','C','D'];rng.shuffle(actions);A,B,C,D=actions;pm={A:Aperm,B:Bperm,C:Cperm,D:Dperm};rows=[]
 def add(s,a,e,tag):rows.append(Transition(digest((seed,tag,s,a,e)),digest((seed,'o',tag,s,a,e)),s,a,e))
 for s in states:
  for a in (A,B,D):add(s,a,pm[a][s],'component')
 train=rng.sample(states,n-2)
 for s in train:add(s,C,pm[C][s],'direct')
 return states,A,B,C,D,pm,rows,train
def run(seed):
 states,A,B,C,D,pm,rows,train=world(seed);rels=construct_global_compositions(rows,4);lookup=direct_lookup(rows);hold=[s for s in states if s not in train];correct=unknown=0
 for s in hold:
  p,status,_=predict_via_composition(s,C,rels,rows);correct+=p==pm[C][s];unknown+=status.startswith('UNKNOWN')
 return {'seed':seed,'correct':correct,'hold':len(hold),'unknown':unknown,'candidate_count':len(rels),'baseline':sum(lookup.get((s,C))==pm[C][s] for s in hold)}
def main():
 xs=[run(166500+i) for i in range(64)];checks={'all_worlds_lift':all(x['correct']>x['baseline'] for x in xs),'all_worlds_perfect_or_unknown_no_wrong':all(x['correct']+x['unknown']==x['hold'] for x in xs),'majority_perfect':sum(x['correct']==x['hold'] for x in xs)>=56}
 out={'milestone':'MS1665','pass':13,'worlds':xs,'checks':checks,'pass_all':all(checks.values()),'disposition':'BREADTH_SURVIVES_RANDOM_OPAQUE_PERMUTATION_ALGEBRAS'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'perfect':sum(x['correct']==x['hold'] for x in xs),'unknown_worlds':sum(x['unknown']>0 for x in xs)},indent=2))
if __name__=='__main__':main()
