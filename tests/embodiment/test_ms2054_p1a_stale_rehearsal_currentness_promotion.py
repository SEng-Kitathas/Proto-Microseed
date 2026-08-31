from __future__ import annotations

import subprocess
from pathlib import Path

from scratch.v1_soak_001_stale_rehearsal_reuse_violation import run

V1 = "0fa41f1ed4cf2fbd341b5f0b63adbc0034d4ac39"


def test_ms2054_p1a_is_narrow_production_repair_from_v1():
    root = Path(__file__).resolve().parents[2]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", f"{V1}..HEAD", "--", "microseed"], cwd=root, text=True
    ).splitlines()
    assert changed == ["microseed/runtime/entity.py"]


def test_ms2054_p1a_blocks_stale_learned_relation_from_durable_rehearsal_execution_premise():
    r = run()
    assert r["sign_flip_guard"]["status"] == "BLOCKED_AS_EXPECTED"
    t = r["terminal_only_drift"]
    assert t["status"] == "BLOCKED"
    assert t["relation_status"]["R-41"]["status"] == "STALE_PREDICTIVE_RELATION"
    assert t["proposal_status"]["s2"]["status"] == "UNKNOWN_INCOMPLETE"
    assert t["proposal_status"]["s2"]["reason"].startswith("REHEARSAL_LEARNED_RELATION_NOT_CURRENT:ACTION-LAW-")
    assert t["post_drift_r_commitment"]["commitment"] == "UNKNOWN"
    assert t["post_drift_r_intent"]["status"] == "ABSTAIN"
