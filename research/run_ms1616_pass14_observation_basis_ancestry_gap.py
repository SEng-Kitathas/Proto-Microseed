from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,EpistemicStatus,QualificationState,QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}

def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1616',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1616',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='R2'))

def call(m,eid,i):
    return m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',required_authority=Authority.OBSERVATION_ONLY,operational_scope_id='R2'),basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),evidence_id=f'E-O-{i}',capture_id=f'C-{i}')

def holdout(m,c,n=12):
    refs=[]
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs]}
    for i in range(n):
        refs.append(m.append_evidence(f'H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HOLDOUT'))
    return tuple(refs)

def main():
  with tempfile.TemporaryDirectory(prefix='ms1616-') as td:
    m,_=seeded(Path(td));install(m)
    for i in range(12):
        eid,_=prepare(m,f'B{i}');r=call(m,eid,i);assert r['status']=='ACTION_OUTCOME_OBSERVED'
    cands=m.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
    c=next(c for c in cands if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY')
    t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c))
    q=m.qualify_action_outcome_predictive_relation(t); rid=q['relation']['relation_id']; before=m.action_outcome_predictive_relation_status(rid)
    stale=sorted(m.invalidate_capability('BASIS',reason='ACTUAL_EVENT_BINDING_CHALLENGED'))
    after=m.action_outcome_predictive_relation_status(rid)
    ev=m.evidence.get(c.source_evidence_ids[0])['payload']
  out={'pass':'MS1616_PASS14','source_outcome_observation_lineage':ev.get('observation_lineage'),'relation_status_before':before,'basis_stale_closure':stale,'relation_status_after_basis_challenge':after,
       'candidate_fields_include_observation_basis':False,
       'result':'OBSERVATION_BASIS_ANCESTRY_IS_PERSISTED_IN_EVIDENCE_BUT_DROPPED_BEFORE_ACTION_OUTCOME_RELATION_CURRENTNESS__DOWNSTREAM_RELATION_REMAINS_CURRENT_AFTER_BINDING_CHALLENGE','scar':'PERSISTED_ANCESTRY != CURRENTNESS_DEPENDENCY','authority':'RESEARCH_ONLY'}
  Path('research/MS1616_PASS14_OBSERVATION_BASIS_ANCESTRY_GAP.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
