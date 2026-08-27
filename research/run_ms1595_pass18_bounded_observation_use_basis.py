from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState,QueryObligation

def reg(m,cid,auth=Authority.DERIVED_READ_ONLY,deps=(),qid=None,scope=None,value=None):
    m.register_capability(CapabilityContract(cid,cid,{}, {},('NO_TRUTH_AUTHORITY',),(),auth,('MS1595-P18',),'CURRENT',{},dependencies=tuple(deps),query_obligation_id=qid,qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:value if value is not None else cid,operational_scope_id=scope))
def main():
  with tempfile.TemporaryDirectory(prefix='ms1595-p18-') as td:
    m=Microseed(Path(td))
    reg(m,'OBS-MAP',Authority.OBSERVATION_ONLY,value={'decoded':'VALUE'})
    reg(m,'POSTEXEC-ROUTE',Authority.DERIVED_READ_ONLY,value='POST_EXECUTION_CAUSAL_ROUTE')
    reg(m,'PAIR-SEPARATE',Authority.DERIVED_READ_ONLY,value='SEPARATE_UNDER_TESTED_INTERVENTIONS')
    reg(m,'OBS-USE-BASIS',Authority.DERIVED_READ_ONLY,deps=('OBS-MAP','POSTEXEC-ROUTE','PAIR-SEPARATE'),qid='OBS-USE-Q',scope='R2-BOUNDED-THREAT',value={'mapping':'OBS-MAP','causal_route':'POSTEXEC-ROUTE','separation':'PAIR-SEPARATE','truth_authority':'NONE','claim':'USABLE_WITHIN_EXACT_SCOPE_NOT_ACTUALNESS'})
    q=QueryObligation('OBS-USE-Q','bounded outcome evidence use',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='R2-BOUNDED-THREAT')
    good=m.capabilities.invoke('OBS-USE-BASIS',q)
    broad=m.capabilities.invoke('OBS-USE-BASIS',QueryObligation('OBS-USE-Q','universal actualness',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='UNBOUNDED'))
    stale=m.invalidate_capability('POSTEXEC-ROUTE',reason='CAUSAL_ROUTE_CHALLENGED')
    after=m.capabilities.invoke('OBS-USE-BASIS',q)
    out={'pass':'MS1595_PASS18','bounded_use':good,'broad_use':broad,'stale_closure':sorted(stale),'after_route_stale':after,'result':'EXISTING_CAPABILITY_DEPENDENCY_PLUS_QUERY_SCOPE_CAN_CARRY_TRANSIENT_BOUNDED_OBSERVATION_USE_BASIS__NO_NEW_ASSURANCE_REGISTRY','boundary':'BASIS_QUALIFICATION_EVIDENCE_STILL_MUST_BE_LAWFULLY_GROUNDED','authority':'RESEARCH_ONLY'}
    Path('research/MS1595_PASS18_BOUNDED_OBSERVATION_USE_BASIS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
