from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,EpistemicStatus,Observation,QualificationState,QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}

def install(m):
    m.register_capability(CapabilityContract('OBS','live observation channel',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1629',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('LIVE-BASIS','current observation use basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1629',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='LIVE-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'CURRENT_OBSERVATION_USE_ALLOWED'},operational_scope_id='R2'))
    # This capability is an immutable historical admission claim for one evidence regime.
    # It intentionally does NOT depend on live OBS access; retrospective falsification
    # challenges it directly rather than current channel loss propagating into history.
    m.register_capability(CapabilityContract('HIST-ADMIT','historical evidence admission basis',{}, {},('NO_TRUTH_AUTHORITY','HISTORICAL_ONLY'),(),Authority.DERIVED_READ_ONLY,('MS1629',),'CURRENT',{},query_obligation_id='HIST-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'EVIDENCE_WAS_ADMISSIBLE_AT_ACQUISITION'},operational_scope_id='R2'))

def close(m,eid,i):
    live=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','current observation use',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id=eid)
    obs=m.capabilities.invoke('OBS',QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),execution_id=eid)
    assert live['status']=='CAPABILITY_RESULT' and obs['status']=='CAPABILITY_RESULT'
    o=Observation(f'C-{i}','CAPABILITY:OBS',f'action-execution:{eid}',dict(obs['value']),currentness_basis='LIVE_USE_PLUS_HISTORICAL_ADMISSION_SPLIT',authority=Authority.OBSERVATION_ONLY,lineage=(f'OBS@{m.capabilities.epochs["OBS"]}',f'LIVE-BASIS@{m.capabilities.epochs["LIVE-BASIS"]}',f'HIST-ADMIT@{m.capabilities.epochs["HIST-ADMIT"]}'))
    return m.record_bounded_action_outcome(eid,o,evidence_id=f'E-{i}',evidence_premise_epochs=(('HIST-ADMIT',m.capabilities.epochs['HIST-ADMIT']),))

def holdout(m,c,n=12):
    refs=[]
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs]}
    for i in range(n): refs.append(m.append_evidence(f'H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
    return tuple(refs)

def established():
    td=tempfile.TemporaryDirectory(prefix='ms1629-');m,_=seeded(Path(td.name));install(m)
    for i in range(12):
        eid,_=prepare(m,f'P{i}');assert close(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
    c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY')
    t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c))
    rr=m.qualify_action_outcome_predictive_relation(t);assert rr['status']=='CURRENT_PREDICTIVE_RELATION'
    return td,m,c,rr['relation']['relation_id']

def case(kind):
    td,m,c,rid=established()
    try:
        before=m.action_outcome_predictive_relation_status(rid)
        if kind=='TEMP_ACCESS': m.invalidate_capability('OBS',reason='TEMP_ACCESS_LOSS')
        elif kind=='PROSPECTIVE_MAPPING': m.capabilities.change_dependency('OBS',reason='NEW_MAPPING_EPOCH')
        elif kind=='RETRO_FALSE': m.invalidate_capability('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_FALSIFIED')
        else: raise ValueError(kind)
        after=m.action_outcome_predictive_relation_status(rid)
        future_obs=m.capabilities.invoke('OBS',QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),execution_id='FUTURE')
        live=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','current observation use',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id='FUTURE')
        return {'before':before['status'],'after':after['status'],'future_obs':future_obs['status'],'live_basis':live['status'],'candidate_premises':[list(x) for x in c.evidence_premise_epochs]}
    finally: td.cleanup()

def main():
    cases={k:case(k) for k in ('TEMP_ACCESS','PROSPECTIVE_MAPPING','RETRO_FALSE')}
    out={'pass':'MS1629_PASS02','cases':cases,
         'result':'ORDINARY_CAPABILITY_SPLIT_SEPARATES_HISTORICAL_ADMISSION_VALIDITY_FROM_LIVE_OBSERVATION_ACCESS',
         'survivor':'HISTORICAL_ADMISSION_BASIS_AS_ORDINARY_DERIVED_CAPABILITY__LIVE_USE_BASIS_SEPARATE',
         'nonclaim':'historical admission basis is externally qualified in this fixture; grounding is not solved',
         'next':'TEST_FRESH_REQUALIFICATION_DEBT_USING_EXISTING_EVIDENCE_PREMISE_GROUPING_AND_HOLDOUT_MATCHING',
         'authority':'RESEARCH_ONLY'}
    Path('research/MS1629_PASS02_SPLIT_HISTORICAL_ADMISSION_BASIS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
