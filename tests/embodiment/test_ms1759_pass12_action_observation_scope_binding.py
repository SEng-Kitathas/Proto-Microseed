from __future__ import annotations
from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob


def install(m, scope, calls):
    m.register_capability(CapabilityContract('OBS-X','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1759',),'CURRENT',{},query_obligation_id='OBS-X-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:calls.append('OBS') or {'next_state_id':'seen'},operational_scope_id=scope))
    m.register_capability(CapabilityContract('BASIS-X','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1759',),'CURRENT',{},dependencies=('OBS-X',),query_obligation_id='BASIS-X-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:calls.append('BASIS') or {'claim':'LIVE'},operational_scope_id=scope))

def close(m,eid,scope):
    return m.record_bounded_action_outcome_via_observation_basis(eid,observation_capability_id='OBS-X',observation_obligation=QueryObligation('OBS-X-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id=scope),basis_capability_id='BASIS-X',basis_obligation=QueryObligation('BASIS-X-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id=scope),evidence_id='E-X',capture_id='C-X')

def test_cross_scope_rejected_before_observation_or_basis_invocation():
    td,m,action_calls,w,t,dc=fixture(); obs_calls=[]
    try:
        install(m,'OTHER',obs_calls); n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        r=close(m,eid,'OTHER')
        assert r=={'status':'OUTCOME_REJECTED','reason':'OBSERVATION_ACTION_SCOPE_MISMATCH'}
        assert obs_calls==[] and not m.action_closure.outcomes
    finally: td.cleanup()

def test_same_scope_still_closes_outcome():
    td,m,action_calls,w,t,dc=fixture(); obs_calls=[]
    try:
        install(m,'S',obs_calls); n=nominate(m,t,dc); e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); eid=e['execution']['execution_id']
        r=close(m,eid,'S')
        assert r['status']=='ACTION_OUTCOME_OBSERVED' and obs_calls==['BASIS','OBS']
    finally: td.cleanup()
