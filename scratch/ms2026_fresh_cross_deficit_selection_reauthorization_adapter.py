from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2021_cross_deficit_selection_blocker_replayed_with_raw_contrast import enumerate_opportunities
from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import derive_strict_same_value_regulatory_dominance
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface, derive_selection_commitment
from scratch.ms2024_selected_opportunity_persistence_and_nomination import persist_and_nominate_selected_current_opportunity
from scratch.ms2025_effect_time_cross_deficit_selection_staleness_hostile import _add_strong_current_p4_competitor


def execute_with_fresh_cross_deficit_selection_reauthorization(m, persisted: dict, selected_opportunity: dict) -> dict:
    fresh_surface = enumerate_opportunities(m)
    if fresh_surface.get("status") != "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES":
        return {
            "status": "NO_EXECUTION",
            "reason": "CURRENT_CROSS_DEFICIT_OPPORTUNITY_SURFACE_REQUIRED",
            "fresh_surface": fresh_surface,
            "selection_authority": "NONE",
            "execution_authority": "NONE",
        }
    comparison = derive_strict_same_value_regulatory_dominance(m, fresh_surface["opportunities"])
    selection = derive_selection_commitment(comparison, fresh_surface["opportunities"])
    if not selection.licenses_yes():
        return {
            "status": "NO_EXECUTION",
            "reason": "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED",
            "fresh_surface": fresh_surface,
            "fresh_comparison": comparison,
            "fresh_selection": selection.serializable(),
            "selection_authority": "NONE",
            "execution_authority": "NONE",
        }
    q = dict(selection.qualifiers)
    if (
        str(q.get("selected_deficit_id")) != str(persisted["selected_deficit_id"])
        or str(q.get("selected_probe_action_id")) != str(persisted["selected_probe_action_id"])
    ):
        return {
            "status": "NO_EXECUTION",
            "reason": "CROSS_DEFICIT_SELECTED_OPPORTUNITY_DRIFT",
            "fresh_surface": fresh_surface,
            "fresh_comparison": comparison,
            "fresh_selection": selection.serializable(),
            "selection_authority": "NONE",
            "execution_authority": "NONE",
        }
    execution = m.execute_bounded_action(
        persisted["nomination"]["intent"]["intent_id"],
        act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(
            selected_opportunity["trial"],
            decision_context=selected_opportunity["decision_context"],
        ),
    )
    return {
        "status": execution["status"],
        "reason": execution.get("reason", execution["status"]),
        "execution": execution,
        "fresh_surface": fresh_surface,
        "fresh_comparison": comparison,
        "fresh_selection": selection.serializable(),
        "selection_authority": q["selection_authority"],
        "execution_authority": "DELEGATED_TO_ORDINARY_EXECUTOR_ONLY",
    }


def _selected_opportunity(initial_surface: dict, persisted: dict) -> dict:
    return next(
        op for op in initial_surface["opportunities"]
        if op["deficit"].deficit_id == persisted["selected_deficit_id"]
        and op["probe_action_id"] == persisted["selected_probe_action_id"]
    )


def run_stable() -> dict:
    td, m, calls, initial_surface, comparison, selection = _surface(True)
    try:
        _ops, _native_selection, selected = m._current_owned_referent_cross_deficit_selection_bundle(act_ob())
        assert _native_selection.licenses_yes() and selected is not None
        persisted = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        assert persisted["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", persisted
        result = execute_with_fresh_cross_deficit_selection_reauthorization(m, persisted, selected)
        assert result["status"] == "ACTION_EXECUTED", result
        assert calls == ["P2"], calls
        return {"status": "PASS", "result": result, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_new_competitor_block() -> dict:
    td, m, calls, initial_surface, comparison, selection = _surface(True)
    try:
        _ops, _native_selection, selected = m._current_owned_referent_cross_deficit_selection_bundle(act_ob())
        assert _native_selection.licenses_yes() and selected is not None
        persisted = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        assert persisted["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", persisted
        weak_p4 = next(op for op in initial_surface["opportunities"] if op["probe_action_id"] == "P4")
        _add_strong_current_p4_competitor(m, weak_p4)
        result = execute_with_fresh_cross_deficit_selection_reauthorization(m, persisted, selected)
        assert result["status"] == "NO_EXECUTION", result
        assert result["reason"] == "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED", result
        assert result["fresh_comparison"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", result
        assert calls == [], calls
        return {"status": "PASS", "result": result, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2026() -> dict:
    return {
        "status": "PASS",
        "stable": run_stable(),
        "new_competitor_block": run_new_competitor_block(),
        "new_scheduler_required": "NO",
        "persistent_opportunity_registry_required": "NO",
        "ordinary_executor_remains_effect_owner": "YES",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2026(), indent=2, sort_keys=True, default=str))
