from __future__ import annotations
import json,random,hashlib,tempfile
from pathlib import Path
from microseed import Microseed,Authority,QualificationState,OperationalFrameContract,EpisodeSchemaContract,ConstructorProjectionSample,ConstructorGrowthConfig
OUT=Path(__file__).with_name('MS1664_PASS12_SCOPED_ALGEBRA_GAUGE_RENAMING.json')
def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
def build_maps(seed=1664):
 rng=random.Random(seed)
 state={f'S{i}':f'Q-{rng.randrange(10**9)}' for i in range(7)}
 action={x:f'A-{rng.randrange(10**9)}' for x in ('A','B','C','RELQ')}
 ctx={x:f'K-{rng.randrange(10**9)}' for x in ('CTX-L','CTX-R')}
 stance={x:f'R-{rng.randrange(10**9)}' for x in ('REL-AA','REL-BB')}
 return state,action,ctx,stance

def step(states,s,a,ctx,A,B,C,L):
 i=states.index(s)
 if a==A:return states[(i+1)%len(states)]
 if a==B:return states[(i-1)%len(states)]
 if a==C:return states[(i+(2 if ctx==L else -2))%len(states)]
 raise KeyError(a)
def main():
 sm,am,cm,rm=build_maps();states=[sm[f'S{i}'] for i in range(7)];A,B,C,RQ=[am[x] for x in ('A','B','C','RELQ')];L,R=cm['CTX-L'],cm['CTX-R'];RA,RB=rm['REL-AA'],rm['REL-BB']
 def stance(s,ctx):
  c=step(states,s,C,ctx,A,B,C,L);aa=step(states,step(states,s,A,ctx,A,B,C,L),A,ctx,A,B,C,L);bb=step(states,step(states,s,B,ctx,A,B,C,L),B,ctx,A,B,C,L)
  return RA if c==aa else RB if c==bb else 'UNKNOWN'
 def rows(prefix,n,seed):
  rng=random.Random(seed);out=[]
  for i in range(n):
   s=rng.choice(states);ctx=L if i%2==0 else R;out.append(ConstructorProjectionSample(f'{prefix}-{i}',((f'N{rng.randrange(4)}',),(ctx,)),RQ,stance(s,ctx),None,'F',0,'EPS',0))
  return out
 td=tempfile.TemporaryDirectory(prefix='ms1664-');m=Microseed(Path(td.name));m.register_operational_frame(OperationalFrameContract('F','opaque',H('F'),Authority.DERIVED_READ_ONLY,('MS1664',),'CURRENT',QualificationState.SHADOW_QUALIFIED));m.register_episode_schema(EpisodeSchemaContract('EPS','opaque-hist',H('EPS'),Authority.DERIVED_READ_ONLY,('MS1664',),'CURRENT',QualificationState.SHADOW_QUALIFIED,(),(('F',0),)))
 cfg=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=100,min_validation_accuracy=.99,min_lift_over_action_baseline=.40,min_scope_accuracy=.99)
 found=m.discover_epistemic_constructor_candidates(rows('tr',240,1),rows('pr',240,2),rows('va',240,3),cfg);cand=m.epistemic_constructor_candidates[found[0]['candidate_id']] if found else None;table={(b,a):e for b,a,e in cand.bucket_action_prediction} if cand else {}
 good=[]
 for ctx in (L,R):
  for s in states:
   bucket=cand.project((('N0',),(ctx,)));st=table[(bucket,RQ)];path=(A,A) if st==RA else (B,B) if st==RB else None;e=step(states,step(states,s,path[0],ctx,A,B,C,L),path[1],ctx,A,B,C,L) if path else None;truth=step(states,s,C,ctx,A,B,C,L);good.append(e==truth)
 checks={'renamed_constructor_found':cand is not None,'renamed_scoped_algebra_equivalent':all(good),'literal_labels_carry_no_required_semantics':all(x not in str(cand.serializable()) for x in ('CTX-L','CTX-R','REL-AA','REL-BB')) if cand else False}
 out={'milestone':'MS1664','pass':12,'checks':checks,'pass_all':all(checks.values()),'maps':{'state':sm,'action':am,'context':cm,'relation':rm},'disposition':'GAUGE_RENAMING_PRESERVES_SCOPED_RELATIONAL_FRAME'};OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True));td.cleanup()
if __name__=='__main__':main()
