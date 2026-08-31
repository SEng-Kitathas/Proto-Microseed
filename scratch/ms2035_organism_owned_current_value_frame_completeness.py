from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Authority, QualificationState, ValueVariableContract
from microseed.development.value import ValueVariableRegistry
from scratch.ms2033_cross_value_epistemic_consequence_vector_construction import (
    REQUESTED_VALUES,
    _complete_fixture,
    derive_cross_value_epistemic_consequence_vector,
)


def _contract(value_id: str) -> ValueVariableContract:
    return ValueVariableContract(
        value_id,
        f"opaque-constitutional-{value_id}",
        0.0,
        10.0,
        hashlib.sha256(f"MS2035:{value_id}:0:10".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS2035",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("MS2035_CURRENT_VALUE_FRAME",),
    )


def _frame_digest(rows: list[dict]) -> str:
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def derive_complete_current_value_frame(values: ValueVariableRegistry) -> dict:
    """Research-only, read-only frame enumeration from registry-owned state."""
    base = {
        "selection_authority": "NONE",
        "execution_authority": "NONE",
        "truth_authority": "NONE",
        "semantic_goal_authority": "NONE",
        "semantic_value_priority_authority": "NONE",
        "persistence": "NONE",
        "construction_authority": "DERIVED_READ_ONLY_ONLY",
    }
    current_ids = tuple(sorted(value_id for value_id in values.contracts if values.is_current(value_id)))
    excluded = tuple(sorted(value_id for value_id in values.contracts if not values.is_current(value_id)))
    rows: list[dict] = []
    for value_id in current_ids:
        contract = values.contracts[value_id]
        epoch = int(values.epochs[value_id])
        latest = values.latest.get(value_id)
        if latest is None or int(latest[0]) != epoch:
            return {
                **base,
                "status": "DEFER_UNKNOWN",
                "reason": f"CURRENT_VALUE_FRAME_OBSERVATION_MISSING:{value_id}",
                "current_value_ids": list(current_ids),
                "excluded_noncurrent_value_ids": list(excluded),
                "missing_value_id": value_id,
            }
        current_value = float(latest[1])
        if not math.isfinite(current_value):
            return {
                **base,
                "status": "DEFER_UNKNOWN",
                "reason": f"CURRENT_VALUE_FRAME_NONFINITE_OBSERVATION:{value_id}",
                "current_value_ids": list(current_ids),
                "excluded_noncurrent_value_ids": list(excluded),
            }
        rows.append({
            "value_id": value_id,
            "value_epoch": epoch,
            "current_value": current_value,
            "contract_signature_sha256": str(contract.signature_sha256),
        })
    if not rows:
        return {
            **base,
            "status": "DEFER_UNKNOWN",
            "reason": "NO_CURRENT_CONSTITUTIONAL_VALUE_FRAME",
            "current_value_ids": [],
            "excluded_noncurrent_value_ids": list(excluded),
        }
    return {
        **base,
        "status": "CURRENT_COMPLETE_VALUE_FRAME",
        "reason": "ALL_CURRENT_CONSTITUTIONAL_VALUES_HAVE_CURRENT_OBSERVATIONS",
        "current_value_ids": list(current_ids),
        "excluded_noncurrent_value_ids": list(excluded),
        "rows": rows,
        "frame_digest_sha256": _frame_digest(rows),
    }


def current_value_frame_is_current(values: ValueVariableRegistry, frame: dict) -> dict:
    current = derive_complete_current_value_frame(values)
    if current.get("status") != "CURRENT_COMPLETE_VALUE_FRAME":
        return {
            "status": "DEFER_UNKNOWN",
            "reason": "CURRENT_COMPLETE_VALUE_FRAME_UNAVAILABLE",
            "current_frame": current,
            "frame_current": False,
        }
    same = (
        frame.get("status") == "CURRENT_COMPLETE_VALUE_FRAME"
        and str(frame.get("frame_digest_sha256")) == str(current.get("frame_digest_sha256"))
        and list(frame.get("rows", ())) == list(current.get("rows", ()))
    )
    return {
        "status": "CURRENT" if same else "STALE",
        "reason": "EXACT_CURRENT_VALUE_FRAME_MATCH" if same else "VALUE_FRAME_DESCRIPTOR_DRIFT",
        "frame_current": same,
        "current_frame_digest_sha256": current["frame_digest_sha256"],
    }


def vector_matches_complete_value_frame(vector: dict, frame: dict) -> dict:
    if frame.get("status") != "CURRENT_COMPLETE_VALUE_FRAME":
        return {"status": "DEFER_UNKNOWN", "reason": "COMPLETE_CURRENT_VALUE_FRAME_REQUIRED", "frame_match": False}
    if vector.get("status") != "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR":
        return {"status": "DEFER_UNKNOWN", "reason": "COMPLETE_CURRENT_VECTOR_REQUIRED", "frame_match": False}
    vector_rows = vector.get("value_rows")
    if not isinstance(vector_rows, dict):
        return {"status": "DEFER_UNKNOWN", "reason": "VECTOR_VALUE_ROWS_REQUIRED", "frame_match": False}
    normalized = []
    for value_id in sorted(vector_rows):
        row = vector_rows[value_id]
        normalized.append({
            "value_id": value_id,
            "value_epoch": int(row["value_epoch"]),
            "current_value": float(row["current_value"]),
            "contract_signature_sha256": str(row["contract_signature_sha256"]),
        })
    same = normalized == list(frame["rows"])
    return {
        "status": "CURRENT_VECTOR_MATCHES_COMPLETE_VALUE_FRAME" if same else "DEFER_UNKNOWN",
        "reason": "EXACT_COMPLETE_VALUE_FRAME_MATCH" if same else "VECTOR_FRAME_INCOMPLETE_OR_DRIFTED",
        "frame_match": same,
    }


def run_complete_frame_and_subset_rejection() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        before = len(ms.store.events())
        frame = derive_complete_current_value_frame(ms.values)
        full = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=REQUESTED_VALUES,
        )
        subset = derive_cross_value_epistemic_consequence_vector(
            opportunity=by_probe["P2"], values=ms.values,
            current_capability_epochs=dict(ms.capabilities.epochs), effect_witnesses=effects,
            requested_value_ids=("V",),
        )
        full_match = vector_matches_complete_value_frame(full, frame)
        subset_match = vector_matches_complete_value_frame(subset, frame)
        after = len(ms.store.events())
        assert frame["status"] == "CURRENT_COMPLETE_VALUE_FRAME", frame
        assert frame["current_value_ids"] == ["V", "W"], frame
        assert [row["value_id"] for row in frame["rows"]] == ["V", "W"], frame
        assert full_match["frame_match"] is True, full_match
        assert subset_match["frame_match"] is False, subset_match
        assert subset_match["reason"] == "VECTOR_FRAME_INCOMPLETE_OR_DRIFTED"
        assert before == after
        assert calls == []
        return {
            "status": "PASS",
            "frame": frame,
            "full_vector_match": full_match,
            "caller_subset_match": subset_match,
            "read_only": before == after,
            "handler_calls": list(calls),
        }
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_missing_current_observation_blocks_frame() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        ms.register_value_variable(_contract("X"))
        frame = derive_complete_current_value_frame(ms.values)
        assert frame["status"] == "DEFER_UNKNOWN", frame
        assert frame["reason"] == "CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X", frame
        assert frame["current_value_ids"] == ["V", "W", "X"], frame
        assert frame["missing_value_id"] == "X"
        assert calls == []
        return {"status": "PASS", "frame": frame, "silent_omission": "NO", "handler_calls": list(calls)}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_stale_value_exclusion_is_explicit_currentness() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        ms.register_value_variable(_contract("X"))
        ms.observe_value_state("X", 1.0)
        complete = derive_complete_current_value_frame(ms.values)
        assert complete["current_value_ids"] == ["V", "W", "X"]
        ms.values.change("X", reason="MS2035_STALE_X")
        after = derive_complete_current_value_frame(ms.values)
        assert after["status"] == "CURRENT_COMPLETE_VALUE_FRAME", after
        assert after["current_value_ids"] == ["V", "W"], after
        assert after["excluded_noncurrent_value_ids"] == ["X"], after
        assert calls == []
        return {"status": "PASS", "before": complete, "after": after, "exclusion_basis": "REGISTRY_IS_CURRENT_FALSE"}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_new_value_invalidates_old_frame() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        old = derive_complete_current_value_frame(ms.values)
        ms.register_value_variable(_contract("X"))
        ms.observe_value_state("X", 1.0)
        current = derive_complete_current_value_frame(ms.values)
        check = current_value_frame_is_current(ms.values, old)
        assert old["current_value_ids"] == ["V", "W"]
        assert current["current_value_ids"] == ["V", "W", "X"]
        assert old["frame_digest_sha256"] != current["frame_digest_sha256"]
        assert check["frame_current"] is False
        assert check["reason"] == "VALUE_FRAME_DESCRIPTOR_DRIFT"
        assert calls == []
        return {"status": "PASS", "old": old, "current": current, "old_frame_current": check}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_same_epoch_observation_change_invalidates_old_frame() -> dict:
    td, ms, calls, by_probe, effects = _complete_fixture()
    try:
        old = derive_complete_current_value_frame(ms.values)
        old_w_epoch = int(ms.values.epochs["W"])
        ms.observe_value_state("W", -0.75)
        assert int(ms.values.epochs["W"]) == old_w_epoch
        current = derive_complete_current_value_frame(ms.values)
        check = current_value_frame_is_current(ms.values, old)
        assert old["frame_digest_sha256"] != current["frame_digest_sha256"]
        assert check["frame_current"] is False
        assert check["reason"] == "VALUE_FRAME_DESCRIPTOR_DRIFT"
        assert calls == []
        return {"status": "PASS", "old": old, "current": current, "old_frame_current": check, "epoch_unchanged": True}
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_order_independence_and_duplicate_identity() -> dict:
    a = ValueVariableRegistry(); b = ValueVariableRegistry()
    for value_id in ("V", "W"):
        a.register(_contract(value_id)); a.observe(value_id, -1.0)
    for value_id in ("W", "V"):
        b.register(_contract(value_id)); b.observe(value_id, -1.0)
    fa = derive_complete_current_value_frame(a); fb = derive_complete_current_value_frame(b)
    assert fa["rows"] == fb["rows"]
    assert fa["frame_digest_sha256"] == fb["frame_digest_sha256"]
    duplicate_rejected = False
    try:
        a.register(_contract("V"))
    except ValueError as exc:
        duplicate_rejected = "duplicate value variable: V" in str(exc)
    assert duplicate_rejected
    return {"status": "PASS", "frame_digest_sha256": fa["frame_digest_sha256"], "order_independent": True, "duplicate_identity_rejected": True}


def run_ms2035() -> dict:
    return {
        "status": "CURRENT_VALUE_FRAME_COMPLETENESS_EARNED_RESEARCH_ONLY",
        "complete_frame_and_subset_rejection": run_complete_frame_and_subset_rejection(),
        "missing_current_observation": run_missing_current_observation_blocks_frame(),
        "stale_value_exclusion": run_stale_value_exclusion_is_explicit_currentness(),
        "new_value_invalidates_old_frame": run_new_value_invalidates_old_frame(),
        "same_epoch_observation_change": run_same_epoch_observation_change_invalidates_old_frame(),
        "order_and_duplicate_identity": run_order_independence_and_duplicate_identity(),
        "earned": "COMPLETE_CURRENT_VALUE_FRAME_IS_DERIVABLE_FROM_VALUE_REGISTRY_WITHOUT_CALLER_SUBSET_AUTHORITY",
        "missing_observation_law": "CURRENT_VALUE_WITHOUT_CURRENT_OBSERVATION_BLOCKS_FRAME_COMPLETENESS",
        "runtime_pareto_selection_authorized": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2035(), indent=2, sort_keys=True, default=str))
