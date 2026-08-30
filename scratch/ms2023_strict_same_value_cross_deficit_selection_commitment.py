from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import (
    P4_D,
    _persist_context,
    _second_asymmetric_binding,
    _second_same_state_binding,
    _setup_same_state_owned_prefix,
    derive_strict_same_value_regulatory_dominance,
    enumerate_opportunities,
)


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def derive_selection_commitment(comparison: dict, opportunities) -> RelationalCommitment:
    target = "cross-deficit-epistemic-selection"
    qnone = (
        ("authority_gain", "NONE"),
        ("selection_authority", "NONE"),
        ("execution_authority", "NONE"),
        ("truth_authority", "NONE"),
        ("semantic_goal_authority", "NONE"),
    )
    rows = tuple(opportunities)
    premises = tuple(
        sorted({
            str(op["deficit"].deficit_id)
            for op in rows
        } | {
            str(op["commitment"].commitment_id)
            for op in rows
        } | {
            str(op["contrast_information"].commitment_id)
            for op in rows
        })
    )
    if comparison.get("status") != "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_QUARRY":
        return RelationalCommitment(
            _sha({"target": target, "comparison": comparison, "premises": premises}),
            target,
            TernaryCommitment.UNKNOWN,
            reason=str(comparison.get("reason", comparison.get("status", "NO_STRICT_CROSS_DEFICIT_DOMINANCE"))),
            qualifiers=qnone,
            premise_ids=premises,
        )
    probe = str(comparison["dominant_probe_action_id"])
    matching = tuple(op for op in rows if str(op["probe_action_id"]) == probe)
    if len(matching) != 1:
        return RelationalCommitment(
            _sha({"target": target, "probe": probe, "matches": len(matching)}),
            target,
            TernaryCommitment.UNKNOWN,
            reason="EXACT_SINGLE_DOMINANT_OPPORTUNITY_REQUIRED",
            qualifiers=qnone,
            premise_ids=premises,
        )
    dominant = matching[0]
    return RelationalCommitment(
        _sha({
            "target": target,
            "probe": probe,
            "deficit": dominant["deficit"].deficit_id,
            "comparison_basis": comparison["comparison_basis"],
            "best": comparison["dominant_worst_residual_pressure"],
            "next": comparison["next_worst_residual_pressure"],
            "premises": premises,
        }),
        target,
        TernaryCommitment.YES,
        reason="STRICT_SAME_VALUE_CROSS_DEFICIT_REGULATORY_DOMINANCE",
        qualifiers=(
            ("authority_gain", "NONE"),
            ("selection_authority", "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"),
            ("execution_authority", "NONE"),
            ("truth_authority", "NONE"),
            ("semantic_goal_authority", "NONE"),
            ("selected_probe_action_id", probe),
            ("selected_deficit_id", str(dominant["deficit"].deficit_id)),
            ("comparison_basis", str(comparison["comparison_basis"])),
            ("dominant_worst_residual_pressure", str(comparison["dominant_worst_residual_pressure"])),
            ("next_worst_residual_pressure", str(comparison["next_worst_residual_pressure"])),
        ),
        premise_ids=premises,
    )


def _surface(asymmetric: bool):
    td, m, calls, world, binding1, bucket_a, bucket_b = _setup_same_state_owned_prefix()
    bucket_d = str(_persist_context(m, "MS2023-D-ASYM" if asymmetric else "MS2023-D-SYM", P4_D)["projection_bucket_id"])
    projection = m.epistemic_projections.records[m.action_outcome_learning.projection_conditioned_bindings[binding1].projection_id]
    if asymmetric:
        _second_asymmetric_binding(m, projection, bucket_a, bucket_d)
    else:
        _second_same_state_binding(m, projection, bucket_a, bucket_d)
    opportunities = enumerate_opportunities(m)
    assert opportunities["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", opportunities
    comparison = derive_strict_same_value_regulatory_dominance(m, opportunities["opportunities"])
    commitment = derive_selection_commitment(comparison, opportunities["opportunities"])
    return td, m, calls, opportunities, comparison, commitment


def run_symmetric() -> dict:
    td, m, calls, opportunities, comparison, commitment = _surface(False)
    try:
        assert commitment.commitment == TernaryCommitment.UNKNOWN, commitment.serializable()
        assert commitment.reason == "WORST_RESIDUAL_PRESSURE_TIE"
        assert dict(commitment.qualifiers)["selection_authority"] == "NONE"
        assert calls == []
        return {
            "status": "PASS",
            "comparison": comparison,
            "commitment": commitment.serializable(),
            "calls": list(calls),
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric() -> dict:
    td, m, calls, opportunities, comparison, commitment = _surface(True)
    try:
        q = dict(commitment.qualifiers)
        assert commitment.licenses_yes(), commitment.serializable()
        assert commitment.reason == "STRICT_SAME_VALUE_CROSS_DEFICIT_REGULATORY_DOMINANCE"
        assert q["selected_probe_action_id"] == "P2"
        assert q["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"
        assert q["execution_authority"] == "NONE"
        assert calls == []
        return {
            "status": "PASS",
            "comparison": comparison,
            "commitment": commitment.serializable(),
            "calls": list(calls),
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_value_observation_drift() -> dict:
    td, m, calls, opportunities, comparison, commitment = _surface(True)
    try:
        assert commitment.licenses_yes(), commitment.serializable()
        # Same value epoch, new current observation inside the viable interval. Re-derive;
        # stale dominance must disappear rather than being cached as selection authority.
        m.observe_value_state("V", 5.0)
        fresh_comparison = derive_strict_same_value_regulatory_dominance(m, opportunities["opportunities"])
        fresh_commitment = derive_selection_commitment(fresh_comparison, opportunities["opportunities"])
        assert not fresh_commitment.licenses_yes(), fresh_commitment.serializable()
        assert dict(fresh_commitment.qualifiers)["selection_authority"] == "NONE"
        assert calls == []
        return {
            "status": "PASS",
            "before": commitment.serializable(),
            "after_comparison": fresh_comparison,
            "after": fresh_commitment.serializable(),
            "calls": list(calls),
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2023() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric": run_asymmetric(),
        "value_observation_drift": run_value_observation_drift(),
        "selection_authority_scope": "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY",
        "execution_authority": "NONE",
        "new_scheduler_required": "NO",
        "new_weighted_utility_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2023(), indent=2, sort_keys=True, default=str))
