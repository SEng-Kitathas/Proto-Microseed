from __future__ import annotations
from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob


def test_current_observation_in_different_operational_scope_is_rejected_after_pass12_repair():
    td,m,calls,w,t,dc=fixture()
    try:
        m.register_capability(CapabilityContract('OBS-X','obs-other-scope',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1758',),'CURRENT',{},query_obligation_id='OBS-X-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'next_state_id':'wrong-scope-state'},operational_scope_id='OTHER'))
        m.register_capability(CapabilityContract('BASIS-X','basis-other-scope',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1758',),'CURRENT',{},dependencies=('OBS-X',),query_obligation_id='BASIS-X-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='OTHER'))
        n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); assert e['status']=='ACTION_EXECUTED'
        eid=e['execution']['execution_id']
        r=m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS-X',observation_obligation=QueryObligation('OBS-X-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='OTHER'),basis_capability_id='BASIS-X',basis_obligation=QueryObligation('BASIS-X-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='OTHER'),evidence_id='E-X',capture_id='C-X')
        assert r=={'status':'OUTCOME_REJECTED','reason':'OBSERVATION_ACTION_SCOPE_MISMATCH'}
        assert not m.action_closure.outcomes
        assert m.action_closure.current_state.state_id!='wrong-scope-state'
    finally: td.cleanup()
