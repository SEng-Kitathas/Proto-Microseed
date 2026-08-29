from __future__ import annotations

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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
from tests.embodiment.test_ms1940_opaque_signaling_by_composition import (
    _act_obligation,
    _basis_obligation,
    _obs_obligation,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _reset_start
from tests.embodiment.test_ms1943_signal_predictive_currentness import _fresh, _execute, _finish, _coord_subject
from tests.embodiment.test_ms1944_signal_replacement_qualification_boundary import (
    _drift_and_qualify_replacement,
)


def _register_t1(ms, world):
    def emit_t1(**_):
        world["emitted"] = "T1"
        return {"opaque_emitted_token": "T1"}

    ms.register_capability(
        CapabilityContract(
            "SIG-T1",
            "opaque-effect-token-emission",
            {},
            {"output": "opaque-token"},
            (
                "SIGNAL != REFERENCE",
                "TOKEN_EMITTED != TOKEN_MEANS",
                "REPRESENTED_SIGNAL_ALTERNATIVE != TOKEN_MEANING",
                "NO_SEMANTIC_MESSAGE_AUTHORITY",
            ),
            (),
            Authority.EFFECT,
            ("MS1945",),
            "CURRENT",
            {},
            query_obligation_id="ACT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=emit_t1,
            operational_scope_id="S",
            assistance_ancestry=("SUPPLIED_REPRESENTED_OPAQUE_SIGNAL_ALTERNATIVE",),
        ),
        counterparty_dependencies=(("CP", 0),),
        coordination_dependencies=(("R", 0),),
    )


def _t1_rows():
    return tuple(
        RehearsalTransitionObservation(
            f"MS1945-T1-SEED-{i}",
            "S0",
            "SIG-T1",
            "CP-ACK",
            2.2,
            0,
            "F",
            0,
            "E",
            0,
            None,
            None,
            "R",
            0,
        )
        for i in range(12)
    )


def _option(cid: str):
    return RecruitmentOption(cid, FeasibilityState.FEASIBLE, local_cost=0.1)


def _holdouts(ms, candidate, *, next_state: str, value_effect: float, n: int = 16):
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
    refs = []
    for i in range(n):
        refs.append(
            ms.append_evidence(
                f"MS1945-T1-HOLDOUT-{i}",
                {
                    **base,
                    "actual_next_state_id": next_state,
                    "actual_value_effect": value_effect,
                    "holdout_index": i,
                },
                EpistemicStatus.PRESSURE_SUPPORTED,
                source="EXTERNAL-HOLDOUT",
            )
        )
    return tuple(refs)


def _record_final_outcome(ms, execution, *, suffix: str):
    return ms.record_bounded_action_outcome_via_observation_basis(
        execution["execution"]["execution_id"],
        observation_capability_id="OBS-CP",
        observation_obligation=_obs_obligation(),
        basis_capability_id="OBS-BASIS",
        basis_obligation=_basis_obligation(),
        evidence_id=f"E-MS1945-FINAL-{suffix}",
        capture_id=f"CAP-MS1945-FINAL-{suffix}",
    )


def main():
    checks = {}
    td, ms, world, old_relation_id, old_t0_proposal = _fresh()
    try:
        # MS1944 boundary: T0 is represented/current but now predicts no regulatory benefit.
        t0_replacement_id, coord_before = _drift_and_qualify_replacement(
            ms, world, old_relation_id, old_t0_proposal
        )
        assert world["expected"] == "T1"
        assert ms.action_outcome_predictive_relation_status(t0_replacement_id)["status"] == "CURRENT_PREDICTIVE_RELATION"
        checks["t0_zero_benefit_replacement_current"] = True

        # Represent T1 without giving it meaning or a learned response model.
        _register_t1(ms, world)
        _reset_start(ms, world, 19450)
        options = (_option("SIG-T0"), _option("SIG-T1"))
        before_learning = ms.nominate_counterfactual_rehearsal(
            (), options, start_state_id="S0", value_id="V"
        )
        assert before_learning is not None
        assert before_learning.sequence == ("SIG-T0",)
        before_commitment = ms.derive_bounded_action_commitment(before_learning.proposal_id)
        assert before_commitment.commitment.value == "UNKNOWN"
        assert before_commitment.reason == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        checks["represented_t1_without_qualified_model_not_selected"] = True

        # Training/exploration assistance is explicit: supplied seed rows make actual T1
        # executions lawful, but final selection uses zero supplied transition rows.
        seed = ms.nominate_counterfactual_rehearsal(
            _t1_rows(), (_option("SIG-T1"),), start_state_id="S0", value_id="V"
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
        t1_candidate = candidates[0]
        assert t1_candidate.support == 12
        assert t1_candidate.consistency == 1.0
        refs = _holdouts(ms, t1_candidate, next_state="CP-ACK", value_effect=2.2)
        ticket = ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(
            t1_candidate, qualification_evidence=refs
        )
        qualified = ms.qualify_action_outcome_predictive_relation(ticket)
        assert qualified["status"] == "CURRENT_PREDICTIVE_RELATION"
        t1_relation_id = qualified["relation"]["relation_id"]
        checks["t1_history_learned_and_exact_subject_qualified"] = True

        # Core discriminator: both T0 and T1 are represented and current; only T1's
        # current qualified model predicts regulatory recovery. No supplied transition rows.
        _reset_start(ms, world, 19451)
        selected = ms.nominate_counterfactual_rehearsal(
            (), options, start_state_id="S0", value_id="V"
        )
        assert selected is not None
        assert selected.sequence == ("SIG-T1",)
        assert selected.predicted_state_path == ("S0", "CP-ACK")
        assert selected.predicted_step_value_effects == (2.2,)
        assert selected.action_indicated is False
        assert selected.execution_authority == "NONE"
        commitment = ms.derive_bounded_action_commitment(selected.proposal_id)
        assert commitment.commitment.value == "YES"
        assert commitment.reason == "BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE"
        intent = ms.nominate_bounded_action_intent(selected.proposal_id, _act_obligation())
        assert intent["status"] == "ACTION_INTENT_NOMINATED"
        assert intent["intent"]["capability_id"] == "SIG-T1"
        assert intent["execution_authority"] == "NONE"
        checks["ordinary_rehearsal_selects_current_regulatory_useful_t1"] = True

        executed = ms.execute_bounded_action(intent["intent"]["intent_id"], _act_obligation())
        assert executed["status"] == "ACTION_EXECUTED"
        actual = _record_final_outcome(ms, executed, suffix="T1")
        assert actual["status"] == "ACTION_OUTCOME_OBSERVED"
        assert actual["outcome"]["actual_next_state_id"] == "CP-ACK"
        assert world["emitted"] == "T1"
        checks["selected_t1_succeeds_through_ordinary_effect_and_observation_path"] = True

        # Selection is currentness-bound rather than persistent signal policy.
        ms.invalidate_capability("SIG-T1", reason="MS1945_T1_CURRENTNESS_HOSTILE")
        assert ms.action_outcome_predictive_relation_status(t1_relation_id)["status"] == "STALE_PREDICTIVE_RELATION"
        assert ms.counterfactual_rehearsal_status(selected.proposal_id)["status"] == "UNKNOWN_INCOMPLETE"
        _reset_start(ms, world, 19452)
        # Reuse the already registered T0-only proposal from before T1 qualification.
        # Re-nominating it would deterministically reproduce the same proposal ID and
        # correctly trip duplicate-proposal protection, which is not the target here.
        assert ms.counterfactual_rehearsal_status(before_learning.proposal_id)["status"] == "CURRENT_REHEARSAL_PROPOSAL"
        stale_commitment = ms.derive_bounded_action_commitment(before_learning.proposal_id)
        assert stale_commitment.commitment.value == "UNKNOWN"
        stale_intent = ms.nominate_bounded_action_intent(before_learning.proposal_id, _act_obligation())
        assert stale_intent["status"] == "ABSTAIN"
        assert stale_intent["reason"] == "NO_DISCRIMINATING_REGULATORY_ADVANTAGE"
        checks["t1_currentness_loss_removes_selection_without_persistent_policy"] = True

        assert ms.coordinations.is_current("R")
        coord_after = _coord_subject(ms)
        assert coord_after == coord_before
        assert not hasattr(ms, "token_meanings")
        assert not hasattr(ms, "signal_policy")
        assert not hasattr(ms, "semantic_convention_registry")
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        checks["no_semantic_registry_policy_or_coordination_rewrite"] = True

        summary = {
            "status": "PASS",
            "checks": checks,
            "selected_sequence": list(selected.sequence),
            "selected_predicted_effect": selected.predicted_value_effect,
            "selected_commitment": commitment.serializable(),
            "t0_replacement_relation_id": t0_replacement_id,
            "t1_relation_id": t1_relation_id,
            "coordination_subject_unchanged": True,
            "semantic_signal_authority": "NONE",
            "reference_authority": "NONE",
            "policy_selection_authority": "NONE",
            "language": ms.status()["language"],
            "training_assistance": [
                "SUPPLIED_REPRESENTED_OPAQUE_SIGNAL_ALTERNATIVE",
                "SUPPLIED_T1_SEED_REHEARSAL_ROWS_FOR_HISTORY_ACQUISITION_ONLY",
                "EXTERNAL_EXACT_SUBJECT_HOLDOUT_QUALIFICATION",
            ],
            "final_selection_supplied_transition_rows": 0,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        _finish(td, ms)


if __name__ == "__main__":
    main()
