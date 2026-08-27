from __future__ import annotations
import json,hashlib,tempfile
from pathlib import Path
from microseed import Microseed,Authority,QualificationState,OperationalFrameContract,EpisodeSchemaContract,ConstructorProjectionSample,ConstructorGrowthConfig
OUT=Path(__file__).with_name('MS1661_PASS09_EXISTING_TEMPORAL_CONSTRUCTOR_RECOVERY.json')
def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
def rows(prefix,n=256):
 out=[]
 # Opaque current token intentionally useless. Prior opaque token + action determines opaque effect.
 for i in range(n):
  old='OLD-L' if (i%4)<2 else 'OLD-R'; now='NOW-X'; action='A0' if i%2==0 else 'A1'
  effect=('E0' if old=='OLD-L' else 'E1') if action=='A0' else ('E1' if old=='OLD-L' else 'E0')
  out.append(ConstructorProjectionSample(f'{prefix}-{i}',((now,),(old,)),action,effect,None,'F',0,'EPS',0))
 return out

def main():
 td=tempfile.TemporaryDirectory(prefix='ms1661-');m=Microseed(Path(td.name))
 m.register_operational_frame(OperationalFrameContract('F','opaque-frame',H('F'),Authority.DERIVED_READ_ONLY,('MS1661',),'CURRENT',QualificationState.SHADOW_QUALIFIED,('EXTERNAL_FRAME',)))
 m.register_episode_schema(EpisodeSchemaContract('EPS','opaque-history',H('EPS'),Authority.DERIVED_READ_ONLY,('MS1661',),'CURRENT',QualificationState.SHADOW_QUALIFIED,('EXTERNAL_EPISODE_SCHEMA',),(('F',0),)))
 cfg0=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=0,min_train_support=100,min_validation_accuracy=.99,min_lift_over_action_baseline=.40,min_scope_accuracy=.99)
 cfg1=ConstructorGrowthConfig(max_support_ceiling=2,max_lag_ceiling=1,min_train_support=100,min_validation_accuracy=.99,min_lift_over_action_baseline=.40,min_scope_accuracy=.99)
 no=m.discover_epistemic_constructor_candidates(rows('tr'),rows('pr'),rows('va'),cfg0)
 yes=m.discover_epistemic_constructor_candidates(rows('tr2'),rows('pr2'),rows('va2'),cfg1)
 cand=m.epistemic_constructor_candidates[yes[0]['candidate_id']] if yes else None
 checks={'present_only_frame_abstains':no==[],'existing_temporal_constructor_recovers':bool(yes),'recovered_candidate_uses_prior_opaque_slice':cand is not None and any(a.lag==1 for a in cand.atoms),'candidate_zero_semantic_truth_authority':cand is not None and cand.semantic_projection_authority=='NONE' and cand.truth_authority=='NONE'}
 out={'milestone':'MS1661','pass':9,'checks':checks,'pass_all':all(checks.values()),'candidate':cand.serializable() if cand else None,'disposition':'EXISTING_CONSTRUCTOR_CAN_EXPAND_OPAQUE_FRAME_WHEN_DISCRIMINATOR_IS_ALREADY_IN_ASSURED_HISTORY','nonclaim':'The episode/history boundary remains supplied and qualified; this does not construct time or invent an unobserved context.'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps({'checks':checks,'atoms':[(a.lag,a.position) for a in cand.atoms] if cand else None},indent=2));td.cleanup()
if __name__=='__main__':main()
