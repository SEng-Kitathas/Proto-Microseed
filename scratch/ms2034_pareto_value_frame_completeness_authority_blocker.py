from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2033_cross_value_epistemic_consequence_vector_construction import (
    REQUESTED_VALUES,
    _complete_fixture,
    _effect_surface,
    _seed_effect_support,
    derive_cross_value_epistemic_consequence_vector,
)
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface


def _frame_descriptor(row: dict) -> tuple[tuple[str, int, float, str], ...] | None:
    if row.get("status") != "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR":
        return None
    requested = tuple(str(x) for x in row.get("requested_value_ids", ()))
    value_rows = row.get("value_rows")
    worst = row.get("worst_residual_by_value")
    if not requested or not isinstance(value_rows, dict) or not isinstance(worst, dict):
        return None
    if set(requested) != set(value_rows) or set(requested) != set(worst):
        return None
    descriptor = []
    for value_id in sorted(requested):
        v = value_rows.get(value_id)
        if not isinstance(v, dict):
            return None
        residual = worst.get(value_id)
        if not isinstance(residual, (int, float)) or not math.isfinite(float(residual)) or float(residual) < 0.0:
            return None
        descriptor.append((
            value_id,
            int(v.get("value_epoch", -1)),
            float(v.get("current_value")),
            str(v.get("contract_signature_sha256", "")),
        ))
    return tuple(descriptor)


def derive_strict_pareto_selection_from_vector_rows(rows: tuple[dict, ...]) -> dict:
    base = {
        "execution_authority": "NONE",
        "truth_authority": "NONE",
        "semantic_goal_authority": "NONE",
        "semantic_value_priority_authority": "NONE",
        "persistence": "NONE",
    }
    if len(rows) < 2:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "MULTIPLE_COMPLETE_VECTORS_REQUIRED", "research_selection_authority": "NONE"}
    descriptors = tuple(_frame_descriptor(dict(row)) for row in rows)
    if any(x is None for x in descriptors):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "COMPLETE_CURRENT_VECTOR_REQUIRED", "research_selection_authority": "NONE"}
    if len(set(descriptors)) != 1:
        return {**base, "status": "DEFER_UNKNOWN", "reason": "EXACT_MATCHING_CURRENT_VALUE_FRAME_REQUIRED", "research_selection_authority": "NONE"}
    coordinate_ids = tuple(x[0] for x in descriptors[0])

    def dominates(a: dict, b: dict) -> bool:
        aw = a["worst_residual_by_value"]
        bw = b["worst_residual_by_value"]
        return (
            all(float(aw[v]) <= float(bw[v]) for v in coordinate_ids)
            and any(float(aw[v]) < float(bw[v]) for v in coordinate_ids)
        )

    winners = []
    for i, row in enumerate(rows):
        if all(i == j or dominates(row, other) for j, other in enumerate(rows)):
            winners.append(row)
    if len(winners) != 1:
        return {
            **base,
            "status": "NO_STRICT_PARETO_SELECTION",
            "reason": "NO_UNIQUE_STRICT_PARETO_DOMINATOR",
            "research_selection_authority": "NONE",
            "coordinate_ids": list(coordinate_ids),
        }
    winner = winners[0]
    return {
        **base,
        "status": "CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY",
        "reason": "UNIQUE_STRICT_PARETO_DOMINATOR",
        "research_selection_authority": "STRICT_PARETO_REGULATORY_DOMINANCE_ONLY",
        "selected_deficit_id": str(winner.get("deficit_id")),
        "selected_probe_action_id": str(winner.get("probe_action_id")),
        "coordinate_ids": list(coordinate_ids),
    }


def _vectors(ms, by_probe, effects, requested):
    return {
        probe: derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe[probe],
            values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effects,
            requested_value_ids=tuple(requested),
        )
        for probe in ("P2", "P4")
    }


def run_full_frame_tradeoff() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        vectors = _vectors(ms, by_probe, effects, REQUESTED_VALUES)
        result = derive_strict_pareto_selection_from_vector_rows((vectors["P2"], vectors["P4"]))
        reverse = derive_strict_pareto_selection_from_vector_rows((vectors["P4"], vectors["P2"]))
        assert vectors["P2"]["worst_residual_by_value"] == {"V": 0.0, "W": 0.5}
        assert vectors["P4"]["worst_residual_by_value"] == {"V": 0.5, "W": 0.0}
        assert result["status"] == "NO_STRICT_PARETO_SELECTION", result
        assert reverse == result
        assert calls == []
        return {"status": "PASS", "vectors": vectors, "selection": result, "order_independent": True}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_caller_subset_violation() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        full = _vectors(ms, by_probe, effects, ("V", "W"))
        full_selection = derive_strict_pareto_selection_from_vector_rows((full["P2"], full["P4"]))
        subset = _vectors(ms, by_probe, effects, ("V",))
        subset_selection = derive_strict_pareto_selection_from_vector_rows((subset["P2"], subset["P4"]))
        assert full_selection["status"] == "NO_STRICT_PARETO_SELECTION", full_selection
        assert subset_selection["status"] == "CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY", subset_selection
        assert subset_selection["selected_probe_action_id"] == "P2", subset_selection
        assert subset_selection["coordinate_ids"] == ["V"], subset_selection
        assert calls == []
        return {
            "status": "AUTHORITY_VIOLATION_REPRODUCED",
            "full_frame_selection": full_selection,
            "caller_subset_selection": subset_selection,
            "omitted_coordinate": "W",
            "false_dominance_created_by_omission": "YES",
            "handler_calls": list(calls),
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_frame_descriptor_drift_block() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        p2 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=REQUESTED_VALUES,
        )
        ms.observe_value_state("W", -0.75)
        p4 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P4"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=REQUESTED_VALUES,
        )
        result = derive_strict_pareto_selection_from_vector_rows((p2, p4))
        assert result["status"] == "DEFER_UNKNOWN", result
        assert result["reason"] == "EXACT_MATCHING_CURRENT_VALUE_FRAME_REQUIRED", result
        assert calls == []
        return {"status": "PASS", "selection": result, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_incomplete_vector_block() -> dict:
    td, ms, calls, *_ = _surface(True)
    try:
        _seed_effect_support(ms, include_b_w=False)
        opps = ms.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        by_probe = {row["probe_action_id"]: row for row in opps["opportunities"]}
        effects = _effect_surface(ms)
        p2 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=REQUESTED_VALUES,
        )
        p4 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P4"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=REQUESTED_VALUES,
        )
        result = derive_strict_pareto_selection_from_vector_rows((p2, p4))
        assert p2["status"] == "DEFER_UNKNOWN"
        assert result["status"] == "DEFER_UNKNOWN", result
        assert result["reason"] == "COMPLETE_CURRENT_VECTOR_REQUIRED", result
        assert calls == []
        return {"status": "PASS", "selection": result, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2034() -> dict:
    return {
        "status": "SUBSTANTIVE_VALUE_FRAME_AUTHORITY_BLOCKER_REPRODUCED",
        "full_frame_tradeoff": run_full_frame_tradeoff(),
        "caller_subset_violation": run_caller_subset_violation(),
        "frame_descriptor_drift_block": run_frame_descriptor_drift_block(),
        "incomplete_vector_block": run_incomplete_vector_block(),
        "blocker": "EXACT_MATCHING_VECTOR_FRAME != COMPLETE_CURRENT_VALUE_FRAME",
        "scar": "CALLER_SELECTED_VALUE_SUBSET_CAN_CREATE_FALSE_PARETO_DOMINANCE",
        "runtime_pareto_selection_authorized": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2034(), indent=2, sort_keys=True, default=str))
