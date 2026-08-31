from __future__ import annotations

import tempfile
from pathlib import Path

from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig

from tests.embodiment.test_ms1940_opaque_signaling_by_composition import (
    _act_obligation,
    _basis_obligation,
    _build,
    _close,
    _obs_obligation,
    _options,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import (
    _learn_and_qualify,
    _learned_rehearsal,
    _reset_start,
)


CFG = PredictiveCurrentnessConfig(
    window_size=8,
    min_accuracy=0.75,
    consecutive_failure_windows=2,
)


def _coord_subject(ms):
    contract = ms.coordinations.contracts["R"]
    return (
        ms.coordinations.epochs["R"],
        ms.coordinations.is_current("R"),
        contract.signature_sha256,
        contract.computed_signature_sha256(),
        contract.purpose,
        contract.participant_counterparty_epochs,
        contract.invariants,
    )


def _fresh():
    td = tempfile.TemporaryDirectory(prefix="ms1943-signal-currentness-")
    ms, world = _build(Path(td.name))
    _, relation_id = _learn_and_qualify(ms, world)
    proposal = _learned_rehearsal(ms, world)
    return td, ms, world, relation_id, proposal


def _finish(td, ms):
    _close(ms)
    td.cleanup()


def _execute(ms, world, proposal, index: int, *, expected: str, prefix: str):
    _reset_start(ms, world, 2000 + index)
    world["expected"] = expected
    intent = ms.nominate_bounded_action_intent(proposal.proposal_id, _act_obligation())
    assert intent["status"] == "ACTION_INTENT_NOMINATED"
    executed = ms.execute_bounded_action(intent["intent"]["intent_id"], _act_obligation())
    assert executed["status"] == "ACTION_EXECUTED"
    outcome = ms.record_bounded_action_outcome_via_observation_basis(
        executed["execution"]["execution_id"],
        observation_capability_id="OBS-CP",
        observation_obligation=_obs_obligation(),
        basis_capability_id="OBS-BASIS",
        basis_obligation=_basis_obligation(),
        evidence_id=f"E-MS1943-{prefix}-{index}",
        capture_id=f"CAP-MS1943-{prefix}-{index}",
    )
    assert outcome["status"] == "ACTION_OUTCOME_OBSERVED"
    return outcome


def test_isolated_signal_prediction_miss_is_tolerated_without_coordination_drift():
    td, ms, world, relation_id, proposal = _fresh()
    try:
        coord_before = _coord_subject(ms)
        _execute(ms, world, proposal, 0, expected="T1", prefix="ISO")
        for i in range(1, 8):
            _execute(ms, world, proposal, i, expected="T0", prefix="ISO")

        witness = ms.assess_action_outcome_predictive_currentness(relation_id, config=CFG)
        assert witness["status"] == "CURRENT_WITHIN_BOUNDS"
        assert witness["witness"]["window_accuracies"] == [0.875]
        assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        assert _coord_subject(ms) == coord_before
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)


def test_transient_bad_signal_window_then_recovery_does_not_become_convention_change():
    td, ms, world, relation_id, proposal = _fresh()
    try:
        coord_before = _coord_subject(ms)
        for i in range(8):
            _execute(ms, world, proposal, i, expected="T1", prefix="BAD")
        for i in range(8, 16):
            _execute(ms, world, proposal, i, expected="T0", prefix="REC")

        witness = ms.assess_action_outcome_predictive_currentness(relation_id, config=CFG)
        assert witness["status"] == "CURRENT_WITHIN_BOUNDS"
        assert witness["witness"]["window_accuracies"] == [0.0, 1.0]
        assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        assert _coord_subject(ms) == coord_before
        assert world["expected"] == "T0"
        assert not hasattr(ms, "token_meanings")
    finally:
        _finish(td, ms)


def test_sustained_signal_prediction_contradiction_stales_model_not_coordination_and_only_nominates_replacement():
    td, ms, world, relation_id, proposal = _fresh()
    try:
        coord_before = _coord_subject(ms)
        for i in range(16):
            _execute(ms, world, proposal, i, expected="T1", prefix="DRIFT")

        witness = ms.assess_action_outcome_predictive_currentness(relation_id, config=CFG)
        assert witness["status"] == "DRIFT_WITNESS"
        assert witness["witness"]["window_accuracies"] == [0.0, 0.0]
        assert witness["model_switch_authority"] == "NONE"
        assert witness["drift_cause_authority"] == "NONE"
        assert witness["semantic_regime_authority"] == "NONE"

        status = ms.action_outcome_predictive_relation_status(relation_id)
        assert status["status"] == "STALE_PREDICTIVE_RELATION"
        assert status["reason"] == "EMPIRICAL_DRIFT_WITNESS"
        assert relation_id in ms.action_outcome_learning.relations

        replacements = ms.nominate_action_outcome_replacement_candidates(
            relation_id,
            witness["witness"]["witness_id"],
        )
        assert len(replacements) == 1
        replacement = replacements[0]
        assert replacement.next_state_id == "CP-NOACK"
        assert replacement.value_effect == 0.0
        assert replacement.support == 16
        assert replacement.consistency == 1.0
        assert replacement.truth_authority == "NONE"
        assert replacement.causal_theorem_authority == "NONE"
        assert replacement.qualification_authority == "NONE"
        link = ms.action_outcome_learning.replacement_links[replacement.candidate_id]
        assert link.replacement_of_relation_id == relation_id
        assert link.qualification_authority == "NONE"
        assert link.model_switch_authority == "NONE"
        assert link.semantic_regime_authority == "NONE"
        assert ms.action_outcome_learning.relation_replacement_lineage == {}

        _reset_start(ms, world, 9000)
        assert ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        ) is None

        assert _coord_subject(ms) == coord_before
        assert world["expected"] == "T1"
        assert not hasattr(ms, "auto_switch_action_outcome_relation")
        assert not hasattr(ms, "signal_policy")
        assert not hasattr(ms, "token_meanings")
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)


def test_recovery_after_empirical_signal_drift_does_not_reactivate_old_model_or_rewrite_coordination():
    td, ms, world, relation_id, proposal = _fresh()
    try:
        coord_before = _coord_subject(ms)
        for i in range(16):
            _execute(ms, world, proposal, i, expected="T1", prefix="DRIFT")
        first = ms.assess_action_outcome_predictive_currentness(relation_id, config=CFG)
        assert first["status"] == "DRIFT_WITNESS"

        # Recovery observations are explicitly assisted.  The stale learned
        # zero-row proposal is no longer a lawful execution premise after the
        # drift witness; reuse the original supplied-row seed proposal that
        # remains in the rehearsal registry from _learn_and_qualify().
        assisted = next(
            p for pid, p in ms.counterfactual_rehearsals.proposals.items()
            if pid != proposal.proposal_id
        )
        assert ms.counterfactual_rehearsal_status(assisted.proposal_id)["status"] == "CURRENT_REHEARSAL_PROPOSAL"
        assert ms.counterfactual_rehearsal_status(proposal.proposal_id)["status"] == "UNKNOWN_INCOMPLETE"
        for i in range(16, 32):
            _execute(ms, world, assisted, i, expected="T0", prefix="REC-ASSISTED")
        recovered = ms.assess_action_outcome_predictive_currentness(relation_id, config=CFG)
        assert recovered["status"] == "DRIFT_WITNESS"
        assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
        assert _coord_subject(ms) == coord_before
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)
