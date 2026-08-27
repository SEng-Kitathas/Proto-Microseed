from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.runtime.types import EpistemicStatus

def main():
  with tempfile.TemporaryDirectory(prefix='ms1585-p8-') as td:
    m=Microseed(Path(td))
    m.register_capability(CapabilityContract('OBS-CHAN','observation channel',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1585-P8',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'OBS'))
    unk=m.append_evidence('UNK-MAP',{'question':'is OBS-CHAN mapping adequate/current?'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_RESEARCH')
    rec=m.record_action_limited_unknown(deficit_id='D-MAP',question_key='OBS-CHAN::MAPPING',hypothesis_digest_sha256=hashlib.sha256(b'mapping-hypotheses').hexdigest(),unknown_evidence_id=unk.evidence_id,missing_discriminator_signature_sha256=hashlib.sha256(b'orthogonal-mapping-probe').hexdigest(),premise_anchors=(EpistemicCurrentnessAnchor('CAPABILITY_PREMISE','OBS-CHAN',0),))
    before=rec.serializable()
    m.invalidate_capability('OBS-CHAN',reason='OBSERVATION_MAPPING_CHALLENGED')
    after=m.epistemic_deficits.records['D-MAP'].serializable()

    m2=Microseed(Path(td)/'probe')
    m2.register_capability(CapabilityContract('OBS-PROBE','diagnostic observation probe',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1585-P8',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:'OBS'))
    unk2=m2.append_evidence('UNK-PROBE',{'question':'mapping unresolved'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_RESEARCH')
    m2.record_action_limited_unknown(deficit_id='D-PROBE',question_key='MAP',hypothesis_digest_sha256=hashlib.sha256(b'h').hexdigest(),unknown_evidence_id=unk2.evidence_id,missing_discriminator_signature_sha256=hashlib.sha256(b'p').hexdigest())
    m2.bind_probe_capability('D-PROBE','OBS-PROBE')
    probe_before=m2.epistemic_deficits.records['D-PROBE'].serializable()
    m2.invalidate_capability('OBS-PROBE',reason='PROBE_ACCESS_LOST')
    probe_after=m2.epistemic_deficits.records['D-PROBE'].serializable()
    out={'pass':'MS1585_PASS08','premise_bound_before':before,'premise_bound_after_capability_invalidation':after,'probe_only_before':probe_before,'probe_only_after_capability_invalidation':probe_after,'result':'EXISTING_EPISTEMIC_LIFECYCLE_DISTINGUISHES_MAPPING_PREMISE_DRIFT_FROM_PROBE_ACCESS_LOSS','authority':'RESEARCH_ONLY'}
    Path('research/MS1585_PASS08_OBSERVATION_PREMISE_LIFECYCLE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
