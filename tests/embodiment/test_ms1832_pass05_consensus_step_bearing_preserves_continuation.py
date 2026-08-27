from microseed.development.epistemic import EpistemicDeficitState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_consensus_matching_actual_step_does_not_request_revisit_and_b_can_be_reearned():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        t2 = _execute_first_and_advance(m, trial, dc, next_state="s1", evidence_id="E-OUT-1832-A")
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, t2, dc)
        assert bearing["status"] == "CONSENSUS_NONDISCRIMINATING", bearing
        assert bearing["revisit_status"] == "ACTION_LIMITED"
        assert m.epistemic_deficits.records[trial.deficit_id].state == EpistemicDeficitState.ACTION_LIMITED
        assert bearing["truth_authority"] == bearing["answer_authority"] == bearing["model_replacement_authority"] == "NONE"
        n2 = m.nominate_endogenous_epistemic_program_step_intent(t2, dc, "FEAS-B", fob("B"), act_ob())
        assert n2["status"] == "ACTION_INTENT_NOMINATED", n2
        assert n2["intent"]["capability_id"] == "B"
        assert calls == ["A"]
    finally:
        td.cleanup()
