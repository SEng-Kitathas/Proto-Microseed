import inspect

from microseed.development.discovery import DiscoveryConfig
from microseed.development.value import derive_complete_current_value_frame
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2035_organism_owned_current_value_frame_completeness import _contract
from scratch.ms2036_full_frame_bound_pareto_research import (
    _fixture,
    _p2_dominates_effects,
    _tradeoff_effects,
)


CFG = DiscoveryConfig(min_singleton_samples=5, quantization_step=0.5, min_consistency=0.99)


def test_ms2037_runtime_full_frame_tradeoff_remains_unselected_read_only():
    td, ms, calls, _by_probe, _effects = _fixture(_tradeoff_effects())
    try:
        before = (len(ms.store.events()), len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        result = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob(), config=CFG)
        after = (len(ms.store.events()), len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        assert result["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", result
        assert result["reason"] == "NO_UNIQUE_STRICT_PARETO_DOMINATOR", result
        assert result["selection_authority"] == "NONE"
        assert result["execution_authority"] == "NONE"
        assert result["complete_value_frame"]["current_value_ids"] == ["V", "W"]
        assert before == after
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2037_runtime_full_frame_dominance_selects_p2_read_only():
    td, ms, calls, _by_probe, _effects = _fixture(_p2_dominates_effects())
    try:
        before = (len(ms.store.events()), len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        result = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob(), config=CFG)
        after = (len(ms.store.events()), len(ms.epistemic_deficits.records), len(ms.action_closure.intents), len(ms.action_closure.executions))
        assert result["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", result
        assert result["reason"] == "UNIQUE_STRICT_FULL_FRAME_PARETO_DOMINATOR", result
        assert result["selected_probe_action_id"] == "P2"
        assert result["selection_authority"] == "STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY"
        assert result["execution_authority"] == "NONE"
        assert before == after
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2037_current_unobserved_value_blocks_runtime_full_frame_surface():
    td, ms, calls, _by_probe, _effects = _fixture(_p2_dominates_effects())
    try:
        ms.register_value_variable(_contract("X"))
        result = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob(), config=CFG)
        assert result["status"] == "NO_CURRENT_COMPLETE_VALUE_FRAME", result
        assert result["reason"] == "CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X", result
        assert result["selection_authority"] == "NONE"
        assert result["execution_authority"] == "NONE"
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2037_production_frame_owner_tracks_same_epoch_observation_drift():
    td, ms, calls, _by_probe, _effects = _fixture(_p2_dominates_effects())
    try:
        before = derive_complete_current_value_frame(ms.values)
        old_epoch = ms.values.epochs["W"]
        ms.observe_value_state("W", -0.75)
        after = derive_complete_current_value_frame(ms.values)
        assert ms.values.epochs["W"] == old_epoch
        assert before["frame_digest_sha256"] != after["frame_digest_sha256"]
        assert before["rows"] != after["rows"]
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def test_ms2037_public_runtime_surface_has_no_value_subset_parameter_and_same_value_surface_survives():
    from microseed.runtime.entity import Microseed

    params = tuple(inspect.signature(Microseed.derive_current_owned_referent_full_frame_cross_deficit_selection_surface).parameters)
    assert "value_ids" not in params
    assert "requested_value_ids" not in params

    td, ms, calls, _by_probe, _effects = _fixture(_tradeoff_effects())
    try:
        old = ms.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        assert old["status"] in {"NO_CURRENT_STRICT_CROSS_DEFICIT_SELECTION", "CURRENT_STRICT_SAME_VALUE_CROSS_DEFICIT_SELECTION"}
        assert old["execution_authority"] == "NONE"
        assert calls == []
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()
