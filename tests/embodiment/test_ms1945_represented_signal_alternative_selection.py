from __future__ import annotations

from microseed import (
    Authority,
    CapabilityContract,
    EpistemicStatus,
    ExternalActionOutcomeRelationQualifier,
    FeasibilityState,
    QualificationState,
    RecruitmentOption,
    RehearsalTransitionObservation,
)
from tests.embodiment.test_ms1940_opaque_signaling_by_composition import _act_obligation
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _reset_start
from tests.embodiment.test_ms1943_signal_predictive_currentness import (
    _coord_subject,
    _execute,
    _finish,
    _fresh,
)
from tests.embodiment.test_ms1944_signal_replacement_qualification_boundary import (
    _drift_and_qualify_replacement,
)


def _register_t1(ms, world) -> None:
    def emit_t1(**_):
        world["emitted"] = "T1"
        return {"opaque_emitted_token": "T1"}

    ms.register_capability(
        CapabilityContract(
            "SIG-T1", "opaque-effect-token-emission", {}, {"output": "opaque-token"},
            (
                "SIGNAL != REFERENCE",
                "TOKEN_EMITTED != TOKEN_MEANS",
                "REPRESENTED_SIGNAL_ALTERNATIVE != TOKEN_MEANING",
                "NO_SEMANTIC_MESSAGE_AUTHORITY",
            ),
            (), Authority.EFFECT, ("MS1945",), "CURRENT", {},
            query_obligation_id="ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=emit_t1, operational_scope_id="S",
            assistance_ancestry=("SUPPLIED_REPRESENTED_OPAQUE_SIGNAL_ALTERNATIVE",),
        ),
        counterparty_dependencies=(("CP", 0),),
        coordination_dependencies=(("R", 0),),
    )


def _option(cid: str) -> RecruitmentOption:
    return RecruitmentOption(cid, FeasibilityState.FEASIBLE, local_cost=0.1)


def _options() -> tuple[RecruitmentOption, ...]:
    return (_option("SIG-T0"), _option("SIG-T1"))


def _t1_seed_rows() -> tuple[RehearsalTransitionObservation, ...]:
    return tuple(
        RehearsalTransitionObservation(
            f"MS1945-T1-SEED-{i}", "S0", "SIG-T1", "CP-ACK", 2.2, 0,
            "F", 0, "E", 0, None, None, "R", 0,
        )
        for i in range(12)
    )


def _holdouts(ms, candidate, n: int = 16):
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
    return tuple(
        ms.append_evidence(
            f"MS1945-T1-HOLDOUT-{i}",
            {
                **base,
                "actual_next_state_id": "CP-ACK",
                "actual_value_effect": 2.2,
                "holdout_index": i,
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXTERNAL-HOLDOUT",
        )
        for i in range(n)
    )


def _prepare_ms1944_plus_represented_t1():
    td, ms, world, old_relation_id, old_t0_proposal = _fresh()
    t0_replacement_id, coord_before = _drift_and_qualify_replacement(
        ms, world, old_relation_id, old_t0_proposal
    )
    assert world["expected"] == "T1"
    _register_t1(ms, world)
    return td, ms, world, t0_replacement_id, coord_before


def _learn_and_qualify_t1(ms, world) -> str:
    seed = ms.nominate_counterfactual_rehearsal(
        _t1_seed_rows(), (_option("SIG-T1"),), start_state_id="S0", value_id="V"
    )
    assert seed is not None and seed.sequence == ("SIG-T1",)
    for i in range(12):
        out = _execute(ms, world, seed, 5000 + i, expected="T1", prefix="T1-TRAIN")
        assert out["outcome"]["actual_next_state_id"] == "CP-ACK"

    candidates = [
        c for c in ms.nominate_action_outcome_predictive_candidates()
        if c.capability_id == "SIG-T1" and c.next_state_id == "CP-ACK"
    ]
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.support == 12
    assert candidate.consistency == 1.0
    ticket = ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(
        candidate, qualification_evidence=_holdouts(ms, candidate)
    )
    qualified = ms.qualify_action_outcome_predictive_relation(ticket)
    assert qualified["status"] == "CURRENT_PREDICTIVE_RELATION"
    return qualified["relation"]["relation_id"]


def test_represented_t1_without_qualified_predictive_model_is_not_selected_or_action_indicated():
    td, ms, world, t0_replacement_id, coord_before = _prepare_ms1944_plus_represented_t1()
    try:
        _reset_start(ms, world, 19450)
        proposal = ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        )
        assert proposal is not None
        assert proposal.sequence == ("SIG-T0",)
        assert proposal.predicted_step_value_effects == (0.0,)
        commitment = ms.derive_bounded_action_commitment(proposal.proposal_id)
        assert commitment.commitment.value == "UNKNOWN"
        assert commitment.reason == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        assert ms.nominate_bounded_action_intent(proposal.proposal_id, _act_obligation())["status"] == "ABSTAIN"
        assert ms.action_outcome_predictive_relation_status(t0_replacement_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        assert _coord_subject(ms) == coord_before
    finally:
        _finish(td, ms)


def test_exact_history_and_qualification_make_zero_row_rehearsal_select_regulatory_useful_t1_without_semantic_policy():
    td, ms, world, _, coord_before = _prepare_ms1944_plus_represented_t1()
    try:
        t1_relation_id = _learn_and_qualify_t1(ms, world)
        _reset_start(ms, world, 19451)
        proposal = ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        )
        assert proposal is not None
        assert proposal.sequence == ("SIG-T1",)
        assert proposal.predicted_state_path == ("S0", "CP-ACK")
        assert proposal.predicted_step_value_effects == (2.2,)
        assert proposal.action_indicated is False
        assert proposal.execution_authority == "NONE"

        commitment = ms.derive_bounded_action_commitment(proposal.proposal_id)
        assert commitment.commitment.value == "YES"
        assert commitment.reason == "BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE"
        assert dict(commitment.qualifiers)["execution_authority"] == "NONE"
        assert dict(commitment.qualifiers)["truth_authority"] == "NONE"

        intent = ms.nominate_bounded_action_intent(proposal.proposal_id, _act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED"
        assert intent["intent"]["capability_id"] == "SIG-T1"
        assert intent["execution_authority"] == "NONE"

        assert ms.action_outcome_predictive_relation_status(t1_relation_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        assert _coord_subject(ms) == coord_before
        assert not hasattr(ms, "token_meanings")
        assert not hasattr(ms, "signal_policy")
        assert not hasattr(ms, "semantic_convention_registry")
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        _finish(td, ms)


def test_t1_currentness_loss_removes_selection_without_persistent_signal_policy():
    td, ms, world, _, coord_before = _prepare_ms1944_plus_represented_t1()
    try:
        _reset_start(ms, world, 19450)
        t0_only = ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        )
        assert t0_only is not None and t0_only.sequence == ("SIG-T0",)

        t1_relation_id = _learn_and_qualify_t1(ms, world)
        _reset_start(ms, world, 19451)
        selected = ms.nominate_counterfactual_rehearsal(
            (), _options(), start_state_id="S0", value_id="V"
        )
        assert selected is not None and selected.sequence == ("SIG-T1",)

        ms.invalidate_capability("SIG-T1", reason="MS1945_T1_CURRENTNESS_HOSTILE")
        assert ms.action_outcome_predictive_relation_status(t1_relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
        assert ms.counterfactual_rehearsal_status(selected.proposal_id)["status"] == "UNKNOWN_INCOMPLETE"

        _reset_start(ms, world, 19452)
        assert ms.counterfactual_rehearsal_status(t0_only.proposal_id)["status"] == "CURRENT_REHEARSAL_PROPOSAL"
        commitment = ms.derive_bounded_action_commitment(t0_only.proposal_id)
        assert commitment.commitment.value == "UNKNOWN"
        assert commitment.reason == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        intent = ms.nominate_bounded_action_intent(t0_only.proposal_id, _act_obligation())
        assert intent["status"] == "ABSTAIN"
        assert intent["reason"] == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        assert _coord_subject(ms) == coord_before
        assert not hasattr(ms, "signal_policy")
    finally:
        _finish(td, ms)
