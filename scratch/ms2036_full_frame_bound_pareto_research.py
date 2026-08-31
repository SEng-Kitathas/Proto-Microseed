from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.discovery import DiscoveryConfig, OperationalTrace
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface
from scratch.ms2033_cross_value_epistemic_consequence_vector_construction import (
    _episode,
    _frame,
    _value_w,
    derive_cross_value_epistemic_consequence_vector,
)
from scratch.ms2034_pareto_value_frame_completeness_authority_blocker import (
    derive_strict_pareto_selection_from_vector_rows,
)
from scratch.ms2035_organism_owned_current_value_frame_completeness import (
    _contract,
    current_value_frame_is_current,
    derive_complete_current_value_frame,
    vector_matches_complete_value_frame,
)


def _seed_effects(ms, effects: dict[tuple[str, str], float]) -> None:
    if "W" not in ms.values.contracts:
        ms.register_value_variable(_value_w())
        ms.observe_value_state("W", -1.0)
    for value_id in ("V", "W"):
        frame_id = f"F-MS2036-{value_id}"
        schema_id = f"E-MS2036-{value_id}"
        if frame_id not in ms.frames.contracts:
            ms.register_operational_frame(_frame(frame_id))
        if schema_id not in ms.episodes.contracts:
            ms.register_episode_schema(_episode(schema_id, frame_id, value_id))
    for (action_id, value_id), effect in effects.items():
        for sample in range(7):
            ms.record_operational_trace(OperationalTrace(
                trace_id=f"MS2036-{action_id}-{value_id}-{sample}",
                steps=(action_id,), step_effects=((float(effect),),),
                frame_id=f"F-MS2036-{value_id}",
                episode_schema_id=f"E-MS2036-{value_id}",
            ))


def _effect_surface(ms) -> dict[str, dict]:
    result = ms.derive_multi_value_action_licenses(
        ("V", "W"),
        config=DiscoveryConfig(min_singleton_samples=5, quantization_step=0.5, min_consistency=0.99),
    )
    return dict(result["effect_witnesses"])


def derive_full_frame_bound_cross_value_vectors(ms, opportunities: tuple[dict, ...], effect_witnesses: dict[str, dict]) -> dict:
    """Research-only lawful vector surface with no caller coordinate scope."""
    frame = derive_complete_current_value_frame(ms.values)
    base = {
        "selection_authority": "NONE",
        "execution_authority": "NONE",
        "truth_authority": "NONE",
        "semantic_goal_authority": "NONE",
        "semantic_value_priority_authority": "NONE",
        "persistence": "NONE",
    }
    if frame.get("status") != "CURRENT_COMPLETE_VALUE_FRAME":
        return {**base, "status": "DEFER_UNKNOWN", "reason": "COMPLETE_CURRENT_VALUE_FRAME_REQUIRED", "frame": frame}
    value_ids = tuple(str(x) for x in frame["current_value_ids"])
    vectors = []
    for opportunity in opportunities:
        vector = derive_cross_value_epistemic_consequence_vector(
            opportunity=opportunity,
            values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs),
            effect_witnesses=effect_witnesses,
            requested_value_ids=value_ids,
        )
        if vector.get("status") != "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR":
            return {**base, "status": "DEFER_UNKNOWN", "reason": "COMPLETE_CURRENT_VECTOR_REQUIRED", "frame": frame, "vector": vector}
        match = vector_matches_complete_value_frame(vector, frame)
        if not match.get("frame_match"):
            return {**base, "status": "DEFER_UNKNOWN", "reason": "VECTOR_MUST_MATCH_COMPLETE_CURRENT_VALUE_FRAME", "frame": frame, "vector": vector}
        vector = dict(vector)
        vector["complete_value_frame_digest_sha256"] = frame["frame_digest_sha256"]
        vectors.append(vector)
    return {
        **base,
        "status": "CURRENT_FULL_FRAME_BOUND_CROSS_VALUE_VECTORS",
        "reason": "ALL_VECTORS_MATCH_ORGANISM_OWNED_COMPLETE_CURRENT_VALUE_FRAME",
        "frame": frame,
        "vectors": vectors,
    }


def derive_current_full_frame_strict_pareto_selection(ms, vector_surface: dict) -> dict:
    base = {
        "execution_authority": "NONE",
        "truth_authority": "NONE",
        "semantic_goal_authority": "NONE",
        "semantic_value_priority_authority": "NONE",
        "persistence": "NONE",
    }
    if vector_surface.get("status") != "CURRENT_FULL_FRAME_BOUND_CROSS_VALUE_VECTORS":
        return {**base, "status": "DEFER_UNKNOWN", "reason": "FULL_FRAME_BOUND_VECTORS_REQUIRED", "research_selection_authority": "NONE"}
    frame = vector_surface["frame"]
    currentness = current_value_frame_is_current(ms.values, frame)
    if not currentness.get("frame_current"):
        return {**base, "status": "DEFER_UNKNOWN", "reason": "COMPLETE_VALUE_FRAME_NOT_CURRENT_AT_SELECTION", "research_selection_authority": "NONE", "frame_currentness": currentness}
    for vector in vector_surface["vectors"]:
        if not vector_matches_complete_value_frame(vector, frame).get("frame_match"):
            return {**base, "status": "DEFER_UNKNOWN", "reason": "VECTOR_FRAME_DRIFT_AT_SELECTION", "research_selection_authority": "NONE"}
    result = dict(derive_strict_pareto_selection_from_vector_rows(tuple(vector_surface["vectors"])))
    result["complete_value_frame_digest_sha256"] = frame["frame_digest_sha256"]
    return result


def _fixture(effects: dict[tuple[str, str], float]):
    td, ms, calls, *_ = _surface(True)
    _seed_effects(ms, effects)
    opportunities = ms.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
    by_probe = {row["probe_action_id"]: row for row in opportunities["opportunities"]}
    return td, ms, calls, by_probe, _effect_surface(ms)


def _tradeoff_effects() -> dict[tuple[str, str], float]:
    return {
        ("A", "V"): 2.0, ("B", "V"): 2.0,
        ("A", "W"): 0.5, ("B", "W"): 0.5,
        ("D", "V"): 0.5, ("C", "V"): 0.5,
        ("D", "W"): 2.0, ("C", "W"): 2.0,
    }


def _p2_dominates_effects() -> dict[tuple[str, str], float]:
    return {
        ("A", "V"): 2.0, ("B", "V"): 2.0,
        ("A", "W"): 2.0, ("B", "W"): 2.0,
        ("D", "V"): 0.5, ("C", "V"): 0.5,
        ("D", "W"): 0.5, ("C", "W"): 0.5,
    }


def run_tradeoff() -> dict:
    td, ms, calls, by_probe, effects = _fixture(_tradeoff_effects())
    try:
        before = len(ms.store.events())
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        selection = derive_current_full_frame_strict_pareto_selection(ms, surface)
        reverse = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P4"], by_probe["P2"]), effects)
        reverse_selection = derive_current_full_frame_strict_pareto_selection(ms, reverse)
        after = len(ms.store.events())
        by_probe_vec = {v["probe_action_id"]: v for v in surface["vectors"]}
        assert by_probe_vec["P2"]["worst_residual_by_value"] == {"V": 0.0, "W": 0.5}, by_probe_vec
        assert by_probe_vec["P4"]["worst_residual_by_value"] == {"V": 0.5, "W": 0.0}, by_probe_vec
        assert selection["status"] == "NO_STRICT_PARETO_SELECTION", selection
        assert reverse_selection["status"] == selection["status"]
        assert reverse_selection["reason"] == selection["reason"]
        assert before == after and calls == []
        return {"status": "PASS", "surface": surface, "selection": selection, "read_only": before == after, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_dominance() -> dict:
    td, ms, calls, by_probe, effects = _fixture(_p2_dominates_effects())
    try:
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        selection = derive_current_full_frame_strict_pareto_selection(ms, surface)
        by_probe_vec = {v["probe_action_id"]: v for v in surface["vectors"]}
        assert by_probe_vec["P2"]["worst_residual_by_value"] == {"V": 0.0, "W": 0.0}, by_probe_vec
        assert by_probe_vec["P4"]["worst_residual_by_value"] == {"V": 0.5, "W": 0.5}, by_probe_vec
        assert selection["status"] == "CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY", selection
        assert selection["selected_probe_action_id"] == "P2", selection
        assert selection["research_selection_authority"] == "STRICT_PARETO_REGULATORY_DOMINANCE_ONLY"
        assert calls == []
        return {"status": "PASS", "surface": surface, "selection": selection, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_new_value_stales_selection() -> dict:
    td, ms, calls, by_probe, effects = _fixture(_p2_dominates_effects())
    try:
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        ms.register_value_variable(_contract("X")); ms.observe_value_state("X", 1.0)
        selection = derive_current_full_frame_strict_pareto_selection(ms, surface)
        assert selection["status"] == "DEFER_UNKNOWN", selection
        assert selection["reason"] == "COMPLETE_VALUE_FRAME_NOT_CURRENT_AT_SELECTION", selection
        assert calls == []
        return {"status": "PASS", "selection": selection, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_same_epoch_observation_stales_selection() -> dict:
    td, ms, calls, by_probe, effects = _fixture(_p2_dominates_effects())
    try:
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        old_epoch = int(ms.values.epochs["W"])
        ms.observe_value_state("W", -0.75)
        assert int(ms.values.epochs["W"]) == old_epoch
        selection = derive_current_full_frame_strict_pareto_selection(ms, surface)
        assert selection["status"] == "DEFER_UNKNOWN", selection
        assert selection["reason"] == "COMPLETE_VALUE_FRAME_NOT_CURRENT_AT_SELECTION", selection
        assert calls == []
        return {"status": "PASS", "selection": selection, "handler_calls": list(calls), "epoch_unchanged": True}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_missing_observation_blocks_vectors() -> dict:
    td, ms, calls, by_probe, effects = _fixture(_p2_dominates_effects())
    try:
        ms.register_value_variable(_contract("X"))
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        assert surface["status"] == "DEFER_UNKNOWN", surface
        assert surface["reason"] == "COMPLETE_CURRENT_VALUE_FRAME_REQUIRED", surface
        assert surface["frame"]["reason"] == "CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X"
        assert calls == []
        return {"status": "PASS", "surface": surface, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_missing_effect_blocks_vectors() -> dict:
    effects_map = _p2_dominates_effects(); effects_map.pop(("B", "W"))
    td, ms, calls, by_probe, effects = _fixture(effects_map)
    try:
        surface = derive_full_frame_bound_cross_value_vectors(ms, (by_probe["P2"], by_probe["P4"]), effects)
        assert surface["status"] == "DEFER_UNKNOWN", surface
        assert surface["reason"] == "COMPLETE_CURRENT_VECTOR_REQUIRED", surface
        assert surface["vector"]["reason"] == "CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:B:W"
        assert calls == []
        return {"status": "PASS", "surface": surface, "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_api_has_no_caller_frame_parameter() -> dict:
    params = tuple(inspect.signature(derive_full_frame_bound_cross_value_vectors).parameters)
    assert "requested_value_ids" not in params
    assert "value_ids" not in params
    return {"status": "PASS", "parameters": list(params), "caller_frame_parameter": "ABSENT"}


def run_ms2036() -> dict:
    return {
        "status": "FULL_FRAME_BOUND_STRICT_PARETO_EARNED_RESEARCH_ONLY",
        "tradeoff": run_tradeoff(),
        "dominance": run_dominance(),
        "new_value_staleness": run_new_value_stales_selection(),
        "same_epoch_observation_staleness": run_same_epoch_observation_stales_selection(),
        "missing_observation": run_missing_observation_blocks_vectors(),
        "missing_effect": run_missing_effect_blocks_vectors(),
        "api_scope": run_api_has_no_caller_frame_parameter(),
        "earned": "CROSS_VALUE_STRICT_PARETO_COMPARISON_IS_LAWFUL_ONLY_OVER_ORGANISM_OWNED_COMPLETE_CURRENT_VALUE_FRAME",
        "currentness_law": "FULL_FRAME_CURRENTNESS_MUST_BE_REDERIVED_BEFORE_CROSS_VALUE_SELECTION",
        "runtime_selection_authorized": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2036(), indent=2, sort_keys=True, default=str))
