from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,OperationalFrameContract,QualificationState,QueryObligation
from microseed.development.capability_admission import CapabilityCandidate,ExternalCapabilityQualifier
from microseed.runtime.types import EpistemicStatus

def main():
  with tempfile.TemporaryDirectory(prefix='ms1586-p9-') as td:
    m=Microseed(Path(td))
    m.register_operational_frame(OperationalFrameContract('OBS-FRAME','opaque observation interface',hashlib.sha256(b'obs-frame').hexdigest(),Authority.DERIVED_READ_ONLY,('MS1586-P9',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    prop=m.append_evidence('MAP-PROP',{'relation':'raw observation token -> decoded scalar','proposal_only':True},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_ENDOGENOUS_PROPOSAL')
    qual=m.append_evidence('MAP-QUAL',{'hostile_fixture':'mapping held on independent calibration pairs'},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL_QUALIFICATION_FIXTURE')
    proposed=CapabilityContract('OBS-MAP','bounded observation mapping',{'raw':'token'},{'decoded':'scalar'},('NO_TRUTH_AUTHORITY','QUERY_SCOPE_BOUND'),('MAPPING_MAY_DRIFT',),Authority.OBSERVATION_ONLY,('MS1586-P9',),'UNKNOWN',{},query_obligation_id='OBS-Q',qualification=QualificationState.CANDIDATE,operational_scope_id='R2')
    cand=CapabilityCandidate('OBS-MAP',proposed,(prop,),assistance_ancestry=('QUALIFIED_OPERATIONAL_FRAME:OBS-FRAME@0',),nomination_basis='RESEARCH_MAPPING_CANDIDATE',operational_signature={'frame_epochs':[['OBS-FRAME',0]]})
    m.nominate_capability_candidate(cand)
    ticket=ExternalCapabilityQualifier(m.evidence,qualifier_id='HSP-MS1586-P9').qualify(cand,qualification_evidence=(qual,))
    admitted=m.admit_capability_candidate(ticket,handler=lambda raw,**_:float(raw)*2.0)
    q=QueryObligation('OBS-Q','decode observation',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2')
    before=m.capabilities.invoke('OBS-MAP',q,raw='1.25')
    admitted_qualification_before_drift=admitted.qualification.value
    admitted_authority_before_drift=admitted.authority.value
    stale=m.change_operational_frame('OBS-FRAME',reason='OBSERVATION_MAPPING_FRAME_CHANGED')
    after=m.capabilities.invoke('OBS-MAP',q,raw='1.25')
    out={'pass':'MS1586_PASS09','admitted_qualification_before_drift':admitted_qualification_before_drift,'admitted_authority_before_drift':admitted_authority_before_drift,'before_frame_drift':before,'stale_capabilities':sorted(stale),'after_frame_drift':after,'result':'EXISTING_CAPABILITY_PLUS_FRAME_LIFECYCLE_CAN_OWN_OBSERVATION_MAPPING_CURRENTNESS__NO_NEW_SENSOR_REGISTRY','boundary':'QUALIFICATION_EVIDENCE_IS_STILL_EXTERNAL_AND_ITS_INDEPENDENCE_NOT_ESTABLISHED','authority':'RESEARCH_ONLY'}
    Path('research/MS1586_PASS09_MAPPING_AS_CAPABILITY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
