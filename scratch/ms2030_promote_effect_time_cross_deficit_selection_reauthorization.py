from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface
from scratch.ms2025_effect_time_cross_deficit_selection_staleness_hostile import _add_strong_current_p4_competitor


def _selected_bundle(m):
    ops, selection, selected = m._current_owned_referent_cross_deficit_selection_bundle(act_ob())
    assert selection.licenses_yes(), selection.serializable()
    assert selected is not None and selected["probe_action_id"] == "P2", (selection.serializable(), selected)
    return ops, selection, selected


def _nominate(m):
    out = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
    assert out["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", out
    assert out["selected_probe_action_id"] == "P2", out
    return out


def run_stable() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        ops, nomination_selection, selected = _selected_bundle(m)
        nominated = _nominate(m)
        unknown = m.evidence.get(nominated["unknown_evidence_id"])
        assert unknown is not None, nominated
        nomination_selection_id = str(unknown["payload"]["cross_deficit_selection_commitment_id"])
        execution = m.execute_bounded_action(
            nominated["nomination"]["intent"]["intent_id"],
            act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                selected["trial"], decision_context=selected["decision_context"],
            ),
        )
        assert execution["status"] == "ACTION_EXECUTED", execution
        assert calls == ["P2"], calls
        packet = execution["execution"]
        fresh_surface = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        assert fresh_surface["status"] == "CURRENT_STRICT_SAME_VALUE_CROSS_DEFICIT_SELECTION", fresh_surface
        fresh_selection_id = str(fresh_surface["selection_commitment"]["commitment_id"])
        premises = set(packet["execution_premise_ids"])
        assert nominated["unknown_evidence_id"] in premises, (packet, nominated)
        assert nomination_selection_id in premises, (packet, nomination_selection_id)
        assert fresh_selection_id in premises, (packet, fresh_selection_id)
        assert packet["execution_commitment_id"] not in {nomination_selection_id, fresh_selection_id}, packet
        return {
            "status": "PASS",
            "execution": execution,
            "nomination_selection_commitment_id": nomination_selection_id,
            "fresh_selection_commitment_id": fresh_selection_id,
            "selected_unknown_evidence_id": nominated["unknown_evidence_id"],
            "handler_calls": list(calls),
            "execution_lineage_contains_nomination_and_fresh_selection": "YES",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_new_competitor_block() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        ops, nomination_selection, selected = _selected_bundle(m)
        nominated = _nominate(m)
        weak_p4 = next(op for op in ops if op["probe_action_id"] == "P4")
        _add_strong_current_p4_competitor(m, weak_p4)
        fresh = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        assert fresh["status"] == "NO_CURRENT_STRICT_CROSS_DEFICIT_SELECTION", fresh
        assert fresh["selection_commitment"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", fresh
        execution = m.execute_bounded_action(
            nominated["nomination"]["intent"]["intent_id"],
            act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                selected["trial"], decision_context=selected["decision_context"],
            ),
        )
        assert execution["status"] == "NO_EXECUTION", execution
        assert execution["reason"] == "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION", execution
        assert calls == [], calls
        return {"status": "PASS", "fresh_selection": fresh, "execution": execution, "handler_calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_forged_selected_unknown_ancestry_block() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        ops, nomination_selection, selected = _selected_bundle(m)
        nominated = _nominate(m)
        deficit_id = nominated["selected_deficit_id"]
        original = m.epistemic_deficits.records[deficit_id]
        # Preserve the selected-origin marker but redirect its durable UNKNOWN pointer
        # to the raw observation premise. The raw record is real/current, but it is
        # not the selected endogenous UNKNOWN admission receipt required by MS2029.
        raw_id = str(m.evidence.get(nominated["unknown_evidence_id"])["payload"]["source_raw_observation_evidence_id"])
        m.epistemic_deficits.records[deficit_id] = replace(original, unknown_evidence_id=raw_id)
        execution = m.execute_bounded_action(
            nominated["nomination"]["intent"]["intent_id"],
            act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                selected["trial"], decision_context=selected["decision_context"],
            ),
        )
        assert execution["status"] == "NO_EXECUTION", execution
        assert execution["reason"] in {
            "EPISTEMIC_PROGRAM_STEP_PREMISE_DRIFT",
            "CROSS_DEFICIT_SELECTION_NOMINATION_ANCESTRY_REQUIRED_AT_EXECUTION",
        }, execution
        assert calls == [], calls
        return {"status": "PASS", "forged_unknown_evidence_id": raw_id, "execution": execution, "handler_calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2030() -> dict:
    return {
        "status": "PASS",
        "stable": run_stable(),
        "new_competitor_block": run_new_competitor_block(),
        "forged_selected_unknown_ancestry_block": run_forged_selected_unknown_ancestry_block(),
        "ordinary_effect_owner": "CapabilityRegistry.invoke",
        "new_scheduler_required": "NO",
        "execution_authority_added_to_selection": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2030(), indent=2, sort_keys=True, default=str))
