from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import (
    _execute_first_and_advance,
    _generated_fixture,
)


def test_model_space_challenge_relevance_does_not_imply_relational_observation_admission():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        advanced = _execute_first_and_advance(
            m, trial, dc, next_state="sx", evidence_id="E-1849-CHALLENGE"
        )
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, advanced, dc)
        assert bearing["status"] == "MODEL_SPACE_CHALLENGE", bearing
        execution_id = advanced.step_records[-1].execution_id
        projected = m.derive_admitted_opaque_transition_sample(execution_id)
        assert projected == {
            "status": "ABSTAIN",
            "reason": "AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED",
            "authority": "NONE",
        }
        assert calls == ["A"]
    finally:
        td.cleanup()
