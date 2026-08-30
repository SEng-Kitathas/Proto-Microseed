from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, CapabilityContract, EpistemicStatus, QualificationState
from microseed.development.action_learning import ExternalProjectionConditionedRelationQualifier
from microseed.development.epistemic_action import derive_current_grounded_feasibility_surface
from microseed.development.rehearsal import CounterfactualRehearsalConfig, propose_counterfactual_rehearsal
from scratch.ms2005_bounded_referent_probe_reconstruction import _persist_context
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _relation
from scratch.ms2021_cross_deficit_selection_blocker_replayed_with_raw_contrast import (
    P4_D,
    _holdouts,
    _second_same_state_binding,
    _setup_same_state_owned_prefix,
    enumerate_opportunities,
)


def _regulatory_summary(m, opportunity: dict) -> dict:
    deficit = opportunity["deficit"]
    anchors = tuple(a for a in deficit.premise_anchors if a.kind == "VALUE")
    if len(anchors) != 1:
        return {"status": "DEFER_UNKNOWN", "reason": "EXACT_SINGLE_VALUE_ANCHOR_REQUIRED"}
    anchor = anchors[0]
    if not m.values.is_current(anchor.object_id, anchor.epoch):
        return {"status": "DEFER_UNKNOWN", "reason": "VALUE_ANCHOR_NOT_CURRENT"}
    latest = m.values.latest.get(anchor.object_id)
    if latest is None or latest[0] != anchor.epoch:
        return {"status": "DEFER_UNKNOWN", "reason": "CURRENT_VALUE_OBSERVATION_REQUIRED"}
    contract = m.values.contracts[anchor.object_id]
    options, _ = derive_current_grounded_feasibility_surface(
        capabilities=m.capabilities, operational_scope_id="S",
    )
    proposals = []
    for rows in opportunity["decision_context"].relation_sets:
        relations = {(r.state_id, r.capability_id): r for r in rows}
        proposal = propose_counterfactual_rehearsal(
            relations,
            start_state_id=opportunity["trial"].start_state_id,
            start_value=float(latest[1]),
            viable_low=float(contract.viable_low),
            viable_high=float(contract.viable_high),
            value_epoch=(anchor.object_id, anchor.epoch),
            options=options,
            cfg=CounterfactualRehearsalConfig(max_horizon=1, max_nodes=64, min_support=1, min_consistency=0.99),
        )
        if proposal is None or not proposal.sequence:
            return {"status": "DEFER_UNKNOWN", "reason": "ALTERNATIVE_REHEARSAL_UNRESOLVED"}
        proposals.append(proposal)
    return {
        "status": "CURRENT_SAME_VALUE_REGULATORY_CONSEQUENCE_SURFACE",
        "value_id": anchor.object_id,
        "value_epoch": anchor.epoch,
        "current_value": float(latest[1]),
        "probe_action_id": opportunity["probe_action_id"],
        "first_actions": tuple(p.sequence[0] for p in proposals),
        "residual_pressures": tuple(float(p.residual_pressure) for p in proposals),
        "worst_residual_pressure": max(float(p.residual_pressure) for p in proposals),
        "proposal_digests": tuple(p.digest() for p in proposals),
        "selection_authority": "NONE",
        "execution_authority": "NONE",
    }


def derive_strict_same_value_regulatory_dominance(m, opportunities) -> dict:
    rows = tuple((op, _regulatory_summary(m, op)) for op in opportunities)
    if len(rows) < 2:
        return {"status": "NO_CROSS_DEFICIT_COMPARISON_REQUIRED", "selection_authority": "NONE"}
    if any(summary.get("status") != "CURRENT_SAME_VALUE_REGULATORY_CONSEQUENCE_SURFACE" for _, summary in rows):
        return {"status": "DEFER_UNKNOWN", "reason": "CURRENT_REGULATORY_CONSEQUENCE_SURFACE_REQUIRED", "selection_authority": "NONE"}
    coordinates = {(s["value_id"], int(s["value_epoch"]), float(s["current_value"])) for _, s in rows}
    if len(coordinates) != 1:
        return {
            "status": "CROSS_DEFICIT_REGULATORY_COMPARISON_UNOWNED",
            "reason": "EXACT_SAME_VALUE_COORDINATE_REQUIRED",
            "selection_authority": "NONE",
        }
    ranked = sorted(
        ((float(summary["worst_residual_pressure"]), str(op["probe_action_id"]), op, summary) for op, summary in rows),
        key=lambda x: (x[0], x[1]),
    )
    best = ranked[0][0]
    winners = tuple(x for x in ranked if x[0] == best)
    if len(winners) != 1:
        return {
            "status": "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE",
            "reason": "WORST_RESIDUAL_PRESSURE_TIE",
            "opportunities": tuple(summary for _, summary in rows),
            "selection_authority": "NONE",
            "execution_authority": "NONE",
        }
    second = ranked[1][0]
    if not best < second:
        return {
            "status": "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE",
            "reason": "NO_STRICT_RESIDUAL_PRESSURE_ORDER",
            "selection_authority": "NONE",
        }
    winner = winners[0]
    return {
        "status": "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_QUARRY",
        "dominant_probe_action_id": winner[1],
        "dominant_worst_residual_pressure": winner[0],
        "next_worst_residual_pressure": second,
        "opportunities": tuple(summary for _, summary in rows),
        "comparison_basis": "EXACT_SAME_VALUE_COORDINATE__STRICT_WORST_RESIDUAL_PRESSURE_ONLY",
        "selection_authority": "NONE__RESEARCH_QUARRY_ONLY",
        "execution_authority": "NONE",
        "truth_authority": "NONE",
    }


def _second_asymmetric_binding(m, projection, bucket_a: str, bucket_d: str) -> str:
    for cid in ("C", "D", "P4"):
        m.register_capability(CapabilityContract(
            cid, "opaque", {}, {}, (), (), Authority.EFFECT, ("MS2022",), "CURRENT", {},
            query_obligation_id="MS2008-ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _cid=cid, **_: {"receipt": _cid}, operational_scope_id="S",
        ))
        m.register_capability(CapabilityContract(
            "FEAS-" + cid, "feas", {"target_capability_id": cid}, {}, (), (),
            Authority.DERIVED_READ_ONLY, ("MS2022",), "CURRENT", {}, dependencies=(cid,),
            query_obligation_id="MS2008-FEAS-" + cid,
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"feasibility": "FEASIBLE", "reason": "CURRENT"},
            operational_scope_id="S",
        ))
    rel_a = {
        "C": _relation(m, "MS2022-A-C", "C", "c-next", 0.5, "22AC"),
        "D": _relation(m, "MS2022-A-D", "D", "d-next", 0.0, "22AD"),
        "P4": _relation(m, "MS2022-A-P4", "P4", "s0", 0.0, "22AP"),
    }
    rel_d = {
        "C": _relation(m, "MS2022-D-C", "C", "c-next-d", 0.0, "22DC"),
        "D": _relation(m, "MS2022-D-D", "D", "d-next-d", 0.5, "22DD"),
        "P4": _relation(m, "MS2022-D-P4", "P4", "s0", 0.0, "22DP"),
    }
    proposal_evidence = m.append_evidence(
        "MS2022-ROUTE2-PROP",
        {"kind": "ROUTING_PROPOSAL", "basis": "SECOND_PARTIAL_RELIEF_REFERENT_PRESSURE"},
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="MS2022",
    )
    route = m.nominate_projection_conditioned_relation_routing(
        projection_id=projection.projection_id,
        task_id="MS2022-DECISION-2",
        action_ids=("C", "D", "P4"),
        channel_ids=("opaque-control",),
        horizon=1,
        default_action_relations=tuple((a, rel_a[a].relation_id) for a in ("C", "D", "P4")),
        bucket_action_overrides=tuple((bucket_d, a, rel_d[a].relation_id) for a in ("C", "D", "P4")),
        source_evidence_ids=(proposal_evidence.evidence_id,),
    )
    refs = _holdouts(m, projection, "MS2022-DECISION-2", bucket_a, rel_a, "A")
    refs += _holdouts(m, projection, "MS2022-DECISION-2", bucket_d, rel_d, "D")
    ticket = ExternalProjectionConditionedRelationQualifier(m.evidence, qualifier_id="EXTERNAL-MS2022-ROUTE2").qualify(
        route,
        qualification_evidence=tuple(refs),
        relations=m.action_outcome_learning.relations,
        min_support=12,
        min_accuracy=.95,
    )
    admitted = m.qualify_projection_conditioned_relation_routing(ticket)
    assert admitted["status"] == "CURRENT_PROJECTION_CONDITIONED_ROUTING", admitted
    return str(admitted["binding"]["binding_id"])


def run_symmetric() -> dict:
    td, m, calls, world, binding1, bucket_a, bucket_b = _setup_same_state_owned_prefix()
    try:
        bucket_d = str(_persist_context(m, "MS2022-SYM-D", P4_D)["projection_bucket_id"])
        projection = m.epistemic_projections.records[m.action_outcome_learning.projection_conditioned_bindings[binding1].projection_id]
        _second_same_state_binding(m, projection, bucket_a, bucket_d)
        surface = enumerate_opportunities(m)
        assert surface["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", surface
        comparison = derive_strict_same_value_regulatory_dominance(m, surface["opportunities"])
        assert comparison["status"] == "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE", comparison
        assert comparison["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", comparison
        assert calls == [], calls
        return {"status": "PASS", "comparison": comparison, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric() -> dict:
    td, m, calls, world, binding1, bucket_a, bucket_b = _setup_same_state_owned_prefix()
    try:
        bucket_d = str(_persist_context(m, "MS2022-ASYM-D", P4_D)["projection_bucket_id"])
        projection = m.epistemic_projections.records[m.action_outcome_learning.projection_conditioned_bindings[binding1].projection_id]
        _second_asymmetric_binding(m, projection, bucket_a, bucket_d)
        surface = enumerate_opportunities(m)
        assert surface["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", surface
        comparison = derive_strict_same_value_regulatory_dominance(m, surface["opportunities"])
        assert comparison["status"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_QUARRY", comparison
        assert comparison["dominant_probe_action_id"] == "P2", comparison
        assert comparison["dominant_worst_residual_pressure"] == 0.0, comparison
        assert comparison["next_worst_residual_pressure"] == 0.5, comparison
        assert calls == [], calls
        return {"status": "PASS", "comparison": comparison, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2022() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric": run_asymmetric(),
        "existing_rehearsal_value_content_sufficient_for_narrow_comparison": "YES",
        "new_scheduler_required": "NO",
        "new_weighted_utility_required": "NO",
        "selection_authority": "NONE__QUARRY_ONLY",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2022(), indent=2, sort_keys=True, default=str))
