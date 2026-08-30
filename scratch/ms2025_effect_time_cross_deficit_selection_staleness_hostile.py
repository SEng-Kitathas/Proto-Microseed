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
    td, m, calls, initial_surface, initial_comparison, initial_selection = _surface(True)
    try:
        assert initial_selection.licenses_yes(), initial_selection.serializable()
        persisted = persist_and_nominate_selected_current_opportunity(m, initial_surface)
        assert persisted["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", persisted
        assert persisted["selected_probe_action_id"] == "P2", persisted
        assert calls == [], calls

        selected = next(
            op for op in initial_surface["opportunities"]
            if op["deficit"].deficit_id == persisted["selected_deficit_id"]
        )
        weak_p4 = next(op for op in initial_surface["opportunities"] if op["probe_action_id"] == "P4")
        new_binding = _add_strong_current_p4_competitor(m, weak_p4)

        fresh_surface = enumerate_opportunities(m)
        assert fresh_surface["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", fresh_surface
        fresh_comparison = derive_strict_same_value_regulatory_dominance(m, fresh_surface["opportunities"])
        fresh_selection = derive_selection_commitment(fresh_comparison, fresh_surface["opportunities"])
        assert not fresh_selection.licenses_yes(), fresh_selection.serializable()
        assert fresh_comparison["status"] == "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE", fresh_comparison
        assert fresh_comparison["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", fresh_comparison

        execution = m.execute_bounded_action(
            persisted["nomination"]["intent"]["intent_id"],
            act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                selected["trial"], decision_context=selected["decision_context"],
            ),
        )
        # This campaign intentionally proves the stale-selection leak if ordinary
        # local reauthorization still executes P2 after cross-deficit uniqueness died.
        assert execution["status"] == "ACTION_EXECUTED", execution
        assert calls == ["P2"], calls
        return {
            "status": "VIOLATION_REPRODUCED",
            "law": "NOMINATION_TIME_CROSS_DEFICIT_SELECTION != EFFECT_TIME_CROSS_DEFICIT_SELECTION_CURRENTNESS",
            "selected_probe_at_nomination": "P2",
            "new_competitor_binding_id": new_binding,
            "fresh_surface_status": fresh_surface["status"],
            "fresh_probe_action_ids": list(fresh_surface["probe_action_ids"]),
            "fresh_comparison": fresh_comparison,
            "fresh_selection": fresh_selection.serializable(),
            "execution_status": execution["status"],
            "handler_calls": list(calls),
            "local_selected_deficit_remained_current": "YES",
            "cross_deficit_selection_reauthorized_at_effect": "NO",
        }
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


if __name__ == "__main__":
    print(json.dumps(run_ms2025(), indent=2, sort_keys=True, default=str))
