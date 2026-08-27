from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState
from microseed.development.capability_admission import CapabilityCandidate,ExternalCapabilityQualifier
from microseed.runtime.types import EpistemicStatus

def main():
  with tempfile.TemporaryDirectory(prefix='ms1588-p11-') as td:
    m=Microseed(Path(td))
    prop=m.append_evidence('PROP',{'mapping':'candidate A'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MICROSEED_PROPOSAL')
    # Deliberately circular: the evidence says the mapping is correct because the same labelled channel reported calibration success.
    circular=m.append_evidence('CIRCULAR-CAL',{'channel':'OBS-A','reported_reference':'R1','expected_reference':'R1','basis':'OBS-A_OUTPUT_ONLY'},EpistemicStatus.PRESSURE_SUPPORTED,source='OBS-A')
    c=CapabilityCandidate('OBS-A-MAP',CapabilityContract('OBS-A-MAP','observation mapping',{}, {},(),('CIRCULAR_QUALIFICATION_RISK',),Authority.OBSERVATION_ONLY,('MS1588-P11',),'UNKNOWN',{},qualification=QualificationState.CANDIDATE),(prop,),nomination_basis='RESEARCH')
    m.nominate_capability_candidate(c)
    t=ExternalCapabilityQualifier(m.evidence,qualifier_id='HSP-MS1588').qualify(c,qualification_evidence=(circular,))
    admitted=m.admit_capability_candidate(t,handler=lambda raw,**_:raw)
    out={'pass':'MS1588_PASS11','ticket_state':t.state.value,'ticket_authority':t.authority.value,'admitted_state':admitted.qualification.value,'qualification_evidence_source':m.evidence.get('CIRCULAR-CAL')['source'],'generic_qualifier_checks_source_ancestry_or_circularity':False,'result':'GENERIC_SUPPORTIVE_EVIDENCE_QUALIFIER_CAN_FALSE_GREEN_SELF_REFERENTIAL_OBSERVATION_MAPPING_EVIDENCE','scope':'QUALIFIER_BOUNDARY_SCAR__NOT_PROOF_OF_NEW_ORGANISM_PRIMITIVE','authority':'RESEARCH_ONLY'}
    Path('research/MS1588_PASS11_MAPPING_QUALIFICATION_CIRCULARITY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
