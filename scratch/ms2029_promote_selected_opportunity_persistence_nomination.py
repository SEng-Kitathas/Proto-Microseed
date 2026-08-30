from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface


def _counts(m):
    return (len(m.evidence.recent(m.evidence.count())), len(m.epistemic_deficits.records), len(m.action_closure.intents), len(m.action_closure.executions))


def run_symmetric() -> dict:
    td, m, calls, _, _, _ = _surface(False)
    try:
        before = _counts(m)
        result = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        after = _counts(m)
        assert result["status"] == "ABSTAIN", result
        assert result["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", result
        assert before == after and calls == [], (before, after, calls)
        return {"status": "PASS", "result": result, "before": before, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric_and_idempotent() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        before = _counts(m)
        first = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        mid = _counts(m)
        assert first["status"] == "SELECTED_OPPORTUNITY_PERSISTED_AND_NOMINATED", first
        assert first["selected_probe_action_id"] == "P2", first
        assert first["deficit_delta"] == 1 and first["intent_delta"] == 1 and first["execution_delta"] == 0, first
        unknown = m.evidence.get(first["unknown_evidence_id"])
        assert unknown is not None and unknown["disposition"] == "UNKNOWN_INCOMPLETE", unknown
        assert unknown["payload"]["kind"] == "SELECTED_OWNED_REFERENT_EPISTEMIC_UNKNOWN", unknown
        assert unknown["payload"]["cross_deficit_selection_commitment_id"] == first["selection_commitment"]["commitment_id"], unknown
        second = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        after = _counts(m)
        assert second["status"] == "ABSTAIN", second
        assert second["reason"] == "SELECTED_EPISTEMIC_DEFICIT_ALREADY_PERSISTED", second
        assert second["deficit_delta"] == second["intent_delta"] == second["execution_delta"] == 0, second
        assert mid == after and calls == [], (mid, after, calls)
        return {"status": "PASS", "first": first, "second": second, "before": before, "mid": mid, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_value_drift() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        m.observe_value_state("V", 5.0)
        before = _counts(m)
        result = m.nominate_current_strict_same_value_referent_epistemic_opportunity(act_ob())
        after = _counts(m)
        assert result["status"] == "ABSTAIN", result
        assert result["reason"] in {"MULTIPLE_CURRENT_CROSS_DEFICIT_OPPORTUNITIES_REQUIRED", "WORST_RESIDUAL_PRESSURE_TIE"}, result
        assert before == after and calls == [], (before, after, calls)
        return {"status": "PASS", "result": result, "before": before, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2029() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric_idempotent": run_asymmetric_and_idempotent(),
        "value_drift": run_value_drift(),
        "new_scheduler_required": "NO",
        "persistent_opportunity_registry_required": "NO",
        "execution_authority": "NONE",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2029(), indent=2, sort_keys=True, default=str))
