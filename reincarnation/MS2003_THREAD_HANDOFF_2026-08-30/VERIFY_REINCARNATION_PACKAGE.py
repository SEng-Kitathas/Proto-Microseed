from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "MANIFEST_SHA256.json"

REQUIRED = {
    "00_READ_ME_FIRST.md",
    "01_NEXT_THREAD_INGRESS_PROMPT.txt",
    "02_VERIFIED_STATE_AND_CONTRADICTIONS.md",
    "03_COMMANDERS_INTENT.md",
    "04_PROJECT_HISTORY_AND_ENGINEERING_DECISIONS.md",
    "05_SCARS_AND_DO_NOT_REINTRODUCE.md",
    "06_AUTHORITY_LINEAGE_AND_PROMOTION_MAP.md",
    "07_CURRENT_FRONTIER_MS2004_UNSEALED.md",
    "08_RECOVERY_AND_OPERATING_PLAYBOOK.md",
    "09_TRANSCRIPT_FIDELITY_AND_GAPS.md",
    "THIS_CONVERSATION.md",
    "source/GIT_STATE.json",
    "source/GIT_LOG.txt",
    "source/REMOTE_REFS.txt",
    "source/MS2004_UNSEALED_HASHES.json",
    "archives/PCMMAD_LAB_HANDOFF_MS1944_2026-08-29.zip",
    "archives/RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip",
    "historical/hand-stitched thread recovery document.txt",
    "unsealed_worktree_snapshot/MS2004/methodology/MS2004_UNIFIED_REFERENT_LIFETIME_POLICY.md",
    "unsealed_worktree_snapshot/MS2004/scratch/ms2004_unified_referent_lifetime_policy.py",
    "unsealed_worktree_snapshot/MS2004/tests/embodiment/test_ms2004_unified_referent_lifetime_policy.py",
}

EXPECTED_KEY_HASHES = {
    "archives/PCMMAD_LAB_HANDOFF_MS1944_2026-08-29.zip": "892dd4914e285faaab82168dbe293dda4bcd033b9d7584972c5d836e7e92d08a",
    "archives/RAHL_ENGINEERING_IN_HOUSE_SOP_SPLIT_CANDIDATE_R3_1_2026-08-29.zip": "4d205becc2413889bdb37c6b6ff7513d6f759a7dff1d9f9b8fddaddd8235a278",
    "historical/hand-stitched thread recovery document.txt": "75464a42ca3d11b065b91fd0d7c12b3b334f0311ccf3ea66b0232a4b28896b17",
}

EXPECTED_MS2003_HEAD = "9946d4ddf37642615b5f4e5a47685f94397803ff"
EXPECTED_MS2003_TREE = "c8795b5de35f02d8c50b100aa264a6018e76494f"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    issues: list[str] = []
    if not MANIFEST.exists():
        print(json.dumps({"status": "FAIL", "issues": ["MANIFEST_MISSING"]}, indent=2))
        return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("files", {})

    for rel in sorted(REQUIRED):
        if not (ROOT / rel).is_file():
            issues.append(f"REQUIRED_MISSING:{rel}")

    for rel, meta in sorted(entries.items()):
        p = ROOT / rel
        if not p.is_file():
            issues.append(f"MANIFEST_FILE_MISSING:{rel}")
            continue
        size = p.stat().st_size
        if size != int(meta["bytes"]):
            issues.append(f"SIZE_MISMATCH:{rel}:{size}!={meta['bytes']}")
            continue
        digest = sha256(p)
        if digest != meta["sha256"]:
            issues.append(f"HASH_MISMATCH:{rel}:{digest}!={meta['sha256']}")

    actual_payload = {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.name not in {"MANIFEST_SHA256.json", "VERIFICATION_RECEIPT.json"}
        and "__pycache__" not in p.parts
        and ".pcmmad_sync_runs" not in p.parts
    }
    manifested = set(entries)
    for rel in sorted(actual_payload - manifested):
        issues.append(f"UNMANIFESTED_FILE:{rel}")
    for rel in sorted(manifested - actual_payload):
        issues.append(f"MANIFEST_ONLY_FILE:{rel}")

    for rel, expected in EXPECTED_KEY_HASHES.items():
        p = ROOT / rel
        if p.is_file():
            digest = sha256(p)
            if digest != expected:
                issues.append(f"KEY_HASH_MISMATCH:{rel}:{digest}!={expected}")

    transcript = ROOT / "THIS_CONVERSATION.md"
    if transcript.is_file() and transcript.stat().st_size < 200_000:
        issues.append(f"TRANSCRIPT_SUSPICIOUSLY_SMALL:{transcript.stat().st_size}")

    git_state_path = ROOT / "source/GIT_STATE.json"
    if git_state_path.is_file():
        state = json.loads(git_state_path.read_text(encoding="utf-8"))
        if state.get("head") != EXPECTED_MS2003_HEAD:
            issues.append(f"GIT_HEAD_MISMATCH:{state.get('head')}!={EXPECTED_MS2003_HEAD}")
        if state.get("tree") != EXPECTED_MS2003_TREE:
            issues.append(f"GIT_TREE_MISMATCH:{state.get('tree')}!={EXPECTED_MS2003_TREE}")
        remote = str(state.get("remote_research_ref", ""))
        if not remote.startswith(EXPECTED_MS2003_HEAD):
            issues.append(f"REMOTE_RESEARCH_REF_MISMATCH:{remote}")

    status = "PASS" if not issues else "FAIL"
    result = {
        "status": status,
        "manifest_file_count": len(entries),
        "payload_file_count": len(actual_payload),
        "issues": issues,
    }
    print(json.dumps(result, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
