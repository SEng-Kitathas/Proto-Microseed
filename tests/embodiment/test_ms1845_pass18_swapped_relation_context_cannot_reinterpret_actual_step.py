from dataclasses import replace

from microseed.development.epistemic_action import EpistemicDecisionBearingContext
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import (
    _execute_first_and_advance,
    _generated_fixture,
)


def _rewrite_first_step(dc, transform):
    rewritten = []
    for rows in dc.relation_sets:
        rewritten.append(tuple(
            transform(rel)
            if rel.state_id == "s0" and rel.capability_id == "A"
            else rel
            for rel in rows
        ))
    return EpistemicDecisionBearingContext(tuple(rewritten), dc.feasibility_routes)


def test_post_execution_path_substitution_cannot_reinterpret_same_actual_step():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        assert {
            rel.next_state_id
            for rows in dc.relation_sets
            for rel in rows
            if rel.state_id == "s0" and rel.capability_id == "A"
        } == {"s1"}
        t2 = _execute_first_and_advance(
            m, trial, dc, next_state="sx", evidence_id="E-OUT-1845-X"
        )

        # Rewriting the first predicted state also destroys the candidate's original
        # represented continuation.  That is ancestry incompleteness, never a new
        # consensus interpretation of the same physical outcome.
        forged = _rewrite_first_step(dc, lambda rel: replace(rel, next_state_id="sx"))
        result = m.assess_epistemic_program_step_outcome_bearing(trial, t2, forged)
        assert result["status"] == "PROGRAM_STEP_BEARING_UNRESOLVED", result
        assert result["reason"] == "PROGRAM_RELATION_ANCESTRY_INCOMPLETE", result
        assert result.get("witness") is None, result
        assert m.epistemic_deficits.records[trial.deficit_id].state.value == "ACTION_LIMITED"
        assert calls == ["A"]
    finally:
        td.cleanup()


def test_post_execution_content_substitution_with_same_path_is_digest_mismatch():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        # Keep the extensional path exactly the same, but mutate evidence-bearing
        # relation content.  The generated candidate digest must bind that ancestry too.
        t2 = _execute_first_and_advance(
            m, trial, dc, next_state="s1", evidence_id="E-OUT-1845-A"
        )
        forged = _rewrite_first_step(dc, lambda rel: replace(rel, support=rel.support + 1))
        result = m.assess_epistemic_program_step_outcome_bearing(trial, t2, forged)
        assert result["status"] == "PROGRAM_STEP_BEARING_UNRESOLVED", result
        assert result["reason"] == "PROGRAM_RELATION_ANCESTRY_MISMATCH", result
        assert result.get("witness") is None, result
        assert m.epistemic_deficits.records[trial.deficit_id].state.value == "ACTION_LIMITED"
        assert calls == ["A"]
    finally:
        td.cleanup()
