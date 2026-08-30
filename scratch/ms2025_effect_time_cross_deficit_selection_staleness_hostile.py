from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _relation, act_ob
from scratch.ms2021_cross_deficit_selection_blocker_replayed_with_raw_contrast import _holdouts, enumerate_opportunities
from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import derive_strict_same_value_regulatory_dominance
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface, derive_selection_commitment
from scratch.ms2024_selected_opportunity_persistence_and_nomination import persist_and_nominate_selected_current_opportunity


def _add_strong_current_p4_competitor(m, weak_p4_opportunity: dict) -> str:
    weak_binding = m.action_outcome_learning.projection_conditioned_bindings[str(weak_p4_opportunity["binding_id"])]
    live = m.derive_current_partial_operational_referent_ambiguity(
        weak_binding.binding_id, max_probe_steps=2, max_records=4096,
    )
    assert live["status"] == "CURRENT_PARTIAL_OPERATIONAL_REFERENT_AMBIGUITY", live
    assert live["unique_probe_action_id"] == "P4", live
    buckets = tuple(str(x) for x in live["surviving_bucket_ids"])
    assert len(buckets) == 2, buckets
    b0, b1 = buckets
    projection = m.epistemic_projections.records[weak_binding.projection_id]

    # Reuse already-current C/D/P4 capability owners. Only a new independently
    # qualified routing hypothesis is introduced; P2's own local premises do not move.
    rel0 = {
        "C": _relation(m, "MS2025-0-C", "C", "c-next-25", 2.0, "25OC"),
        "D": _relation(m, "MS2025-0-D", "D", "d-next-25", 0.0, "25OD"),
        "P4": _relation(m, "MS2025-0-P4", "P4", "s0", 0.0, "25OP"),
    }
    rel1 = {
        "C": _relation(m, "MS2025-1-C", "C", "c-next-25b", 0.0, "25IC"),
        "D": _relation(m, "MS2025-1-D", "D", "d-next-25b", 2.0, "25ID"),
        "P4": _relation(m, "MS2025-1-P4", "P4", "s0", 0.0, "25IP"),
    }
    proposal = m.append_evidence(
        "MS2025-ROUTE3-PROP",
        {"kind": "ROUTING_PROPOSAL", "basis": "NEW_CURRENT_STRONG_P4_COMPETITOR_AFTER_P2_NOMINATION"},
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="MS2025",
    )
    task = "MS2025-DECISION-3"
    route = m.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,
        task_id=task,
        action_ids=("C", "D", "P4"),
        channel_ids=("opaque-control",),
        horizon=1,
        default_action_relations=tuple((a, rel0[a].relation_id) for a in ("C", "D", "P4")),
        bucket_action_overrides=tuple((b1, a, rel1[a].relation_id) for a in ("C", "D", "P4")),
        source_evidence_ids=(proposal.evidence_id,),
    )
    refs = _holdouts(m, projection, task, b0, rel0, "25-0")
    refs += _holdouts(m, projection, task, b1, rel1, "25-1")
    ticket = ExternalProjectionConditionedRelationQualifier(
        m.evidence, qualifier_id="EXTERNAL-MS2025-ROUTE3",
    ).qualify(
        route,
        qualification_evidence=tuple(refs),
        relations=m.action_outcome_learning.relations,
        min_support=12,
        min_accuracy=.95,
    )
    admitted = m.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING", admitted
    return str(admitted["binding"]["binding_id"])


def run_ms2025() -> dict:
    td, m, calls, _initial_surface, _initial_comparison, _initial_selection = _surface(True)
    try:
        ops, selection, selected = m._current_owned_referent_cross_deficit_selection_bundle(act_ob())
        assert selection.licenses_yes() and selected is not None and selected["probe_action_id"] == "P2"
        persisted = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        assert persisted["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", persisted
        weak_p4 = next(op for op in ops if op["probe_action_id"] == "P4")
        new_binding = _add_strong_current_p4_competitor(m, weak_p4)
        fresh = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        assert fresh["status"] == "NO_CURRENT_STRICT_CROSS_DEFICIT_SELECTION", fresh
        execution = m.execute_bounded_action(
            persisted["nomination"]["intent"]["intent_id"], act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(selected["trial"], decision_context=selected["decision_context"]),
        )
        assert execution["status"] == "NO_EXECUTION", execution
        assert execution["reason"] == "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION", execution
        assert calls == [], calls
        return {"status":"HISTORICAL_VIOLATION_CLOSED","law":"NOMINATION_TIME_CROSS_DEFICIT_SELECTION != EFFECT_TIME_CROSS_DEFICIT_SELECTION_CURRENTNESS","new_competitor_binding_id":new_binding,"fresh_selection":fresh,"execution_status":execution["status"],"execution_reason":execution["reason"],"handler_calls":list(calls),"cross_deficit_selection_reauthorized_at_effect":"YES"}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2025(), indent=2, sort_keys=True, default=str))
