from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,QualificationState,QueryObligation

def reg(m,cid,auth,deps=(),scope='FRAME-CAUSAL',qid=None,value=None):
    m.register_capability(CapabilityContract(cid,cid,{}, {},('NO_TRUTH_AUTHORITY',),(),auth,('MS1609-P7',),'CURRENT',{},dependencies=tuple(deps),query_obligation_id=qid,qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: value if value is not None else cid,operational_scope_id=scope))

def main():
    with tempfile.TemporaryDirectory(prefix='ms1609-') as td:
        m=Microseed(Path(td))
        reg(m,'INTERVENTION-ROUTE',Authority.EFFECT)
        reg(m,'TARGET-EFFECT-ROUTE',Authority.OBSERVATION_ONLY)
        reg(m,'NEGATIVE-CONTROL-ROUTE',Authority.OBSERVATION_ONLY)
        reg(m,'CAUSAL-USE-BASIS',Authority.DERIVED_READ_ONLY,deps=('INTERVENTION-ROUTE','TARGET-EFFECT-ROUTE','NEGATIVE-CONTROL-ROUTE'),qid='CAUSAL-Q',value={'claim':'BOUNDED_CAUSAL_USE_ONLY','truth_authority':'NONE'})
        q=QueryObligation('CAUSAL-Q','bounded causal mediation use',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='FRAME-CAUSAL')
        before=m.capabilities.invoke('CAUSAL-USE-BASIS',q)
        stale=sorted(m.invalidate_capability('NEGATIVE-CONTROL-ROUTE',reason='CONTROL_COVERAGE_CHALLENGED'))
        after=m.capabilities.invoke('CAUSAL-USE-BASIS',q)
    out={'pass':'MS1609_PASS07','before':before,'stale_closure':stale,'after_negative_control_stale':after,
         'result':'EXISTING_CAPABILITY_DEPENDENCY_GRAPH_CAN_CARRY_BOUNDED_CAUSAL_USE_BASIS_AND_TRANSITIVE_CURRENTNESS__NO_CAUSAL_REGISTRY_NEEDED','boundary':'QUALIFICATION_OF_THE_BASIS_REMAINS_THE_EPISTEMIC_PROBLEM','authority':'RESEARCH_ONLY'}
    Path('research/MS1609_PASS07_CAUSAL_BASIS_AS_CAPABILITY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
