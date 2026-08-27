from __future__ import annotations
import tempfile
from pathlib import Path

from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob
from tests.embodiment.test_ms1754_pass07_relational_discovery_from_admitted_history import build_world, add_transition


def install_observation(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1756',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'next_state_id':'s1'},operational_scope_id='S'))
    m.register_capability(CapabilityContract('BASIS','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1756',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='BASIS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='S'))
    m.frames.bind_capability('F','A'); m.frames.bind_capability('F','OBS')


def test_actual_ordinary_executor_event_allows_transition_projection():
    td,m,calls,w,t,dc=fixture()
    try:
        install_observation(m)
        n=nominate(m,t,dc); assert n['status']=='ACTION_INTENT_NOMINATED'
        e=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc)); assert e['status']=='ACTION_EXECUTED'
        eid=e['execution']['execution_id']
        r=m.record_bounded_action_outcome_via_observation_basis(
            eid,observation_capability_id='OBS',observation_obligation=QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
            basis_capability_id='BASIS',basis_obligation=QueryObligation('BASIS-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),evidence_id='E-OUT',capture_id='C-OUT')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        p=m.derive_admitted_opaque_transition_sample(eid)
        assert p['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        assert p['sample'].action_token=='A' and p['sample'].start_token=='s0' and p['sample'].end_token=='s1'
    finally: td.cleanup()


def test_injected_closure_execution_without_durable_executor_event_is_rejected():
    with tempfile.TemporaryDirectory(prefix='ms1756-injected-') as td:
        m,outcomes=build_world(Path(td)); add_transition(m,outcomes,0,'s0','A','m0')
        assert m.derive_admitted_opaque_transition_sample('X-0')=={'status':'ABSTAIN','reason':'AUTHENTICATED_ORDINARY_EXECUTION_REQUIRED','authority':'NONE'}
