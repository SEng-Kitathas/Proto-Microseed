from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from opaque_relational_algebra import Transition,digest,construct_global_compositions,predict_via_composition
OUT=Path(__file__).with_name('MS1669_PASS17_RELATIONAL_CONSTRUCTOR_HOSTILES.json')
def base_rows():
 s=['S0','S1','S2','S3','S4'];rows=[]
 def add(tag,x,a,y,origin=None):rows.append(Transition(digest((tag,x,a,y)),origin or digest(('o',tag,x,a,y)),x,a,y))
 # Unique target: A=+1, B=+2, C=+3 over five opaque states.
 for i,x in enumerate(s):
  add('a',x,'A',s[(i+1)%5]); add('b',x,'B',s[(i+2)%5])
 for i,x in enumerate(s[:3]):add('c',x,'C',s[(i+3)%5])
 return rows

def hostile_results():
 rows=base_rows();good=construct_global_compositions(rows,2);target=lambda rs:[r for r in rs if (r.direct_action,r.first_action,r.second_action)==('C','A','B')]
 results={}
 # 1 observed counterexample must kill global relation.
 r1=list(rows)+[Transition(digest('ce-a'),digest('ce-oa'),'S3','C','S2')]
 results['ignore_counterexample']=len(target(construct_global_compositions(r1,2)))==0
 # 2 replay same physical origins must not create support: use only one support start, duplicated events.
 one=[r for r in rows if r.start in {'S0','S1'}]
 # construct a minimal one-witness dataset and replay exact origins under new event ids
 mini=[]
 # Keep exactly one valid C=A then B witness: S0 --A--> S1 --B--> S3 and S0 --C--> S3.
 for r in rows:
  if (r.start,r.action) in {('S0','A'),('S1','B'),('S0','C')}: mini.append(r)
 replay=mini+[Transition(digest(('replay',i,j,r.evidence_id)),r.origin_id,r.start,r.action,r.end) for i,r in enumerate(mini) for j in range(4)]
 results['event_replay_inflates_support']=len(target(construct_global_compositions(replay,2)))==0
 # 3 disagreement must remain UNKNOWN.
 amb=list(rows)
 amb += [Transition(digest(('d',s)),digest(('od',s)),s,'D',f'M{i}') for i,s in enumerate(['S0','S1','S2','S3','S4'])]
 # D then E agrees with C on the three direct-C training starts, but diverges on S3/S4.
 amb += [Transition(digest(('e',i)),digest(('oe',i)),f'M{i}', 'E', out) for i,out in enumerate(['S3','S4','S0','S2','S1'])]
 rel=construct_global_compositions(amb,2);p,status,_=predict_via_composition('S3','C',rel,amb);results['force_first_under_disagreement']=p is None and status=='UNKNOWN_RELATIONAL_DISAGREEMENT'
 # 4 proposal relations must carry no truth/effect authority.
 results['self_authorize_relation']=all(r.truth_authority=='NONE' and r.execution_authority=='NONE' for r in good)
 # 5 missing component path must not be synthesized.
 cut=[r for r in rows if not (r.start=='S4' and r.action=='B')];rels_cut=[r for r in construct_global_compositions(cut,2) if (r.direct_action,r.first_action,r.second_action)==('C','A','B')];p2,status2,_=predict_via_composition('S3','C',rels_cut,cut);results['synthesize_missing_component_path']=p2 is None and status2.startswith('UNKNOWN')
 return results

def main():
 results=hostile_results();out={'milestone':'MS1669','pass':17,'hostiles':results,'rejected':sum(results.values()),'total':len(results),'pass_all':all(results.values()),'disposition':'HOSTILE_CLEAN' if all(results.values()) else 'HOSTILE_ESCAPE'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
