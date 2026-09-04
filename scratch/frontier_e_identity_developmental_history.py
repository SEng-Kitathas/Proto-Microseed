from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, Observation
from scratch.ms2009_owned_current_referent_probe_prefix import (
    World,
    build,
    derive_current_owned_probe_prefix,
    produce_prefix,
    record_raw,
)


def _close(ms) -> None:
    for obj in (getattr(ms, "biography", None), getattr(ms, "evidence", None), getattr(ms, "store", None)):
        try:
            if hasattr(obj, "conn"):
                obj.conn.close()
            elif hasattr(obj, "close"):
                obj.close()
        except Exception:
            pass


def _current_surface(ms, derived: dict[str, Any]) -> dict[str, Any]:
    current = ms.action_closure.current_state
    if current is None:
        raise AssertionError("CURRENT_CONTROL_STATE_REQUIRED")
    return {
        "control_state_id": current.state_id,
        "control_state_authority": current.authority,
        "capability_epochs": dict(sorted(ms.capabilities.epochs.items())),
        "frame_epochs": dict(sorted(ms.frames.epochs.items())),
        "episode_epochs": dict(sorted(ms.episodes.epochs.items())),
        "value_snapshot": ms.values.snapshot(),
        "current_raw_sample": list(derived["raw_samples"][-1]),
    }


def _historyful(root: Path) -> tuple[Any, dict[str, Any]]:
    world = World()
    first = produce_prefix(root, world)
    try:
        before = derive_current_owned_probe_prefix(first, max_steps=2)
        assert before["status"] == "CURRENT_OWNED_OPAQUE_PROBE_PREFIX", before
        assert before["opaque_action_sequence"] == ("P0", "P1"), before
    finally:
        _close(first)

    restarted_world = World()
    restarted_world.index = 2
    restarted_world.value = 2.0
    restarted = build(root, restarted_world)
    derived = derive_current_owned_probe_prefix(restarted, max_steps=2)
    assert derived["status"] == "CURRENT_OWNED_OPAQUE_PROBE_PREFIX", derived
    assert derived["opaque_action_sequence"] == ("P0", "P1"), derived
    assert derived["step_count"] == 2, derived
    return restarted, derived


def _fresh_current(root: Path) -> tuple[Any, dict[str, Any]]:
    world = World()
    world.index = 2
    world.value = 2.0
    first = build(root, world)
    try:
        first.observe_value_state("V", 2.0)
        first.observe_opaque_control_state(
            Observation("FRONTIER-E-DEV-CURRENT", "EXT", "opaque-control", "s2", authority=Authority.OBSERVATION_ONLY),
            evidence_id="E-FRONTIER-E-DEV-CURRENT",
        )
        record_raw(first, "FRONTIER-E-DEV-CURRENT")
        before = derive_current_owned_probe_prefix(first, max_steps=2)
        assert before["status"] == "CURRENT_OWNED_OPAQUE_PROBE_PREFIX", before
        assert before["step_count"] == 0 and before["opaque_action_sequence"] == (), before
    finally:
        _close(first)

    restarted_world = World()
    restarted_world.index = 2
    restarted_world.value = 2.0
    restarted = build(root, restarted_world)
    derived = derive_current_owned_probe_prefix(restarted, max_steps=2)
    assert derived["status"] == "CURRENT_OWNED_OPAQUE_PROBE_PREFIX", derived
    assert derived["step_count"] == 0 and derived["opaque_action_sequence"] == (), derived
    return restarted, derived


def run_frontier_e_developmental_history() -> dict[str, Any]:
    history_td = tempfile.TemporaryDirectory(prefix="frontier-e-dev-history-")
    fresh_td = tempfile.TemporaryDirectory(prefix="frontier-e-dev-fresh-")
    history_ms = fresh_ms = None
    try:
        history_ms, history = _historyful(Path(history_td.name))
        fresh_ms, fresh = _fresh_current(Path(fresh_td.name))
        history_surface = _current_surface(history_ms, history)
        fresh_surface = _current_surface(fresh_ms, fresh)
        surface_equal = history_surface == fresh_surface
        if not surface_equal:
            raise AssertionError({"CURRENT_SURFACE_NOT_MATCHED": {"history": history_surface, "fresh": fresh_surface}})

        authority_fields = (
            "semantic_coordinate_authority",
            "semantic_referent_authority",
            "truth_authority",
            "selection_authority",
            "execution_authority",
        )
        for payload in (history, fresh):
            for key in authority_fields:
                assert payload[key] == "NONE", (key, payload)

        # The discriminator is deliberately read-only.  The difference comes from
        # authenticated durable predecessor ancestry, not an identity label or manager.
        assert history["history_basis"] == fresh["history_basis"] == "AUTHENTICATED_CURRENT_RAW_RECEIPTS_PLUS_ACTION_OUTCOME_PREDECESSOR_CHAIN"
        assert history["step_count"] == 2 and fresh["step_count"] == 0
        assert history["raw_samples"][-1] == fresh["raw_samples"][-1]
        assert not hasattr(history_ms, "identity_manager") and not hasattr(fresh_ms, "identity_manager")

        return {
            "status": "PASS",
            "discriminator": "MATCHED_CURRENT_SURFACE_DIFFERENT_AUTHENTICATED_DEVELOPMENTAL_HISTORY",
            "current_surface_equal": True,
            "current_surface": history_surface,
            "historyful": {
                "step_count": history["step_count"],
                "opaque_action_sequence": list(history["opaque_action_sequence"]),
                "raw_samples": [list(x) for x in history["raw_samples"]],
                "history_basis": history["history_basis"],
            },
            "fresh_current": {
                "step_count": fresh["step_count"],
                "opaque_action_sequence": list(fresh["opaque_action_sequence"]),
                "raw_samples": [list(x) for x in fresh["raw_samples"]],
                "history_basis": fresh["history_basis"],
            },
            "history_sensitive_read_only_difference": True,
            "numerical_identity_required": "NOT_SHOWN",
            "identity_primitive_added": "NO",
            "caller_supplied_history_label": "NO",
            "semantic_coordinate_authority": "NONE",
            "semantic_referent_authority": "NONE",
            "truth_authority": "NONE",
            "selection_authority": "NONE",
            "execution_authority": "NONE",
            "claim_ceiling": "AUTHENTICATED_DEVELOPMENTAL_PROVENANCE_CAN_BE_OPERATIONALLY_READABLE_ACROSS_RESTART_WHEN_CURRENT_OBSERVABLE_SURFACES_MATCH__THIS_DOES_NOT_ESTABLISH_NUMERICAL_IDENTITY_OR_SELFHOOD",
        }
    finally:
        if history_ms is not None:
            _close(history_ms)
        if fresh_ms is not None:
            _close(fresh_ms)
        history_td.cleanup()
        fresh_td.cleanup()


def main() -> None:
    print(json.dumps(run_frontier_e_developmental_history(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
