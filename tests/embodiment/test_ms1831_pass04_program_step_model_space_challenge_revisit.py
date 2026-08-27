from microseed.development.epistemic import EpistemicDeficitState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_off_model_actual_program_step_requests_revisit_without_replacement_or_answer_authority():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="sx", evidence_id="E-OUT-1831-X")
        result = m.assess_epistemic_program_step_outcome_bearing(trial, t2, dc)
        assert result["status"] == "MODEL_SPACE_CHALLENGE", result
        assert result["revisit_status"] == "REVISIT_REQUIRED"
        assert m.epistemic_deficits.records[trial.deficit_id].state == EpistemicDeficitState.REVISIT_REQUIRED
        assert result["truth_authority"] == result["answer_authority"] == result["model_replacement_authority"] == "NONE"
        assert result["witness"]["actual_next_state_id"] == "sx"
        assert set(result["witness"]["represented_next_states"]) == {"s1"}
        # Revisit kills continuation pressure; it does not invent a replacement program/action.
        n2 = m.nominate_endogenous_epistemic_program_step_intent(t2, dc, "FEAS-B", fob("B"), act_ob())
        assert n2["status"] == "ABSTAIN", n2
        assert calls == ["A"]
    finally:
        td.cleanup()
