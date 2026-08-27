from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_unexpected_actual_state_yields_represented_incomplete_not_deeper_or_replacement_program():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="sx", evidence_id="E-OUT-1829-X")
        assert t2.status == "OPEN" and m.action_closure.current_state.state_id == "sx"

        generated = m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=act_ob())
        assert generated["status"] == "REPRESENTED_REACHABILITY_INCOMPLETE", generated
        assert generated.get("candidates", ()) == ()
        assert generated.get("closure_authority") == "NONE"
        assert generated.get("physical_affordance_closure_authority", "NONE") == "NONE"

        # The old generated word also cannot continue merely because it still contains B,C.
        n2 = m.nominate_endogenous_epistemic_program_step_intent(t2, dc, "FEAS-B", fob("B"), act_ob())
        assert n2["status"] == "ABSTAIN", n2
        assert calls == ["A"]
    finally:
        td.cleanup()
