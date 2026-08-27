from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Observation,QualificationState,QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare
TRUE_POST={"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}; FALSE_POST={"ENERGY":4.6,"THERMAL":8.3,"INTEGRITY":5.1}

def install(m,payload):
    m.register_capability(CapabilityContract('OBS-OUTCOME','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1596',),'CURRENT',{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(payload)))
    m.register_capability(CapabilityContract('OBS-USE-BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1596',),'CURRENT',{},dependencies=('OBS-OUTCOME',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2-THREAT'))
def via_basis(m,eid,evidence_id,scope='R2-THREAT'):
    q=QueryObligation('BASIS-Q','bounded observation use',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id=scope)
    basis=m.capabilities.invoke('OBS-USE-BASIS',q)
    if basis.get('status')!='CAPABILITY_RESULT': return {'status':'OUTCOME_REJECTED','reason':'OBSERVATION_BASIS_NOT_CURRENT','basis':basis}
    obsr=m.capabilities.invoke('OBS-OUTCOME',QueryObligation('RAW','raw'))
    if obsr.get('status')!='CAPABILITY_RESULT': return {'status':'OUTCOME_REJECTED','reason':'OBSERVATION_CHANNEL_NOT_CURRENT'}
    return m.record_bounded_action_outcome(eid,Observation('CAP-'+evidence_id,'OBS-OUTCOME',f'action-execution:{eid}',obsr['value'],authority=Authority.OBSERVATION_ONLY,lineage=('BASIS:OBS-USE-BASIS','CHANNEL:OBS-OUTCOME')),evidence_id=evidence_id)
def main():
  with tempfile.TemporaryDirectory(prefix='ms1596-p19-') as td:
    good,_=seeded(Path(td)/'g');install(good,{"next_state_id":"S1","observed_values":TRUE_POST});e,_=prepare(good,'G');rg=via_basis(good,e,'EG')
    stale,_=seeded(Path(td)/'s');install(stale,{"next_state_id":"S1","observed_values":TRUE_POST});e2,_=prepare(stale,'S');stale.invalidate_capability('OBS-OUTCOME',reason='MAP_STALE');rs=via_basis(stale,e2,'ES')
    wrong,_=seeded(Path(td)/'w');install(wrong,{"next_state_id":"S1","observed_values":TRUE_POST});e3,_=prepare(wrong,'W');rw=via_basis(wrong,e3,'EW',scope='UNBOUNDED')
    forged,_=seeded(Path(td)/'f');install(forged,{"next_state_id":"FALSE","observed_values":FALSE_POST});e4,_=prepare(forged,'F');rf=via_basis(forged,e4,'EF')
    raw,_=seeded(Path(td)/'r');e5,_=prepare(raw,'R');rr=raw.record_bounded_action_outcome(e5,Observation('RAW','RAW-BYPASS',f'action-execution:{e5}',{"next_state_id":"FALSE","observed_values":FALSE_POST},authority=Authority.OBSERVATION_ONLY),evidence_id='ER')
    out={'pass':'MS1596_PASS19','good_basis':rg['status'],'stale_dependency':rs['status'],'wrong_scope':rw['status'],'forged_but_current_basis':rf['status'],'legacy_raw_bypass':rr['status'],'result':'BASIS_GATE_CAN_ENFORCE_CURRENTNESS_SCOPE_IF_USED__BUT_FALSELY_QUALIFIED_BASIS_AND_LEGACY_RAW_INGRESS_REMAIN_FALSE_GREEN_PATHS','authority':'RESEARCH_ONLY'}
    Path('research/MS1596_PASS19_BASIS_GATED_OUTCOME_INGRESS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
