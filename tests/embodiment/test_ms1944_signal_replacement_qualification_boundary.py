from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import EpistemicStatus, ExternalActionOutcomeRelationQualifier

from tests.embodiment.test_ms1940_opaque_signaling_by_composition import (
    _act_obligation,
    _options,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _reset_start
from tests.embodiment.test_ms1943_signal_predictive_currentness import (
    CFG,
    _coord_subject,
    _execute,
    _finish,
    _fresh,
)


def _fresh_holdout_refs(ms, candidate, n: int = 12):
    refs = []
    base = {
        "kind": "ACTION_OUTCOME_HOLDOUT",
        "start_state_id": candidate.start_state_id,
        "capability_id": candidate.capability_id,
        "capability_epoch": candidate.capability_epoch,
        "frame_epochs": [list(x) for x in candidate.frame_epochs],
        "episode_schema_epochs": [list(x) for x in candidate.episode_schema_epochs],
        "value_epoch": list(candidate.value_epoch),
        "topology_epochs": [list(x) for x in candidate.topology_epochs],
        "coordination_epochs": [list(x) for x in candidate.coordination_epochs],
        "evidence_premise_epochs": [list(x) for x in candidate.evidence_premise_epochs],
        "evidence_premise_signatures": [list(x) for x in candidate.evidence_premise_signatures],
    }
    for i in range(n):
        refs.append(
            ms.append_evidence(
                f"MS1944-HOLDOUT-{i}",
                {
                    **base,
                    "actual_next_state_id": "CP-NOACK",
                    "actual_value_effect": 0.0,
                    "holdout_index": i,
                },
                EpistemicStatus.PRESSURE_SUPPORTED,
                source="EXTERNAL-HOLDOUT",
            )
        )
    return tuple(refs)


def _drift_and_qualify_replacement(ms, world, old_relation_id, proposal):
    coord_before = _coord_subject(ms)
    for i in range(16):
        _execute(ms, world, proposal, i, expected="T1", prefix="MS1944-DRIFT")

    witness = ms.assess_action_outcome_predictive_currentness(old_relation_id, config=CFG)
    assert witness["status"] == "DRIFT_WITNESS"
    assert witness["model_switch_authority"] == "NONE"
    assert witness["semantic_regime_authority"] == "NONE"

    candidates = ms.nominate_action_outcome_replacement_candidates(
        old_relation_id,
        witness["witness"]["witness_id"],
    )
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.next_state_id == "CP-NOACK"
    assert candidate.value_effect == 0.0
    assert candidate.support == 16
    assert candidate.consistency == 1.0
    assert candidate.qualification_authority == "NONE"
    assert candidate.truth_authority == "NONE"
    assert candidate.causal_theorem_authority == "NONE"

    refs = _fresh_holdout_refs(ms, candidate)
    ticket = ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(
        candidate,
        qualification_evidence=refs,
    )
    qualified = ms.qualify_action_outcome_predictive_relation(ticket)
    assert qualified["status"] == "CURRENT_PREDICTIVE_RELATION"
    assert qualified["replacement_of"] == old_relation_id
    replacement_id = qualified["relation"]["relation_id"]

    assert ms.action_outcome_predictive_relation_status(old_relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
    assert ms.action_outcome_predictive_relation_status(replacement_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
    assert _coord_subject(ms) == coord_before
    return replacement_id, coord_before


def test_fresh_signal_replacement_qualification_does_not_rewrite_coordination_or_reactivate_old_model():
    td, ms, world, old_relation_id, proposal = _fresh()
    try:
        replacement_id, coord_before = _drift_and_qualify_replacement(
            ms, world, old_relation_id, proposal
        )
        assert replacement_id != old_relation_id
        assert _coord_subject(ms) == coord_before
        assert ms.action_outcome_predictive_relation_status(old_relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
        assert ms.action_outcome_predictive_relation_status(replacement_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        assert ms.action_outcome_learning.replacement_links
        assert ms.action_outcome_learning_status()["model_switch_authority"] == "NONE"
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)


def test_qualified_zero_benefit_signal_replacement_can_reenter_rehearsal_but_not_action_indication():
    td, ms, world, old_relation_id, proposal = _fresh()
    try:
        _drift_and_qualify_replacement(ms, world, old_relation_id, proposal)
        _reset_start(ms, world, 1944)

        replacement_proposal = ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        )
        assert replacement_proposal is not None
        assert replacement_proposal.sequence == ("SIG-T0",)
        assert replacement_proposal.predicted_state_path == ("S0", "CP-NOACK")
        assert replacement_proposal.predicted_step_value_effects == (0.0,)
        assert replacement_proposal.action_indicated is False
        assert replacement_proposal.action_indication_authority == "NONE"

        commitment = ms.derive_bounded_action_commitment(replacement_proposal.proposal_id)
        assert commitment.commitment.value == "UNKNOWN"
        assert commitment.reason == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"

        intent = ms.nominate_bounded_action_intent(
            replacement_proposal.proposal_id,
            _act_obligation(),
        )
        assert intent["status"] == "ABSTAIN"
        assert intent["reason"] == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        assert intent["execution_authority"] == "NONE"
    finally:
        _finish(td, ms)


def test_signal_replacement_qualification_does_not_gain_semantic_convention_or_auto_switch_authority():
    td, ms, world, old_relation_id, proposal = _fresh()
    try:
        _drift_and_qualify_replacement(ms, world, old_relation_id, proposal)
        status = ms.action_outcome_learning_status()
        assert status["model_switch_authority"] == "NONE"
        assert status["drift_cause_authority"] == "NONE"
        assert status["self_qualification_authority"] == "NONE"
        assert not hasattr(ms, "token_meanings")
        assert not hasattr(ms, "signal_policy")
        assert not hasattr(ms, "auto_switch_action_outcome_relation")
        assert not hasattr(ms, "semantic_convention_registry")
        assert ms.coordinations.is_current("R")
        coord = ms.coordinations.contracts["R"]
        assert coord.semantic_commitment_authority == "NONE"
        assert coord.intention_authority == "NONE"
        assert coord.promise_authority == "NONE"
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)
