from __future__ import annotations
import json,hashlib,tempfile,random
from pathlib import Path
from microseed import Microseed,Authority,QualificationState,OperationalFrameContract,EpisodeSchemaContract,ConstructorProjectionSample,ConstructorGrowthConfig
OUT=Path(__file__).with_name('MS1663_PASS11_PROJECTION_SCOPED_OPAQUE_ALGEBRA.json')
def H(x):return hashlib.sha256(str(x).encode()).hexdigest()

def step(states,s,a,ctx):
 i=states.index(s)
 if a=='A':return states[(i+1)%len(states)]
 if a=='B':return states[(i-1)%len(states)]
 if a=='C':return states[(i+(2 if ctx=='CTX-L' else -2))%len(states)]
 raise KeyError(a)

def relation_stance(states,s,ctx):
 c=step(states,s,'C',ctx); aa=step(states,step(states,s,'A',ctx),'A',ctx); bb=step(states,step(states,s,'B',ctx),'B',ctx)
 if c==aa and c!=bb:return 'REL-AA'
 if c==bb and c!=aa:return 'REL-BB'
 return 'REL-UNKNOWN'

def samples(prefix,n=240,seed=1):
 rng=random.Random(seed); states=[f'S{i}' for i in range(7)]; out=[]
 for i in range(n):
  s=rng.choice(states);ctx='CTX-L' if i%2==0 else 'CTX-R'; stance=relation_stance(states,s,ctx)
  # Current token is deliberately uninformative random nuisance; prior token carries opaque context.
  now=(f'N{rng.randrange(4)}',); old=(ctx,)
  out.append(ConstructorProjectionSample(f'{prefix}-{i}',(now,old),'RELQ',stance,None,'F',0,'EPS',0))
 return out

def main():
 td=tempfile.TemporaryDirectory(prefix='ms1663-');m=Microseed(Path(td.name));m.register_operational_frame(OperationalFrameContract('F','opaque-current-boundary',H('F'),Authority.DERIVED_READ_ONLY,('MS1663',),'CURRENT',QualificationState.SHADOW_QUALIFIED));m.register_episode_schema(EpisodeSchemaContract('EPS','opaque-history-boundary',H('EPS'),Authority.DERIVED_READ_ONLY,('MS1663',),'CURRENT',QualificationState.SHADOW_QUALIFIED,(),(('F',0),)))
 cfg=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=100,min_validation_accuracy=.99,min_lift_over_action_baseline=.40,min_scope_accuracy=.99)
 found=m.discover_epistemic_constructor_candidates(samples('tr',seed=1),samples('pr',seed=2),samples('va',seed=3),cfg)
 cand=m.epistemic_constructor_candidates[found[0]['candidate_id']] if found else None
 # Use the discovered opaque bucket->stance prediction to choose the appropriate endpoint-equivalence relation on heldout states.
 states=[f'S{i}' for i in range(7)]; table={(b,a):e for b,a,e in cand.bucket_action_prediction} if cand else {}
 predictions=[]
 for ctx in ('CTX-L','CTX-R'):
  for s in states:
   bucket=cand.project((('N0',),(ctx,))) if cand else None
   stance=table.get((bucket,'RELQ')) if bucket else None
   path=('A','A') if stance=='REL-AA' else ('B','B') if stance=='REL-BB' else None
   if path:
    e=step(states,step(states,s,path[0],ctx),path[1],ctx)
   else:e=None
   truth=step(states,s,'C',ctx)
   predictions.append((ctx,s,stance,e,truth,e==truth))
 checks={'projection_found':cand is not None,'projection_uses_history':cand is not None and any(a.lag==1 for a in cand.atoms),'scoped_algebra_predicts_all_heldout':all(x[-1] for x in predictions),'projection_zero_semantic_truth_authority':cand is not None and cand.semantic_projection_authority=='NONE' and cand.truth_authority=='NONE'}
 out={'milestone':'MS1663','pass':11,'checks':checks,'pass_all':all(checks.values()),'candidate':cand.serializable() if cand else None,'predictions':predictions,'disposition':'EXISTING_OPAQUE_PROJECTION_CAN_SCOPE_RELATIONAL_ALGEBRA','nonclaim':'REL-AA/REL-BB are derived endpoint-equality stances, not semantic context labels or truth authority.'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'atoms':[(a.lag,a.position) for a in cand.atoms] if cand else None},indent=2));td.cleanup()
if __name__=='__main__':main()
