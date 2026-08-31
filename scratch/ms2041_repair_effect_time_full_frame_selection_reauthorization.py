from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2035_organism_owned_current_value_frame_completeness import _contract
from scratch.ms2036_full_frame_bound_pareto_research import _fixture, _p2_dominates_effects


def _prepare():
    td, ms, calls, _by_probe, _effects = _fixture(_p2_dominates_effects())
    internal_ops = ms._current_owned_referent_epistemic_opportunities(act_ob())
    selected = next(op for op in internal_ops if str(op["probe_action_id"]) == "P2")
    nominated = ms.nominate_current_strict_full_frame_referent_epistemic_opportunity(act_ob())
    assert nominated["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", nominated
    return td, ms, calls, selected, nominated


def _execute(ms, selected, nominated):
    return ms.execute_bounded_action(
        nominated["nomination"]["intent"]["intent_id"],
        act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(
            selected["trial"], decision_context=selected["decision_context"],
        ),
    )


def run_stable() -> dict:
    td, ms, calls, selected, nominated = _prepare()
    try:
        unknown = ms.evidence.get(nominated["unknown_evidence_id"])
        assert unknown is not None
        nomination_selection_id = str(unknown["payload"]["cross_deficit_selection_commitment_id"])
        nomination_frame_digest = str(unknown["payload"]["complete_value_frame_digest_sha256"])
        fresh = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob())
        assert fresh["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", fresh
        fresh_selection_id = str(fresh["selection_commitment"]["commitment_id"])
        execution = _execute(ms, selected, nominated)
        assert execution["status"] == "ACTION_EXECUTED", execution
        assert calls == ["P2"], calls
        packet = execution["execution"]
        premises = set(packet["execution_premise_ids"])
        assert nominated["unknown_evidence_id"] in premises, packet
        assert nomination_selection_id in premises, packet
        assert fresh_selection_id in premises, packet
        assert nomination_frame_digest in premises, packet
        assert packet["execution_commitment_id"] not in {nomination_selection_id, fresh_selection_id}
        return {
            "status": "PASS",
            "execution": execution,
            "selected_unknown_evidence_id": nominated["unknown_evidence_id"],
            "nomination_selection_commitment_id": nomination_selection_id,
            "fresh_selection_commitment_id": fresh_selection_id,
            "nomination_frame_digest": nomination_frame_digest,
            "handler_calls": list(calls),
            "execution_lineage_contains_full_frame_nomination_and_fresh_selection": "YES",
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_new_value_block() -> dict:
    td, ms, calls, selected, nominated = _prepare()
    try:
        ms.register_value_variable(_contract("X"))
        ms.observe_value_state("X", 1.0)
        fresh = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob())
        assert fresh["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", fresh
        execution = _execute(ms, selected, nominated)
        assert execution["status"] == "NO_EXECUTION", execution
        assert execution["reason"] == "CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION", execution
        assert calls == [], calls
        return {"status": "PASS", "fresh_selection": fresh, "execution": execution, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_forged_unknown_block() -> dict:
    td, ms, calls, selected, nominated = _prepare()
    try:
        deficit_id = nominated["selected_deficit_id"]
        original = ms.epistemic_deficits.records[deficit_id]
        selected_unknown = ms.evidence.get(nominated["unknown_evidence_id"])
        raw_id = str(selected_unknown["payload"]["source_raw_observation_evidence_id"])
        ms.epistemic_deficits.records[deficit_id] = replace(original, unknown_evidence_id=raw_id)
        execution = _execute(ms, selected, nominated)
        assert execution["status"] == "NO_EXECUTION", execution
        assert execution["reason"] in {
            "EPISTEMIC_PROGRAM_STEP_PREMISE_DRIFT",
            "FULL_FRAME_SELECTION_NOMINATION_ANCESTRY_REQUIRED_AT_EXECUTION",
        }, execution
        assert calls == [], calls
        return {"status": "PASS", "forged_unknown_evidence_id": raw_id, "execution": execution, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2041() -> dict:
    return {
        "status": "PASS",
        "stable": run_stable(),
        "new_value_block": run_new_value_block(),
        "forged_unknown_block": run_forged_unknown_block(),
        "ordinary_effect_owner": "CapabilityRegistry.invoke",
        "selection_execution_authority": "NONE",
        "new_scheduler_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2041(), indent=2, sort_keys=True, default=str))
