from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityCandidate,CapabilityContract,EpistemicStatus,ExternalCapabilityQualifier,Microseed,QualificationState

def candidate(m,cid,dep,proposal_ref):
    pe=proposal_ref
    c=CapabilityContract(cid,'opaque actual-event binding',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1613',),'UNKNOWN',{},dependencies=(dep,),qualification=QualificationState.CANDIDATE)
    return CapabilityCandidate(cid,c,(pe,),nomination_basis='BOUNDED_CAUSAL_BINDING_PROPOSAL',operational_signature={'dependency_epochs':[[dep,m.capabilities.epochs[dep]]]})

def main():
  with tempfile.TemporaryDirectory(prefix='ms1613-') as td:
    m=Microseed(Path(td))
    for cid in ('ROUTE-OLD','ROUTE-NEW'):
      m.register_capability(CapabilityContract(cid,cid,{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1613',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:cid))
    pe=m.append_evidence('PE-OLD',{'proposal':'binding'},EpistemicStatus.PRESSURE_SUPPORTED,source='LOCAL')
    old_q=m.append_evidence('QE-OLD',{'basis_id':'ROUTE-OLD','causal_contrast':'SUPPORTS'},EpistemicStatus.PROVED,source='HSP_EXTERNAL')
    c1=candidate(m,'BIND-OLD','ROUTE-OLD',pe);m.nominate_capability_candidate(c1)
    t1=ExternalCapabilityQualifier(m.evidence,qualifier_id='HSP-MS1613').qualify(c1,qualification_evidence=(old_q,));m.admit_capability_candidate(t1,handler=lambda **_:'OLD')
    m.invalidate_capability('ROUTE-OLD',reason='QUALIFICATION_BASIS_COLLAPSED')
    # Replacement binding is a different proposal on a fresh route, but the old positive
    # qualification evidence is still accepted by the generic fixed qualifier.
    pe2=m.append_evidence('PE-NEW',{'proposal':'replacement binding'},EpistemicStatus.PRESSURE_SUPPORTED,source='LOCAL')
    c2=candidate(m,'BIND-NEW','ROUTE-NEW',pe2);m.nominate_capability_candidate(c2)
    t2=ExternalCapabilityQualifier(m.evidence,qualifier_id='HSP-MS1613').qualify(c2,qualification_evidence=(old_q,))
    admitted=m.admit_capability_candidate(t2,handler=lambda **_:'NEW')
  out={'pass':'MS1613_PASS11','old_binding_state':'STALE','replacement_qualified_with_old_basis_evidence':admitted.qualification.value,
       'result':'GENERIC_EXTERNAL_CAPABILITY_QUALIFIER_DOES_NOT_ENFORCE_FRESH_REQUALIFICATION_DEBT_FROM_QUALIFICATION_EVIDENCE_ANCESTRY','boundary':'THIS_IS_EXTERNAL_QUALIFIER_ASSISTANCE_DEBT_NOT_PERMISSION_FOR_MICROSEED_SELF_QUALIFICATION','scar':'QUALIFICATION_BASIS_FAILURE_REQUIRES_FRESH_REQUALIFICATION_DEBT_FOR_ACTUAL_EVENT_BINDINGS','authority':'RESEARCH_ONLY'}
  Path('research/MS1613_PASS11_REQUALIFICATION_DEBT_HOSTILE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
