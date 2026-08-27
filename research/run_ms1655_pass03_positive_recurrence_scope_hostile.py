from __future__ import annotations
import json, hashlib
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
OUT=Path(__file__).with_name('MS1655_PASS03_POSITIVE_RECURRENCE_SCOPE_HOSTILE.json')
def H(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@dataclass(frozen=True)
class T: evidence_id:str; origin_id:str; start:str; action:str; end:str

def derive_positive_only(rows,min_support=2):
 by={(r.start,r.action):r for r in rows}; states=sorted({r.start for r in rows}|{r.end for r in rows}); acts=sorted({r.action for r in rows}); g=defaultdict(set)
 for s in states:
  for c in acts:
   d=by.get((s,c))
   if not d:continue
   for a in acts:
    r1=by.get((s,a))
    if not r1:continue
    for b in acts:
     r2=by.get((r1.end,b))
     if r2 and r2.end==d.end:g[(c,a,b)].add(H(tuple(sorted({d.origin_id,r1.origin_id,r2.origin_id}))))
 return {k:v for k,v in g.items() if len(v)>=min_support}

def derive_with_counterexamples(rows,min_support=2):
 by={(r.start,r.action):r for r in rows}; states=sorted({r.start for r in rows}|{r.end for r in rows}); acts=sorted({r.action for r in rows}); stats=defaultdict(lambda:{'yes':set(),'no':set()})
 for s in states:
  for c in acts:
   d=by.get((s,c))
   if not d:continue
   for a in acts:
    r1=by.get((s,a))
    if not r1:continue
    for b in acts:
     r2=by.get((r1.end,b))
     if not r2:continue
     sig=H(tuple(sorted({d.origin_id,r1.origin_id,r2.origin_id})))
     stats[(c,a,b)]['yes' if r2.end==d.end else 'no'].add(sig)
 out={}
 for k,v in stats.items():
  if len(v['yes'])>=min_support and not v['no']:out[k]=v
 return out,stats

def fixture():
 # Six opaque states. C=A∘B on Q0,Q1,Q2 only; contradicted on Q3,Q4,Q5.
 states=[f'Q{i}' for i in range(6)]; rows=[]
 A,B,C='A','B','C'
 def add(s,a,e):rows.append(T(H((s,a,e)),H(('origin',s,a,e)),s,a,e))
 # A and B are simple total transitions, opaque to learner.
 for i,s in enumerate(states):
  add(s,A,states[(i+1)%6]); add(s,B,states[(i+1)%6])
 for i,s in enumerate(states):
  composed=states[(i+2)%6]
  direct=composed if i<3 else states[(i+3)%6]
  add(s,C,direct)
 return rows

def main():
 rows=fixture(); pos=derive_positive_only(rows); strict,stats=derive_with_counterexamples(rows)
 target=('C','A','B')
 r={'milestone':'MS1655','pass':3,'target':target,'positive_only_nominates':target in pos,'positive_support':len(stats[target]['yes']),'negative_support':len(stats[target]['no']),'counterexample_aware_nominates':target in strict,
 'checks':{'positive_recurrence_false_greens_global_relation':target in pos,'counterexamples_exist':len(stats[target]['no'])>=2,'counterexample_aware_global_relation_rejected':target not in strict},
 'scar':'POSITIVE_RELATIONAL_RECURRENCE_NE_UNIVERSAL_RELATIONAL_SCOPE','disposition':'GLOBAL_COMPOSITION_REQUIRES_COUNTEREXAMPLE_ACCOUNTING'}
 r['pass_all']=all(r['checks'].values());OUT.write_text(json.dumps(r,indent=2,sort_keys=True));print(json.dumps(r,indent=2,sort_keys=True))
if __name__=='__main__':main()
