from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed.development.epistemic_priority import derive_strict_same_value_cross_deficit_selection_commitment
from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import _regulatory_summary
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface


def _rows(m, opportunities) -> tuple[dict, ...]:
    out = []
    for op in opportunities:
        summary = _regulatory_summary(m, op)
        assert summary["status"] == "CURRENT_SAME_VALUE_REGULATORY_CONSEQUENCE_SURFACE", summary
        out.append({
            "deficit_id": str(op["deficit"].deficit_id),
            "probe_action_id": str(op["probe_action_id"]),
            "value_id": str(summary["value_id"]),
            "value_epoch": int(summary["value_epoch"]),
            "current_value": float(summary["current_value"]),
            "worst_residual_pressure": float(summary["worst_residual_pressure"]),
            "premise_ids": (
                str(op["deficit"].deficit_id),
                str(op["priority"].commitment_id),
                str(op["contrast_information"].commitment_id),
                str(op["commitment"].commitment_id),
                *tuple(str(x) for x in summary["proposal_digests"]),
            ),
        })
    return tuple(out)


def run_symmetric() -> dict:
    td, m, calls, opportunities, _, _ = _surface(False)
    try:
        rows = _rows(m, opportunities["opportunities"])
        c = derive_strict_same_value_cross_deficit_selection_commitment(rows)
        assert c.commitment.value == "UNKNOWN", c.serializable()
        assert c.reason == "WORST_RESIDUAL_PRESSURE_TIE", c.serializable()
        assert dict(c.qualifiers)["selection_authority"] == "NONE"
        assert calls == []
        return {"status": "PASS", "rows": rows, "commitment": c.serializable(), "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric() -> dict:
    td, m, calls, opportunities, _, _ = _surface(True)
    try:
        rows = _rows(m, opportunities["opportunities"])
        c = derive_strict_same_value_cross_deficit_selection_commitment(rows)
        q = dict(c.qualifiers)
        assert c.licenses_yes(), c.serializable()
        assert c.reason == "STRICT_SAME_VALUE_CROSS_DEFICIT_REGULATORY_DOMINANCE"
        assert q["selected_probe_action_id"] == "P2"
        assert q["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"
        assert q["execution_authority"] == "NONE"
        assert calls == []
        return {"status": "PASS", "rows": rows, "commitment": c.serializable(), "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_value_drift() -> dict:
    td, m, calls, opportunities, _, _ = _surface(True)
    try:
        before = derive_strict_same_value_cross_deficit_selection_commitment(_rows(m, opportunities["opportunities"]))
        assert before.licenses_yes(), before.serializable()
        m.observe_value_state("V", 5.0)
        after_rows = _rows(m, opportunities["opportunities"])
        after = derive_strict_same_value_cross_deficit_selection_commitment(after_rows)
        assert not after.licenses_yes(), after.serializable()
        assert after.reason == "WORST_RESIDUAL_PRESSURE_TIE", after.serializable()
        assert calls == []
        return {"status": "PASS", "before": before.serializable(), "after_rows": after_rows, "after": after.serializable(), "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_cross_value_refusal() -> dict:
    td, m, calls, opportunities, _, _ = _surface(True)
    try:
        rows = [dict(x) for x in _rows(m, opportunities["opportunities"])]
        rows[1]["value_id"] = "OTHER-VALUE"
        c = derive_strict_same_value_cross_deficit_selection_commitment(rows)
        assert not c.licenses_yes(), c.serializable()
        assert c.reason == "EXACT_SAME_VALUE_COORDINATE_REQUIRED", c.serializable()
        assert dict(c.qualifiers)["selection_authority"] == "NONE"
        assert calls == []
        return {"status": "PASS", "commitment": c.serializable(), "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2027() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric": run_asymmetric(),
        "value_drift": run_value_drift(),
        "cross_value_refusal": run_cross_value_refusal(),
        "new_scheduler_required": "NO",
        "new_weighted_utility_required": "NO",
        "runtime_orchestration_added": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2027(), indent=2, sort_keys=True, default=str))
