from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import _surface


def _counts(m):
    return (
        len(m.epistemic_deficits.records),
        len(m.action_closure.intents),
        len(m.action_closure.executions),
    )


def run_symmetric() -> dict:
    td, m, calls, _, _, _ = _surface(False)
    try:
        before = _counts(m)
        surface = m.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        selection = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        after = _counts(m)
        assert surface["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", surface
        assert set(surface["probe_action_ids"]) == {"P2", "P4"}, surface
        assert selection["status"] == "NO_CURRENT_STRICT_CROSS_DEFICIT_SELECTION", selection
        assert selection["selection_commitment"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE", selection
        assert before == after and calls == [], (before, after, calls)
        return {"status": "PASS", "surface": surface, "selection": selection, "before": before, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_asymmetric() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        before = _counts(m)
        surface = m.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        selection = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        after = _counts(m)
        assert surface["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES", surface
        assert selection["status"] == "CURRENT_STRICT_SAME_VALUE_CROSS_DEFICIT_SELECTION", selection
        assert selection["selected_probe_action_id"] == "P2", selection
        assert selection["selection_commitment"]["commitment"] == "YES", selection
        assert selection["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY", selection
        assert before == after and calls == [], (before, after, calls)
        return {"status": "PASS", "surface": surface, "selection": selection, "before": before, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_value_drift() -> dict:
    td, m, calls, _, _, _ = _surface(True)
    try:
        before = _counts(m)
        initial = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        assert initial["status"] == "CURRENT_STRICT_SAME_VALUE_CROSS_DEFICIT_SELECTION", initial
        m.observe_value_state("V", 5.0)
        surface = m.derive_current_owned_referent_epistemic_opportunity_surface(act_ob())
        selection = m.derive_current_owned_referent_cross_deficit_selection_surface(act_ob())
        after = _counts(m)
        assert surface["status"] == "NO_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY", surface
        assert selection["status"] == "NO_CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED", selection
        assert before == after and calls == [], (before, after, calls)
        return {"status": "PASS", "initial": initial, "surface": surface, "selection": selection, "before": before, "after": after, "calls": list(calls)}
    finally:
        m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def run_ms2028() -> dict:
    return {
        "status": "PASS",
        "symmetric": run_symmetric(),
        "asymmetric": run_asymmetric(),
        "value_drift": run_value_drift(),
        "persistent_state_created": "NO",
        "execution_authority": "NONE",
        "new_scheduler_required": "NO",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2028(), indent=2, sort_keys=True, default=str))
