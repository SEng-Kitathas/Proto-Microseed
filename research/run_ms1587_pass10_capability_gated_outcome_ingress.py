from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,Microseed,Observation,QualificationState,QueryObligation
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

FALSE_POST={"ENERGY":4.6,"THERMAL":8.3,"INTEGRITY":5.1}
TRUE_POST={"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}

def install_channel(m:Microseed,payload:dict):
    m.register_capability(CapabilityContract('OBS-OUTCOME','outcome observation channel',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1587-P10',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(payload),operational_scope_id='R2'))

def via_channel(m,execution_id,obligation,evidence_id):
    got=m.capabilities.invoke('OBS-OUTCOME',obligation)
    if got.get('status')!='CAPABILITY_RESULT' or got.get('authority')!=Authority.OBSERVATION_ONLY.value:
        return {'status':'OUTCOME_REJECTED','reason':'OBSERVATION_CAPABILITY_NOT_USABLE','channel_result':got}
    obs=Observation('CAPTURE-'+evidence_id,'OBS-OUTCOME',f'action-execution:{execution_id}',got['value'],authority=Authority.OBSERVATION_ONLY,lineage=(f'CAPABILITY:OBS-OUTCOME@{m.capabilities.epochs["OBS-OUTCOME"]}',))
    return m.record_bounded_action_outcome(execution_id,obs,evidence_id=evidence_id)

def main():
  with tempfile.TemporaryDirectory(prefix='ms1587-p10-') as td:
    q=QueryObligation('OBS-Q','observe outcome',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2')
    m,_=seeded(Path(td)/'good'); install_channel(m,{"next_state_id":"TRUE-NEXT","observed_values":TRUE_POST}); ex,_=prepare(m,'GOOD'); good=via_channel(m,ex,q,'E-GOOD')
    m2,_=seeded(Path(td)/'stale'); install_channel(m2,{"next_state_id":"TRUE-NEXT","observed_values":TRUE_POST}); ex2,_=prepare(m2,'STALE'); m2.invalidate_capability('OBS-OUTCOME',reason='CHANNEL_CHALLENGED'); stale=via_channel(m2,ex2,q,'E-STALE')
    m3,_=seeded(Path(td)/'scope'); install_channel(m3,{"next_state_id":"TRUE-NEXT","observed_values":TRUE_POST}); ex3,_=prepare(m3,'SCOPE'); wrong=via_channel(m3,ex3,QueryObligation('OBS-Q','observe outcome',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='OTHER'),'E-SCOPE')
    m4,_=seeded(Path(td)/'false'); install_channel(m4,{"next_state_id":"FALSE-NEXT","observed_values":FALSE_POST}); ex4,_=prepare(m4,'FALSE'); false=via_channel(m4,ex4,q,'E-FALSE')
    out={'pass':'MS1587_PASS10','current_channel':good['status'],'stale_channel':stale,'wrong_scope':wrong,'current_but_wrong_mapping':false['status'],'false_mapping_learned_values':false.get('outcome',{}).get('value_outcomes',[]),'result':'CAPABILITY_GATED_INGRESS_COMPOSES_CURRENTNESS_QUERY_SCOPE__BUT_CURRENT_WRONG_MAPPING_STILL_FALSE_GREENS','authority':'RESEARCH_ONLY'}
    Path('research/MS1587_PASS10_CAPABILITY_GATED_OUTCOME_INGRESS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
