from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,EpistemicStatus,Microseed,QualificationState
from microseed.development.epistemic import EpistemicCurrentnessAnchor

def sha(x): return hashlib.sha256(x.encode()).hexdigest()

def main():
  with tempfile.TemporaryDirectory(prefix='ms1610-') as td:
    m=Microseed(Path(td))
    for cid in ('INTERVENTION-ROUTE','TARGET-ROUTE','CONTROL-ROUTE'):
      auth=Authority.EFFECT if cid=='INTERVENTION-ROUTE' else Authority.OBSERVATION_ONLY
      m.register_capability(CapabilityContract(cid,cid,{}, {},(),(),auth,('MS1610',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:cid))
    u=m.append_evidence('E-U',{'cause':'UNRESOLVED_CAUSAL_MEDIATOR'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='LOCAL')
    rec=m.record_action_limited_unknown(deficit_id='D-CAUSE',question_key='OPAQUE-CAUSE-Q',hypothesis_digest_sha256=sha('HSET'),unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256=sha('NEGATIVE-CONTROL'),premise_anchors=(EpistemicCurrentnessAnchor('CAPABILITY_PREMISE','TARGET-ROUTE',0),EpistemicCurrentnessAnchor('CAPABILITY_PREMISE','INTERVENTION-ROUTE',0)))
    m.bind_probe_capability('D-CAUSE','CONTROL-ROUTE')
    probe=m.append_evidence('E-P',{'target_change':True,'control_change':False},EpistemicStatus.PRESSURE_SUPPORTED,source='CONTROL-ROUTE')
    revisit=m.record_epistemic_probe_evidence('D-CAUSE',probe.evidence_id)
    # Probe loss reopens action-limited; premise loss stales the question.
    m.invalidate_capability('CONTROL-ROUTE',reason='CONTROL_ROUTE_LOST')
    after_probe_loss=m.epistemic_deficit_status('D-CAUSE')
    m.invalidate_capability('TARGET-ROUTE',reason='TARGET_ROUTE_CHANGED')
    after_premise_loss=m.epistemic_deficit_status('D-CAUSE')
  out={'pass':'MS1610_PASS08','initial':rec.serializable(),'after_probe_evidence':revisit,'after_probe_loss':after_probe_loss,'after_premise_loss':after_premise_loss,
       'result':'EXISTING_EPISTEMIC_DEFICIT_LIFECYCLE_CARRIES_CAUSAL_ATTRIBUTION_UNKNOWN__PROBE_LOSS_ACTION_LIMITED__PREMISE_DRIFT_STALE','authority':'RESEARCH_ONLY'}
  Path('research/MS1610_PASS08_CAUSAL_DEFICIT_LIFECYCLE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
