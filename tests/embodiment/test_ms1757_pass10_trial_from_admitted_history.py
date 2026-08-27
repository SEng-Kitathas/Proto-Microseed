from __future__ import annotations

from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob


def install_history_surface(m):
    m.register_capability(CapabilityContract('C','opaque',{}, {},(),(),Authority.EFFECT,('MS1757',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'receipt':'C'},operational_scope_id='S'))
    outcomes={}
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1757',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_:{'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1757',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='S'))
    for cid in ('A','B','C','OBS'): m.frames.bind_capability('F',cid)
    return outcomes


def add_history_transition(m,outcomes,idx,start,action,end):
    cmt=RelationalCommitment(f'HCM-{idx}',f'action:{action}',TernaryCommitment.YES,reason='HISTORICAL_EXECUTION_RECORD')
    intent=BoundedActionIntent(intent_id=f'HI-{idx}',proposal_id=f'HT-{idx}',proposal_digest='e'*64,action_commitment=cmt,capability_id=action,capability_epoch=0,start_state_id=start,control_state_evidence_id=f'HCS-{idx}',expected_next_state_id=None,expected_value_effect=None,value_epoch=None,obligation_id='Q',operational_scope_id='S',basis_kind='EPISTEMIC_PROGRAM_STEP')
    ex=ActionExecutionRecord(f'HX-{idx}',intent.intent_id,action,0,start,'h'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex)
    # Exact event shape emitted by the already-tested ordinary executor (Pass 9).
    m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable())
    outcomes[ex.execution_id]=end
    r=m.record_bounded_action_outcome_via_observation_basis(ex.execution_id,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),evidence_id=f'HE-{idx}',capture_id=f'HC-{idx}')
    assert r['status']=='ACTION_OUTCOME_OBSERVED'


def test_trial_instantiation_can_consume_admitted_history_without_sample_argument():
    td,m,calls,world,t,dc=fixture()
    try:
        outcomes=install_history_surface(m)
        rows=(('s0','A','m0'),('m0','B','e0'),('s0','C','e0'),('s1','A','m1'),('m1','B','e1'),('s1','C','e1'))
        for idx,row in enumerate(rows): add_history_transition(m,outcomes,idx,*row)
        m.observe_opaque_control_state(Observation('CS-RESET','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-RESET')
        r=m.discover_and_arbitrate_endogenous_epistemic_trial_from_admitted_history(deficit_id='D',decision_context=dc,obligation=act_ob())
        assert r['candidate_surface_count']>=1 and r['admitted_sample_count']==6
        assert r['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        assert r['trial'].steps==('A','B')
        assert r['sample_provenance_authority']=='AUTHENTICATED_ORDINARY_EXECUTION_PLUS_BOUNDED_OBSERVATION_INGRESS'
        assert r['physical_truth_authority']==r['evidence_independence_authority']=='NONE'
        assert calls==[]
    finally: td.cleanup()
