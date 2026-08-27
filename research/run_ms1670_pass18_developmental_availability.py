from __future__ import annotations
import json,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,predict_via_composition,direct_lookup
OUT=Path(__file__).with_name('MS1670_PASS18_DEVELOPMENTAL_AVAILABILITY.json')
def compose(p,q):return {x:q[p[x]] for x in p}
def run(seed,n=8,budget=40):
 rng=random.Random(seed);states=[f'S{seed}-{i}' for i in range(n)];A=dict(zip(states,rng.sample(states,n)));B=dict(zip(states,rng.sample(states,n)));C=compose(A,B);rows=[]
 for t in range(budget):
  s=rng.choice(states);a=rng.choice(('A','B','C'));e={'A':A,'B':B,'C':C}[a][s];rows.append(Transition(digest((seed,t,s,a,e)),digest((seed,'o',t)),s,a,e))
 rel=construct_global_compositions(rows,2);lookup=direct_lookup(rows); target=[r for r in rel if (r.direct_action,r.first_action,r.second_action)==('C','A','B')]
 # evaluate only direct-C keys not already observed but whose components are both known.
 elig=[]
 for s in states:
  if (s,'C') in lookup:continue
  m=lookup.get((s,'A'))
  if m is not None and (m,'B') in lookup:elig.append(s)
 correct=wrong=unknown=0
 for s in elig:
  p,status,_=predict_via_composition(s,'C',rel,rows);truth=C[s]
  if p==truth:correct+=1
  elif p is None:unknown+=1
  else:wrong+=1
 return {'seed':seed,'candidate':bool(target),'eligible':len(elig),'correct':correct,'wrong':wrong,'unknown':unknown}
def main():
 xs=[run(167000+i) for i in range(64)];checks={'no_false_predictions':all(x['wrong']==0 for x in xs),'candidate_available_in_majority':sum(x['candidate'] for x in xs)>=40,'some_heldout_relational_use_in_majority':sum(x['correct']>0 for x in xs)>=32}
 out={'milestone':'MS1670','pass':18,'budget_per_lifetime':40,'worlds':xs,'checks':checks,'pass_all':all(checks.values()),'summary':{'candidate_worlds':sum(x['candidate'] for x in xs),'useful_worlds':sum(x['correct']>0 for x in xs),'wrong_predictions':sum(x['wrong'] for x in xs)},'disposition':'DEVELOPMENTALLY_AVAILABLE_UNDER_THIS_DETERMINISTIC_BUDGET' if all(checks.values()) else 'DEVELOPMENTAL_AVAILABILITY_NARROW'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'summary':out['summary']},indent=2))
if __name__=='__main__':main()
