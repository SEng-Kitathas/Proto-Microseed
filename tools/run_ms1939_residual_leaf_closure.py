from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "ms1939_residual_leaf_closure"
if REPORT.exists():
    shutil.rmtree(REPORT)
REPORT.mkdir(parents=True, exist_ok=True)

MAX_PARALLEL = 6
GROUP_TIMEOUT = 30
CHUNK_SIZE = 2

FILES = (
    "tests/embodiment/test_ms1533_multi_pressure_bridge.py",
    "tests/embodiment/test_ms1534_multi_pressure_effect_boundary.py",
    "tests/embodiment/test_ms1535_multi_pressure_outcome_closure.py",
    "tests/embodiment/test_ms1598_observation_basis_ingress.py",
    "tests/embodiment/test_ms1643_historical_admission_ingress.py",
    "tests/embodiment/test_ms1763_pass16_content_bound_sample_currentness.py",
    "tests/embodiment/test_ms1764_pass17_external_alternative_model_boundary.py",
    "tests/embodiment/test_ms1765_pass18_no_candidate_is_not_closure.py",
    "tests/embodiment/test_ms1768_pass01_flat_relation_owner_not_model_set.py",
    "tests/embodiment/test_ms1770_pass03_projection_routing_not_live_model_set.py",
)


def source_snapshot() -> tuple[str, list[tuple[str, str]]]:
    rows: list[tuple[str, str]] = []
    h = hashlib.sha256()
    for base in (ROOT / "microseed", ROOT / "tests"):
        for p in sorted(base.rglob("*.py")):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            rows.append((rel, digest))
            h.update(rel.encode())
            h.update(b"\0")
            h.update(digest.encode())
            h.update(b"\n")
    return h.hexdigest(), rows


def test_names(rel: str) -> list[str]:
    tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
    return [
        n.name
        for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
    ]


def run_group(gid: str, nodes: list[str], depth: int) -> dict:
    d = REPORT / gid
    d.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "tools/run_pytest_cleanup_neutral.py",
        "-q",
        "-p",
        "no:cacheprovider",
        *nodes,
    ]
    started = time.time()
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=GROUP_TIMEOUT)
        code, out, err = r.returncode, r.stdout, r.stderr
        marker = "COMPLETE"
        cls = "PASS" if code == 0 else "NEGATIVE_OR_COMPATIBILITY_REVIEW_REQUIRED"
    except subprocess.TimeoutExpired as exc:
        code = None
        out = (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        marker = "INCOMPLETE"
        cls = "UNKNOWN_INCOMPLETE_TIMEOUT"
    duration = round(time.time() - started, 6)
    (d / "pytest.stdout.log").write_text(out, encoding="utf-8")
    (d / "pytest.stderr.log").write_text(err, encoding="utf-8")
    m = re.search(r"(\d+) passed", out)
    passed = int(m.group(1)) if m else None
    rec = {
        "schema": "microseed.ms1939.residual-leaf.group.v1",
        "group_id": gid,
        "depth": depth,
        "nodes": nodes,
        "duration_seconds": duration,
        "exit_code": code,
        "classification": cls,
        "completion_marker": marker,
        "passed_count": passed,
        "stdout_sha256": hashlib.sha256(out.encode()).hexdigest(),
        "stderr_sha256": hashlib.sha256(err.encode()).hexdigest(),
        "stdout_tail": "\n".join(out.splitlines()[-8:]),
        "stderr_tail": "\n".join(err.splitlines()[-8:]),
    }
    (d / "receipt.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


start_sha, start_rows = source_snapshot()
expected_nodes: list[str] = []
pending: list[tuple[str, list[str], int]] = []
for rel in FILES:
    names = test_names(rel)
    if not names:
        raise SystemExit(f"NO_TESTS:{rel}")
    nodes = [f"{rel}::{name}" for name in names]
    expected_nodes.extend(nodes)
    for i in range(0, len(nodes), CHUNK_SIZE):
        pending.append((f"{Path(rel).stem}-{i // CHUNK_SIZE:02d}", nodes[i:i + CHUNK_SIZE], 0))

selected: list[dict] = []
negative: list[dict] = []
terminal_unknown: list[dict] = []
all_runs: list[dict] = []
rounds = 0
while pending:
    rounds += 1
    current = pending
    pending = []
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        futures = {
            pool.submit(run_group, gid, nodes, depth): (gid, nodes, depth)
            for gid, nodes, depth in current
        }
        for fut in as_completed(futures):
            rec = fut.result()
            all_runs.append(rec)
            if rec["classification"] == "PASS" and rec["exit_code"] == 0:
                selected.append(rec)
            elif rec["classification"] == "UNKNOWN_INCOMPLETE_TIMEOUT":
                nodes = list(rec["nodes"])
                depth = int(rec["depth"])
                if len(nodes) <= 1:
                    terminal_unknown.append(rec)
                else:
                    mid = (len(nodes) + 1) // 2
                    pending.append((rec["group_id"] + "a", nodes[:mid], depth + 1))
                    pending.append((rec["group_id"] + "b", nodes[mid:], depth + 1))
            else:
                negative.append(rec)
    if negative or terminal_unknown:
        break
    if rounds > 8:
        raise SystemExit("RESIDUAL_RECURSION_DEPTH_GUARD")

covered = [node for rec in selected for node in rec["nodes"]]
missing = sorted(set(expected_nodes) - set(covered))
extra = sorted(set(covered) - set(expected_nodes))
dup = sorted({x for x in covered if covered.count(x) > 1})
coverage_ok = not missing and not extra and not dup and len(covered) == len(expected_nodes)
end_sha, end_rows = source_snapshot()
source_stable = start_sha == end_sha and start_rows == end_rows
passed_total = sum(rec.get("passed_count") or 0 for rec in selected)
classification = "PASS" if coverage_ok and source_stable and not negative and not terminal_unknown else "REVIEW_REQUIRED"
agg = {
    "schema": "microseed.ms1939.residual-leaf.aggregate.v1",
    "purpose": "close the exact ten slow files left uncovered by the corrected-source sharded compatibility sweep",
    "source_snapshot_start_sha256": start_sha,
    "source_snapshot_end_sha256": end_sha,
    "source_stable": source_stable,
    "file_count": len(FILES),
    "files": list(FILES),
    "expected_test_node_count": len(expected_nodes),
    "covered_test_node_count": len(covered),
    "coverage_ok": coverage_ok,
    "passed_count": passed_total,
    "missing_nodes": missing,
    "extra_nodes": extra,
    "duplicate_nodes": dup,
    "negative_groups": [r["group_id"] for r in negative],
    "terminal_unknown_groups": [r["group_id"] for r in terminal_unknown],
    "rounds": rounds,
    "run_count": len(all_runs),
    "classification": classification,
    "completion_marker": "COMPLETE" if classification == "PASS" else "INCOMPLETE",
}
(REPORT / "aggregate_receipt.json").write_text(json.dumps(agg, indent=2), encoding="utf-8")
print(json.dumps({
    "receipt": str((REPORT / "aggregate_receipt.json").relative_to(ROOT)),
    "classification": classification,
    "source_stable": source_stable,
    "file_count": len(FILES),
    "expected_nodes": len(expected_nodes),
    "covered_nodes": len(covered),
    "passed_count": passed_total,
    "coverage_ok": coverage_ok,
    "negative_groups": agg["negative_groups"],
    "terminal_unknown_groups": agg["terminal_unknown_groups"],
    "rounds": rounds,
    "run_count": len(all_runs),
}, indent=2))
raise SystemExit(0 if classification == "PASS" else 1)
