from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_next_generated_step_can_be_nominated_without_caller_selecting_feasibility_route():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="s1", evidence_id="E-OUT-1833-A")
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, t2, dc)
        assert bearing["status"] == "CONSENSUS_NONDISCRIMINATING"
        n2 = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(t2, dc, act_ob())
        assert n2["status"] == "ACTION_INTENT_NOMINATED", n2
        assert n2["intent"]["capability_id"] == "B"
        assert n2["feasibility_basis"]["status"] == "CURRENT_BOUNDED_FEASIBILITY_SURFACE"
        assert n2["feasibility_basis"]["route_ids"] == ("FEAS-B",)
        assert calls == ["A"]
    finally:
        td.cleanup()
