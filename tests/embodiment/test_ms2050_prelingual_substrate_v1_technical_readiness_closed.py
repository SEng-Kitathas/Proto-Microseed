from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from microseed import Microseed
from scratch.ms2047_v1_candidate_simplification_and_authority_audit import run_ms2047


FROZEN_WHOLE_HEAD = "1e6ca740db9bec7492b2ffc988d0b7a091cddf99"


def test_ms2050_current_production_bytes_match_frozen_895_of_895_whole_suite_subject():
    root = Path(__file__).resolve().parents[2]
    current = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    diff = subprocess.run(["git", "diff", "--quiet", f"{FROZEN_WHOLE_HEAD}..{current}", "--", "microseed"], cwd=root)
    assert diff.returncode == 0
    audit = run_ms2047()
    assert audit["status"] == "V1_CANDIDATE_SHAPE_AUDIT_PASS"
    assert audit["canonical_promotion_authority"] == "OPERATOR_ONLY"


def test_ms2050_current_microseed_self_test_green_and_language_still_deferred():
    with tempfile.TemporaryDirectory(prefix="ms2050-self-test-") as td:
        ms = Microseed(Path(td))
        try:
            result = ms.self_test()
            assert result["all_pass"] is True
            assert result["passed"] == result["total"] == 81
            assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
