from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, EpisodeSchemaContract, OperationalFrameContract, QualificationState, ValueVariableContract
from microseed.development.discovery import DiscoveryConfig, OperationalTrace
from microseed.development.value import residual_pressure_after_effect
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface


REQUESTED_VALUES = ("V", "W")


def _value_w() -> ValueVariableContract:
    return ValueVariableContract(
        "W", "opaque-second-regulatory-coordinate", 0.0, 10.0,
        hashlib.sha256(b"MS2033-W:0:10").hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS2033",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("MS2033_CURRENT_SECOND_VALUE_COORDINATE",),
    )


def _frame(frame_id: str) -> OperationalFrameContract:
    return OperationalFrameContract(
        frame_id, "opaque-ms2033-effect-frame", hashlib.sha256(frame_id.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS2033",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def _episode(schema_id: str, frame_id: str, value_id: str) -> EpisodeSchemaContract:
    return EpisodeSchemaContract(
        schema_id, "opaque-ms2033-single-value-effect-binding", hashlib.sha256(schema_id.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS2033",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=((frame_id, 0),), value_epochs=((value_id, 0),),
    )


def _seed_effect_support(ms, *, include_b_w: bool = True, conflicting_a_w: bool = False) -> None:
    # Existing MS2023 fixture already has frame F, value V and capabilities A/B/C/D/P2/P4.
    ms.register_value_variable(_value_w())
    ms.observe_value_state("W", -1.0)

    # Use dedicated current frames/episode schemas so effect ancestry is explicit and
    # independent from the V-bound epistemic rehearsal relation sets.
    for value_id in REQUESTED_VALUES:
        frame_id = f"F-MS2033-{value_id}"
        ms.register_operational_frame(_frame(frame_id))
        ms.register_episode_schema(_episode(f"E-MS2033-{value_id}", frame_id, value_id))

    # P2 branches A/B are better on V but worse on W. P4 branches D/C are reverse.
    effects = {
        ("A", "V"): 2.0, ("B", "V"): 2.0,
        ("A", "W"): 0.5, ("B", "W"): 0.5,
        ("D", "V"): 0.5, ("C", "V"): 0.5,
        ("D", "W"): 2.0, ("C", "W"): 2.0,
        # Deliberately large immediate probe effect: vector construction must ignore it.
        ("P2", "W"): -5.0,
    }
    if not include_b_w:
        effects.pop(("B", "W"))

    for (capability_id, value_id), effect in effects.items():
        frame_id = f"F-MS2033-{value_id}"
        schema_id = f"E-MS2033-{value_id}"
        for sample in range(7):
            ms.record_operational_trace(OperationalTrace(
                trace_id=f"MS2033-{capability_id}-{value_id}-{sample}",
                steps=(capability_id,), step_effects=((effect,),),
                frame_id=frame_id, episode_schema_id=schema_id,
            ))

    if conflicting_a_w:
        ms.register_operational_frame(_frame("F-MS2033-W-ALT"))
        ms.register_episode_schema(_episode("E-MS2033-W-ALT", "F-MS2033-W-ALT", "W"))
        for sample in range(7):
            ms.record_operational_trace(OperationalTrace(
                trace_id=f"MS2033-A-W-ALT-{sample}", steps=("A",), step_effects=((3.0,),),
                frame_id="F-MS2033-W-ALT", episode_schema_id="E-MS2033-W-ALT",
            ))


def _effect_surface(ms) -> dict[str, dict]:
    result = ms.derive_multi_value_action_licenses(
        REQUESTED_VALUES,
        config=DiscoveryConfig(min_singleton_samples=5, quantization_step=0.5, min_consistency=0.99),
    )
    return dict(result["effect_witnesses"])


def derive_cross_value_epistemic_consequence_vector(
    *,
    opportunity: dict,
    values,
    current_capability_epochs: dict[str, int],
    effect_witnesses: dict[str, dict],
    requested_value_ids: tuple[str, ...],
) -> dict:
    """Research-only composition of branch-conditioned downstream residual vectors.

    The only branch/action identity comes from the current epistemic consequence
    surface. Coordinate effects come from separately bound current singleton trace
    witnesses. No comparator, persistence, selection, or execution is performed.
    """
    base = {
        "selection_authority": "NONE", "execution_authority": "NONE",
        "truth_authority": "NONE", "semantic_goal_authority": "NONE",
        "semantic_value_priority_authority": "NONE", "persistence": "NONE",
    }
    consequence = dict(opportunity.get("consequence") or {})
    if consequence.get("status") != "CURRENT_SAME_VALUE_REGULATORY_CONSEQUENCE_SURFACE":
        return {**base, "status": "DEFER_UNKNOWN", "reason": "CURRENT_EPISTEMIC_CONSEQUENCE_REQUIRED"}
    actions = tuple(str(x) for x in consequence.get("first_actions", ()))
    proposal_digests = tuple(str(x) for x in consequence.get("proposal_digests", ()))
    if len(actions) < 2 or len(actions) != len(proposal_digests):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "BRANCH_ACTION_IDENTITY_REQUIRED"}

    value_rows: dict[str, dict] = {}
    branch_rows: list[dict] = []
    premise_ids: set[str] = {
        str(consequence.get("decision_bearing_commitment_id", "")),
        *proposal_digests,
    }
    premise_ids.discard("")

    for value_id in tuple(str(x) for x in requested_value_ids):
        if not values.is_current(value_id):
            return {**base, "status": "DEFER_UNKNOWN", "reason": f"VALUE_NOT_CURRENT:{value_id}"}
        latest = values.latest.get(value_id)
        contract = values.contracts.get(value_id)
        if latest is None or contract is None or int(latest[0]) != int(values.epochs[value_id]):
            return {**base, "status": "DEFER_UNKNOWN", "reason": f"CURRENT_VALUE_OBSERVATION_REQUIRED:{value_id}"}
        value_rows[value_id] = {
            "value_id": value_id,
            "value_epoch": int(values.epochs[value_id]),
            "current_value": float(latest[1]),
            "contract_signature_sha256": str(contract.signature_sha256),
        }
        premise_ids.add(f"{value_id}@{values.epochs[value_id]}")

    for branch_index, (action_id, proposal_digest) in enumerate(zip(actions, proposal_digests)):
        residuals: dict[str, float] = {}
        effect_sources: dict[str, list[str]] = {}
        for value_id in requested_value_ids:
            key = f"{action_id}::{value_id}"
            row = effect_witnesses.get(key)
            if row is None:
                return {**base, "status": "DEFER_UNKNOWN", "reason": f"CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:{action_id}:{value_id}"}
            if row.get("status") != "CURRENT_EFFECT":
                return {**base, "status": "DEFER_UNKNOWN", "reason": f"DOWNSTREAM_ACTION_VALUE_EFFECT_UNRESOLVED:{action_id}:{value_id}:{row.get('status')}"}
            if int(row.get("value_epoch", -1)) != int(values.epochs[value_id]):
                return {**base, "status": "DEFER_UNKNOWN", "reason": f"DOWNSTREAM_ACTION_VALUE_EPOCH_DRIFT:{action_id}:{value_id}"}
            if int(row.get("capability_epoch", -1)) != int(current_capability_epochs.get(action_id, -2)):
                return {**base, "status": "DEFER_UNKNOWN", "reason": f"DOWNSTREAM_ACTION_CAPABILITY_EPOCH_DRIFT:{action_id}"}
            latest = values.latest[value_id]
            contract = values.contracts[value_id]
            residuals[value_id] = float(residual_pressure_after_effect(contract, float(latest[1]), float(row["effect"])))
            sources = [str(x) for x in row.get("source_trace_ids", ())]
            effect_sources[value_id] = sources
            premise_ids.update(sources)
        branch_rows.append({
            "branch_index": branch_index,
            "proposal_digest": proposal_digest,
            "downstream_action_id": action_id,
            "residual_by_value": residuals,
            "effect_source_trace_ids_by_value": effect_sources,
        })

    worst = {
        value_id: max(float(branch["residual_by_value"][value_id]) for branch in branch_rows)
        for value_id in requested_value_ids
    }
    return {
        **base,
        "status": "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR",
        "deficit_id": str(opportunity.get("deficit_id")),
        "probe_action_id": str(opportunity.get("probe_action_id")),
        "requested_value_ids": list(requested_value_ids),
        "value_rows": value_rows,
        "branches": branch_rows,
        "worst_residual_by_value": worst,
        "premise_ids": sorted(premise_ids),
        "construction_authority": "DERIVED_READ_ONLY_ONLY",
    }


def _complete_fixture():
    td, ms, calls, *_ = _surface(True)
    _seed_effect_support(ms)
    opportunities = ms.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
    assert opportunities["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", opportunities
    by_probe = {row["probe_action_id"]: row for row in opportunities["opportunities"]}
    effects = _effect_surface(ms)
    return td, ms, calls, by_probe, effects


def run_complete_tradeoff() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        before = len(ms.store.events())
        p2 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effects, requested_value_ids=REQUESTED_VALUES,
        )
        p4 = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P4"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effects, requested_value_ids=REQUESTED_VALUES,
        )
        after = len(ms.store.events())
        assert p2["status"] == p4["status"] == "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR", (p2, p4)
        assert p2["worst_residual_by_value"] == {"V": 0.0, "W": 0.5}, p2
        assert p4["worst_residual_by_value"] == {"V": 0.5, "W": 0.0}, p4
        assert {x["downstream_action_id"] for x in p2["branches"]} == {"A", "B"}
        assert {x["downstream_action_id"] for x in p4["branches"]} == {"C", "D"}
        assert all("P2" not in src for branch in p2["branches"] for ids in branch["effect_source_trace_ids_by_value"].values() for src in ids)
        assert "P2::W" in effects and float(effects["P2::W"]["effect"]) == -5.0
        assert before == after
        assert calls == []
        return {
            "status": "PASS",
            "p2": p2, "p4": p4,
            "tradeoff": "P2_BETTER_V__P4_BETTER_W",
            "cross_value_selection_authority": "NONE",
            "read_only": before == after,
            "handler_calls": list(calls),
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_missing_witness() -> dict:
    td, ms, calls, *_ = _surface(True)
    try:
        _seed_effect_support(ms, include_b_w=False)
        opps = ms.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        p2 = next(row for row in opps["opportunities"] if row["probe_action_id"] == "P2")
        result = derive_cross_value_epistemic_consequence_vector(
            opportunity=p2, values=ms.values, current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=_effect_surface(ms), requested_value_ids=REQUESTED_VALUES,
        )
        assert result["status"] == "DEFER_UNKNOWN", result
        assert result["reason"] == "CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:B:W", result
        assert calls == []
        return {"status": "PASS", "result": result, "zero_fill": "NO", "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ambiguous_ancestry() -> dict:
    td, ms, calls, *_ = _surface(True)
    try:
        _seed_effect_support(ms, conflicting_a_w=True)
        opps = ms.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        p2 = next(row for row in opps["opportunities"] if row["probe_action_id"] == "P2")
        effects = _effect_surface(ms)
        assert effects["A::W"]["status"] == "UNKNOWN_MULTIPLE_CURRENT_ANCESTRY_SHAPES", effects["A::W"]
        result = derive_cross_value_epistemic_consequence_vector(
            opportunity=p2, values=ms.values, current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effects, requested_value_ids=REQUESTED_VALUES,
        )
        assert result["status"] == "DEFER_UNKNOWN", result
        assert result["reason"].startswith("DOWNSTREAM_ACTION_VALUE_EFFECT_UNRESOLVED:A:W:UNKNOWN_MULTIPLE_CURRENT_ANCESTRY_SHAPES"), result
        assert calls == []
        return {"status": "PASS", "result": result, "ancestry_averaging": "NO", "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_value_drift() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        ms.values.change("W", reason="MS2033_VALUE_DRIFT")
        result = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values, current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effects, requested_value_ids=REQUESTED_VALUES,
        )
        assert result["status"] == "DEFER_UNKNOWN", result
        assert result["reason"] == "VALUE_NOT_CURRENT:W", result
        assert calls == []
        return {"status": "PASS", "result": result, "old_effect_witness_reuse": "REJECTED", "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2033() -> dict:
    return {
        "status": "COMPOSITIONAL_VECTOR_CONSTRUCTION_EARNED_RESEARCH_ONLY",
        "complete_tradeoff": run_complete_tradeoff(),
        "missing_witness": run_missing_witness(),
        "ambiguous_ancestry": run_ambiguous_ancestry(),
        "value_drift": run_value_drift(),
        "new_core_owner_required": "NO_EVIDENCE",
        "pareto_comparator_authorized": "NO",
        "cross_value_selection_authority": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2033(), indent=2, sort_keys=True, default=str))
