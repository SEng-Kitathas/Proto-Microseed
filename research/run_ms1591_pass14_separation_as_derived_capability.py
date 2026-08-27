from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState,QueryObligation

def cap(cid): return CapabilityContract(cid,'observation channel',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1591-P14',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:cid)
def main():
  with tempfile.TemporaryDirectory(prefix='ms1591-p14-') as td:
    m=Microseed(Path(td));m.register_capability(cap('OBS-A'));m.register_capability(cap('OBS-B'))
    pair=CapabilityContract('PAIR-SEPARATE','bounded functional separation witness',{}, {},('BOUNDED_TESTED_SCOPE_ONLY',),('NO_UNIVERSAL_INDEPENDENCE_AUTHORITY',),Authority.DERIVED_READ_ONLY,('MS1590-P13',),'CURRENT',{},dependencies=('OBS-A','OBS-B'),query_obligation_id='PAIR-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'pair':['OBS-A','OBS-B'],'relation':'SEPARATE_UNDER_TESTED_INTERVENTIONS'},operational_scope_id='SELECTIVE-PROBES')
    m.register_capability(pair)
    good=m.capabilities.invoke('PAIR-SEPARATE',QueryObligation('PAIR-Q','bounded pair use',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='SELECTIVE-PROBES'))
    broad=m.capabilities.invoke('PAIR-SEPARATE',QueryObligation('PAIR-Q','broad independence',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='ALL-FAILURE-MODES'))
    stale=m.invalidate_capability('OBS-A',reason='CHANNEL_A_CHALLENGED')
    after=m.capabilities.invoke('PAIR-SEPARATE',QueryObligation('PAIR-Q','bounded pair use',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='SELECTIVE-PROBES'))
    out={'pass':'MS1591_PASS14','bounded_scope_use':good,'broad_scope_use':broad,'stale_closure':sorted(stale),'after_channel_stale':after,'result':'EXISTING_DERIVED_CAPABILITY_DEPENDENCY_QUERY_SCOPE_CAN_OWN_BOUNDED_CHANNEL_SEPARATION__NO_INDEPENDENCE_REGISTRY','qualification_note':'DIRECT_SHADOW_REGISTRATION_USED_ONLY_TO_TEST_EXISTING_REPRESENTATION_AND_LIFECYCLE','authority':'RESEARCH_ONLY'}
    Path('research/MS1591_PASS14_SEPARATION_AS_DERIVED_CAPABILITY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
