from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import (
    Authority,
    EpistemicStatus,
    ExternalActionOutcomeRelationQualifier,
    Observation,
)
from microseed.development.rehearsal import (
    CounterfactualRehearsalConfig,
    CounterfactualRehearsalProposal,
    RehearsalTransitionRelation,
    propose_counterfactual_rehearsal,
)

from tests.embodiment.test_ms1940_opaque_signaling_by_composition import (
    _act_obligation,
    _basis_obligation,
    _build,
    _close,
    _obs_obligation,
    _options,
    _proposal,
)


LEGACY_PROPOSAL_DIGEST = "22741c348c8efe347201c9e98fe27e4c21a0076ec2cba6f14338ff9fb093b8f7"


def _reset_start(ms, world, index: int) -> None:
    world["emitted"] = None
    ms.observe_value_state("V", 0.0)
    ms.observe_opaque_control_state(
        Observation(
            f"MS1941-RESET-{index}", "EXT", "opaque-control", "S0",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-MS1941-RESET-{index}",
    )


def _holdout_refs(ms, candidate, n: int = 20):
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
                f"MS1941-HOLDOUT-{i}",
                {
                    **base,
                    "actual_next_state_id": "CP-ACK",
                    "actual_value_effect": 2.2,
                    "holdout_index": i,
                },
                EpistemicStatus.PRESSURE_SUPPORTED,
                source="EXTERNAL-HOLDOUT",
            )
        )
    return tuple(refs)


def _learn_and_qualify(ms, world):
    seed_proposal = _proposal(ms)
    for i in range(12):
        if i:
            _reset_start(ms, world, i)
        intent = ms.nominate_bounded_action_intent(seed_proposal.proposal_id, _act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED"
        execution = ms.execute_bounded_action(intent["intent"]["intent_id"], _act_obligation())
        assert execution["status"] == "ACTION_EXECUTED"
        result = ms.record_bounded_action_outcome_via_observation_basis(
            execution["execution"]["execution_id"],
            observation_capability_id="OBS-CP",
            observation_obligation=_obs_obligation(),
            basis_capability_id="OBS-BASIS",
            basis_obligation=_basis_obligation(),
            evidence_id=f"E-MS1941-OUT-{i}",
            capture_id=f"CAP-MS1941-OUT-{i}",
        )
        assert result["status"] == "ACTION_OUTCOME_OBSERVED"
        assert result["outcome"]["actual_next_state_id"] == "CP-ACK"

    candidates = ms.nominate_action_outcome_predictive_candidates()
    target = [
        c for c in candidates
        if c.capability_id == "SIG-T0" and c.next_state_id == "CP-ACK"
    ]
    assert len(target) == 1
    candidate = target[0]
    assert candidate.support == 12
    assert candidate.consistency == 1.0
    assert candidate.coordination_epochs == (("R", 0),)
    assert candidate.evidence_premise_epochs == (("OBS-BASIS", 0),)
    assert candidate.truth_authority == "NONE"
    assert candidate.causal_theorem_authority == "NONE"
    assert candidate.qualification_authority == "NONE"

    refs = _holdout_refs(ms, candidate)
    ticket = ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(
        candidate, qualification_evidence=refs
    )
    qualified = ms.qualify_action_outcome_predictive_relation(ticket)
    assert qualified["status"] == "CURRENT_PREDICTIVE_RELATION"
    relation_id = qualified["relation"]["relation_id"]
    relation = ms.action_outcome_learning.relations[relation_id]
    assert relation.evidence_premise_epochs == candidate.evidence_premise_epochs
    assert relation.evidence_premise_signatures == candidate.evidence_premise_signatures
    assert relation.truth_authority == relation.causal_theorem_authority == "NONE"
    assert relation.execution_authority == relation.semantic_goal_authority == "NONE"
    return candidate, relation_id


def _learned_rehearsal(ms, world):
    _reset_start(ms, world, 100)
    proposal = ms.nominate_counterfactual_rehearsal(
        (), _options(), start_state_id="S0", value_id="V"
    )
    assert proposal is not None
    assert proposal.sequence == ("SIG-T0",)
    assert proposal.predicted_state_path == ("S0", "CP-ACK")
    assert proposal.predicted_step_value_effects == (2.2,)
    assert proposal.evidence_premise_epochs == (("OBS-BASIS", 0),)
    assert proposal.truth_authority == proposal.execution_authority == "NONE"
    assert proposal.qualification_authority == proposal.semantic_goal_authority == "NONE"
    return proposal


def test_learned_signal_response_reenters_ordinary_rehearsal_without_supplied_transition_rows():
    with tempfile.TemporaryDirectory(prefix="ms1941-learned-signal-") as td:
        ms, world = _build(Path(td))
        try:
            _, relation_id = _learn_and_qualify(ms, world)
            proposal = _learned_rehearsal(ms, world)
            assert ms.counterfactual_rehearsal_status(proposal.proposal_id)["status"] == "CURRENT_REHEARSAL_PROPOSAL"
            assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
            assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        finally:
            _close(ms)


def test_coordination_drift_stales_learned_relation_and_removes_zero_row_rehearsal():
    with tempfile.TemporaryDirectory(prefix="ms1941-coord-drift-") as td:
        ms, world = _build(Path(td))
        try:
            _, relation_id = _learn_and_qualify(ms, world)
            proposal = _learned_rehearsal(ms, world)
            stale = ms.change_operational_coordination("R", reason="MS1941_CONVENTION_DRIFT")
            assert "SIG-T0" in stale
            assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
            status = ms.counterfactual_rehearsal_status(proposal.proposal_id)
            assert status["status"] == "UNKNOWN_INCOMPLETE"
            assert "REHEARSAL_CAPABILITY_NOT_CURRENT:SIG-T0" == status["reason"]
            assert ms.nominate_counterfactual_rehearsal(
                (), _options(), start_state_id="S0", value_id="V"
            ) is None
        finally:
            _close(ms)


def test_evidence_premise_epoch_drift_stales_durable_learned_rehearsal():
    with tempfile.TemporaryDirectory(prefix="ms1941-premise-epoch-") as td:
        ms, world = _build(Path(td))
        try:
            _, relation_id = _learn_and_qualify(ms, world)
            proposal = _learned_rehearsal(ms, world)
            ms.invalidate_capability("OBS-BASIS", reason="MS1941_OBSERVATION_USE_BASIS_CHALLENGED")
            assert ms.action_outcome_predictive_relation_status(relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
            status = ms.counterfactual_rehearsal_status(proposal.proposal_id)
            assert status["status"] == "UNKNOWN_INCOMPLETE"
            assert status["reason"] == "REHEARSAL_EVIDENCE_PREMISE_NOT_CURRENT:OBS-BASIS"
        finally:
            _close(ms)


def test_explicit_evidence_premise_signature_drift_stales_durable_proposal_without_epoch_change():
    with tempfile.TemporaryDirectory(prefix="ms1941-premise-signature-") as td:
        ms, _ = _build(Path(td))
        try:
            signature = ms.capabilities.contracts["OBS-BASIS"].computed_signature_sha256()
            relation = RehearsalTransitionRelation(
                "S0", "SIG-T0", "CP-ACK", 2.2, 12, 1.0, ("E-SIG",), 0,
                ("F", 0), ("E", 0), coordination_epoch=("R", 0),
                evidence_premise_epochs=(("OBS-BASIS", 0),),
                evidence_premise_signatures=(("OBS-BASIS", signature),),
                value_epoch=("V", 0),
            )
            proposal = propose_counterfactual_rehearsal(
                {("S0", "SIG-T0"): relation},
                start_state_id="S0", start_value=0.0, viable_low=2.0, viable_high=3.0,
                value_epoch=("V", 0), options=_options(),
                cfg=CounterfactualRehearsalConfig(max_horizon=1),
            )
            assert proposal is not None
            assert proposal.evidence_premise_signatures == (("OBS-BASIS", signature),)
            ms.counterfactual_rehearsals.add(proposal)
            assert ms.counterfactual_rehearsal_status(proposal.proposal_id)["status"] == "CURRENT_REHEARSAL_PROPOSAL"

            before_epoch = ms.capabilities.epochs["OBS-BASIS"]
            ms.capabilities.contracts["OBS-BASIS"].purpose = "mutated-bounded-use-basis"
            assert ms.capabilities.epochs["OBS-BASIS"] == before_epoch
            status = ms.counterfactual_rehearsal_status(proposal.proposal_id)
            assert status["status"] == "UNKNOWN_INCOMPLETE"
            assert status["reason"] == "REHEARSAL_EVIDENCE_PREMISE_SIGNATURE_DRIFT:OBS-BASIS"
        finally:
            _close(ms)


def test_legacy_empty_ancestry_proposal_digest_is_unchanged_by_ms1941_carrier_extension():
    proposal = CounterfactualRehearsalProposal(
        proposal_id="P",
        start_state_id="S0",
        sequence=("A",),
        final_state_id="S1",
        predicted_value_effect=1.0,
        predicted_final_value=1.0,
        residual_pressure=0.0,
        transition_relation_digests=("d",),
        source_evidence_ids=("E",),
        capability_epochs=(("A", 0),),
        frame_epochs=(("F", 0),),
        episode_schema_epochs=(("EP", 0),),
        value_epoch=("V", 0),
        topology_epochs=(),
        coordination_epochs=(),
        predicted_state_path=("S0", "S1"),
        predicted_step_value_effects=(1.0,),
        assistance_ancestry=(),
        nodes_expanded=1,
    )
    assert proposal.evidence_premise_epochs == ()
    assert proposal.evidence_premise_signatures == ()
    assert proposal.digest() == LEGACY_PROPOSAL_DIGEST
