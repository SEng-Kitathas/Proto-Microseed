from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2036_full_frame_bound_pareto_research import _fixture, _p2_dominates_effects, _tradeoff_effects

BASE = "84a19d7ea30342c84ac8a9f0bf44fa0fe556bc43"
V1_PROMOTION = "0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39"
EXPECTED_CORE = {
    "microseed/development/epistemic_action.py",
    "microseed/development/epistemic_priority.py",
    "microseed/development/value.py",
    "microseed/runtime/entity.py",
}
FORBIDDEN_ATTRS = (
    "global_scheduler", "scheduler", "global_executive", "value_manager",
    "referent_manager", "self_manager", "body_manager", "language_manager",
    "signal_meaning_registry", "semantic_reference_registry", "token_meaning_registry",
    "persistent_opportunity_registry", "global_selected_opportunity",
)


def _git_core_delta(target_ref: str = V1_PROMOTION) -> dict[str, object]:
    """Audit the sealed V1 candidate delta, not arbitrary future HEAD descendants."""
    root = Path(__file__).resolve().parents[1]
    target = subprocess.check_output(["git", "rev-parse", target_ref], cwd=root, text=True).strip()
    rows = subprocess.check_output(["git", "diff", "--name-status", f"{BASE}..{target}", "--", "microseed"], cwd=root, text=True).splitlines()
    changed = {row.split("\t", 1)[1].replace("\\", "/") for row in rows if "\t" in row}
    new_files = [row for row in rows if row.startswith("A\t")]
    numstat = subprocess.check_output(["git", "diff", "--numstat", f"{BASE}..{target}", "--", "microseed"], cwd=root, text=True).splitlines()
    return {"head": target, "audit_ref": target_ref, "changed_core_paths": sorted(changed), "new_core_files": new_files, "numstat": numstat}


def _surface_authority(effects):
    td, ms, calls, *_ = _fixture(effects)
    try:
        surface = ms.derive_current_owned_referent_full_frame_cross_deficit_selection_surface(act_ob())
        return surface, list(calls)
    finally:
        ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close(); td.cleanup()


def run_ms2047() -> dict[str, object]:
    delta = _git_core_delta()
    assert set(delta["changed_core_paths"]) == EXPECTED_CORE, delta
    assert delta["new_core_files"] == [], delta

    trade, trade_calls = _surface_authority(_tradeoff_effects())
    assert trade["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", trade
    assert trade["selection_authority"] == "NONE"
    assert trade["execution_authority"] == "NONE"
    assert trade_calls == []

    dom, dom_calls = _surface_authority(_p2_dominates_effects())
    assert dom["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION", dom
    assert dom["selection_authority"] == "STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY"
    assert dom["execution_authority"] == "NONE"
    assert dom_calls == []

    with tempfile.TemporaryDirectory(prefix="ms2047-audit-") as td:
        ms = Microseed(Path(td))
        try:
            status = ms.status()
            assert status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE", status
            present = [name for name in FORBIDDEN_ATTRS if hasattr(ms, name)]
            assert present == [], present
            audit = {
                "language_status": status["language"],
                "forbidden_cross_cutting_attrs_present": present,
            }
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()

    # Static source check for known shortcut vocabulary in the actual changed production files.
    root = Path(__file__).resolve().parents[1]
    texts = {rel: (root / rel).read_text(encoding="utf-8") for rel in EXPECTED_CORE}
    forbidden_tokens = {
        "weighted_utility": [],
        "semantic_value_priority_manager": [],
        "global_selected_opportunity =": [],
        "signal_meaning_registry": [],
        "language_manager": [],
    }
    for token in forbidden_tokens:
        forbidden_tokens[token] = [rel for rel, text in texts.items() if token in text]
    assert all(not hits for hits in forbidden_tokens.values()), forbidden_tokens

    return {
        "status": "V1_CANDIDATE_SHAPE_AUDIT_PASS",
        "core_delta": delta,
        "tradeoff_surface": {"status": trade["status"], "selection_authority": trade["selection_authority"], "execution_authority": trade["execution_authority"]},
        "dominance_surface": {"status": dom["status"], "selection_authority": dom["selection_authority"], "execution_authority": dom["execution_authority"]},
        "runtime_audit": audit,
        "forbidden_token_hits": forbidden_tokens,
        "earned": "POST_MS2035_PRODUCTION_DELTA_IS_A_BOUNDED_EXISTING_OWNER_EXTENSION_NOT_A_NEW_CROSS_CUTTING_EXECUTIVE",
        "promotion_law": "TECHNICAL_READINESS_FOR_PROMOTION_REVIEW != CANONICAL_PROMOTION_AUTHORITY",
        "canonical_promotion_authority": "OPERATOR_ONLY",
    }


if __name__ == "__main__":
    print(json.dumps(run_ms2047(), indent=2, sort_keys=True, default=str))
