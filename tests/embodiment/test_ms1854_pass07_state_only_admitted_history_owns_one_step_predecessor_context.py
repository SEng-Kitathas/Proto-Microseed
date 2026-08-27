from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def _install(m, outcomes):
    m.register_capability(CapabilityContract('P-1854','opaque',{}, {},(),(),Authority.EFFECT,('MS1854',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'receipt':'P'},operational_scope_id='S'))
    m.register_capability(CapabilityContract('OBS-1854','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1854',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda execution_id,**_:{'next_state_id':outcomes[execution_id]},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS-1854','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1854',),'CURRENT',{},dependencies=('OBS-1854',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'BOUND'},operational_scope_id='S'))
    for cid in ('P-1854','A','OBS-1854'): m.frames.bind_capability('F',cid)


def _add(m,outcomes,idx,cap,start,end,control_eid):
    cmt=RelationalCommitment(f'C1854-{idx}',f'action:{cap}',TernaryCommitment.YES,reason='STATE_ONLY_SUCCESSOR_FIXTURE')
    intent=BoundedActionIntent(f'I1854-{idx}',None,None,cmt,cap,0,start,control_eid,None,None,None,'Q','S',basis_kind='EPISTEMIC_PROGRAM_STEP')
    ex=ActionExecutionRecord(f'X1854-{idx}',intent.intent_id,cap,0,start,'a'*64,execution_commitment_id=cmt.commitment_id)
    m.action_closure.add_intent(intent); m.action_closure.add_execution(ex); m.store.append('BOUNDED_ACTION_EXECUTED',ex.serializable())
    outcomes[ex.execution_id]=end
    out=m.record_bounded_action_outcome_via_observation_basis(
        ex.execution_id,observation_capability_id='OBS-1854',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS-1854',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=f'E1854-{idx}',capture_id=f'CAP1854-{idx}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED', out
    return ex.execution_id, out['outcome']['evidence_id']


def test_exact_control_state_evidence_link_recovers_one_step_predecessor_for_state_only_admitted_transition():
    td,m,_,_,_,_=fixture()
    try:
        outcomes={}; _install(m,outcomes)
        first, first_eid=_add(m,outcomes,0,'P-1854','p','s0','ROOT-E')
        second, second_eid=_add(m,outcomes,1,'A','s0','s1',first_eid)
        p1=m.derive_admitted_opaque_transition_sample(first); p2=m.derive_admitted_opaque_transition_sample(second)
        assert p1['status']==p2['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        ex2=m.action_closure.executions[second]; intent2=m.action_closure.intents[ex2.intent_id]
        prior=[o for o in m.action_closure.outcomes.values() if o.evidence_id==intent2.control_state_evidence_id]
        assert len(prior)==1
        prior_ex=m.action_closure.executions[prior[0].execution_id]
        assert prior_ex.execution_id==first
        assert prior_ex.start_state_id=='p' and prior[0].actual_next_state_id=='s0'
        assert p2['sample'].start_token=='s0' and p2['sample'].end_token=='s1'
        # This is observed successor ancestry only, not a semantic episode or hidden-state label.
        assert intent2.control_state_evidence_id==first_eid
        assert not hasattr(m,'episode_manager')
    finally:
        td.cleanup()
