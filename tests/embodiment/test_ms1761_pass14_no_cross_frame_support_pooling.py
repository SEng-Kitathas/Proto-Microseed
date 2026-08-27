from __future__ import annotations

from microseed import Authority, CapabilityContract, OperationalFrameContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture
from tests.embodiment.test_ms1757_pass10_trial_from_admitted_history import install_history_surface


def add_transition(m, outcomes, idx, start, action, end, *, obs_id, basis_id):
    cmt=RelationalCommitment(f'FM-{idx}',f'action:{action}',TernaryCommitment.YES,reason='FRAME_SEPARATION_FIXTURE')
    intent=BoundedActionIntent(
        intent_id=f'FI-{idx}',proposal_id=f'FT-{idx}',proposal_digest='a'*64,
        action_commitment=cmt,capability_id=action,capability_epoch=m.capabilities.epochs[action],
        start_state_id=start,control_state_evidence_id=f'FCS-{idx}',expected_next_state_id=None,
        expected_value_effect=None,value_epoch=None,obligation_id='Q',operational_scope_id='S',
        basis_kind='EPISTEMIC_PROGRAM_STEP')
    ex=ActionExecutionRecord(f'FX-{idx}',intent.intent_id,action,m.capabilities.epochs[action],start,'b'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex); m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable())
    outcomes[ex.execution_id]=end
    r=m.record_bounded_action_outcome_via_observation_basis(
        ex.execution_id,
        observation_capability_id=obs_id,
        observation_obligation=QueryObligation(f'{obs_id}-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id=basis_id,
        basis_obligation=QueryObligation(f'{basis_id}-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=f'FE-{idx}',capture_id=f'FC-{idx}')
    assert r['status']=='ACTION_OUTCOME_OBSERVED'


def test_support_from_distinct_frames_cannot_pool_into_one_relational_candidate():
    td,m,calls,world,t,dc=fixture()
    try:
        outcomes=install_history_surface(m)
        m.register_operational_frame(OperationalFrameContract('F2','opaque-2','2'*64,Authority.DERIVED_READ_ONLY,('MS1761',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
        for cid in ('A','B','C'): m.frames.bind_capability('F2',cid)
        m.register_capability(CapabilityContract('OBS2','obs2',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1761',),'CURRENT',{},query_obligation_id='OBS2-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_:{'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
        m.register_capability(CapabilityContract('BASIS2','basis2',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1761',),'CURRENT',{},dependencies=('OBS2',),query_obligation_id='BASIS2-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='S'))
        m.frames.bind_capability('F2','OBS2')

        # Each frame has only one positive C ~= A->B witness. Pooling them would
        # illegally manufacture the existing relational owner's min support of 2.
        rows_f=(('s0','A','m0'),('m0','B','e0'),('s0','C','e0'))
        rows_f2=(('s1','A','m1'),('m1','B','e1'),('s1','C','e1'))
        for idx,row in enumerate(rows_f): add_transition(m,outcomes,idx,*row,obs_id='OBS',basis_id='BASIS')
        for off,row in enumerate(rows_f2,3): add_transition(m,outcomes,off,*row,obs_id='OBS2',basis_id='BASIS2')

        r=m.discover_admitted_opaque_action_composition_candidates()
        assert r['admitted_sample_count']==6
        assert len(r['frame_groups'])==2
        assert r['candidates']==()
        assert r['truth_authority']==r['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
