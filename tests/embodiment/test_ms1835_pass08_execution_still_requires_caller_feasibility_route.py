from microseed.development.epistemic_action import EpistemicStepExecutionContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_route_free_generated_step_can_reauthorize_at_effect_boundary_without_caller_route_selection():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state='s1', evidence_id='E-OUT-1835-A')
        m.assess_epistemic_program_step_outcome_bearing(trial, t2, dc)
        n2 = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(t2, dc, act_ob())
        assert n2['status']=='ACTION_INTENT_NOMINATED', n2
        ctx = EpistemicStepExecutionContext(t2, decision_context=dc)
        ex2 = m.execute_bounded_action(n2['intent']['intent_id'], act_ob(), epistemic_step_context=ctx)
        assert ex2['status']=='ACTION_EXECUTED', ex2
        assert calls==['A','B']
    finally:
        td.cleanup()
