from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import (
    _execute_first_and_advance,
    _generated_fixture,
)


def _surface_digest(surface):
    return tuple(
        tuple(rel.digest() for rel in rows)
        for rows in surface.get("relation_sets", ())
    )


def test_revisit_model_space_challenge_does_not_currently_revise_owned_alternative_surface():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        before = m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        before_digest = _surface_digest(before)
        before_experiences = tuple((x.evidence_id, x.execution_id) for x in m._action_outcome_experiences())

        advanced = _execute_first_and_advance(
            m, trial, dc, next_state="sx", evidence_id="E-1848-CHALLENGE"
        )
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, advanced, dc)
        assert bearing["status"] == "MODEL_SPACE_CHALLENGE", bearing
        assert bearing["revisit_status"] == "REVISIT_REQUIRED", bearing

        after = m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        after_digest = _surface_digest(after)
        after_experiences = tuple((x.evidence_id, x.execution_id) for x in m._action_outcome_experiences())

        # The challenge is real developmental pressure, but the state-only epistemic
        # outcome is deliberately not a value-bearing ActionOutcomeExperience and no
        # existing owner silently revises the model surface from it.
        assert "E-1848-CHALLENGE" in m.epistemic_deficits.records[trial.deficit_id].relevant_evidence_ids
        assert all(eid != "E-1848-CHALLENGE" for eid, _ in after_experiences)
        assert after_experiences == before_experiences
        assert after_digest == before_digest
        assert m.epistemic_deficits.records[trial.deficit_id].state.value == "REVISIT_REQUIRED"
        assert not hasattr(m, "revisit_manager")
        assert not hasattr(m, "world_model_manager")
        assert calls == ["A"]
    finally:
        td.cleanup()
