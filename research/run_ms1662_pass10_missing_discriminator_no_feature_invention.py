from __future__ import annotations
import json,hashlib,tempfile
from pathlib import Path
from microseed import Microseed,Authority,QualificationState,OperationalFrameContract,EpisodeSchemaContract,ConstructorProjectionSample,ConstructorGrowthConfig
OUT=Path(__file__).with_name('MS1662_PASS10_MISSING_DISCRIMINATOR_NO_FEATURE_INVENTION.json')
def H(x):return hashlib.sha256(str(x).encode()).hexdigest()
def rows(prefix,n=256):
 out=[]
 # Evaluator-hidden bit flips effect, but neither current nor prior supplied opaque slices contain it.
 for i in range(n):
  hidden=(i//2)%2; now='NOW-X';old='OLD-X';action='A0' if i%2==0 else 'A1';effect=f'E{hidden ^ (action=="A1")}'
  out.append(ConstructorProjectionSample(f'{prefix}-{i}',((now,),(old,)),action,effect,None,'F',0,'EPS',0))
 return out

def main():
 td=tempfile.TemporaryDirectory(prefix='ms1662-');m=Microseed(Path(td.name));m.register_operational_frame(OperationalFrameContract('F','opaque-frame',H('F'),Authority.DERIVED_READ_ONLY,('MS1662',),'CURRENT',QualificationState.SHADOW_QUALIFIED));m.register_episode_schema(EpisodeSchemaContract('EPS','opaque-history',H('EPS'),Authority.DERIVED_READ_ONLY,('MS1662',),'CURRENT',QualificationState.SHADOW_QUALIFIED,(),(('F',0),)))
 cfg=ConstructorGrowthConfig(max_support_ceiling=4,max_lag_ceiling=1,min_train_support=100,min_validation_accuracy=.90,min_lift_over_action_baseline=.20,min_scope_accuracy=.84)
 found=m.discover_epistemic_constructor_candidates(rows('tr'),rows('pr'),rows('va'),cfg)
 checks={'no_candidate_when_discriminator_never_enters_observation':found==[]}
 out={'milestone':'MS1662','pass':10,'checks':checks,'pass_all':all(checks.values()),'found':found,'disposition':'IDENTIFIABILITY_LIMIT__NO_FEATURE_INVENTION','scar':'FRAME_CONSTRUCTOR_CANNOT_CREATE_INFORMATION_ABSENT_FROM_ASSURED_EXPERIENCE'}
 OUT.write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True));td.cleanup()
if __name__=='__main__':main()
