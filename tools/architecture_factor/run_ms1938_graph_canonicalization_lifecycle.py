from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
REPORT = ROOT / "reports" / "ms1938_graph_canonicalization_lifecycle"
REPORT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))

def _source_snapshot() -> str:
    h = hashlib.sha256()
    for source_base in (ROOT / "microseed", ROOT / "tests"):
        for p in sorted(source_base.rglob("*.py")):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            h.update(rel.encode())
            h.update(b"\0")
            h.update(digest.encode())
            h.update(b"\n")
    return h.hexdigest()


import run_ms1933_invalidation_blast_radius as ms1933  # noqa: E402

FAULT_REASON = "MS1938_OPAQUE_INJECTED_FAULT"
DEPTH = ms1933.DEPTH
MIN_BRANCHES = 8
MAX_BRANCHES = 19
ORDERINGS_PER_VERSION = 6
TARGET = 3


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(obj) -> str:
    return _sha_bytes(_canon(obj))


def _inventory(branches: int) -> dict[str, list[str]]:
    return {
        "capabilities": [f"B{i}-{d}" for i in range(branches) for d in range(DEPTH)],
        "coordinations": [f"R{i}" for i in range(branches)],
        "counterparties": ["CP0"],
    }


def _graph(branches: int) -> list[list[str]]:
    edges: list[list[str]] = []
    for i in range(branches):
        edges.append(["CP0", f"R{i}"])
        edges.append([f"R{i}", f"B{i}-0"])
        for d in range(1, DEPTH):
            edges.append([f"B{i}-{d-1}", f"B{i}-{d}"])
    return edges


def _normalize_edge(edge) -> tuple[str, str]:
    if not isinstance(edge, (list, tuple)) or len(edge) != 2:
        raise ValueError("INVALID_EDGE_ARITY")
    src, dst = str(edge[0]), str(edge[1])
    if not src or not dst:
        raise ValueError("EMPTY_EDGE_ENDPOINT")
    if src == dst:
        raise ValueError("SELF_EDGE_NOT_ALLOWED_IN_FIXTURE")
    return src, dst


def _canonical_graph(graph) -> list[list[str]]:
    normalized = [_normalize_edge(e) for e in graph]
    if len(set(normalized)) != len(normalized):
        raise ValueError("DUPLICATE_EDGE_NOT_ALLOWED")
    return [list(x) for x in sorted(normalized)]


def _canonical_graph_sha(graph) -> str:
    return _sha(_canonical_graph(graph))


def _ordered_inventory_sha(inventory) -> str:
    # Inventory ordering is intentionally semantic because certificate bit positions
    # are interpreted against these ordered lists.
    return _sha(inventory)


def _build(state: Path, branches: int):
    m = ms1933.Microseed(state)
    m.register_operational_counterparty(ms1933._cp())
    for i in range(branches):
        m.register_operational_coordination(ms1933._coord(i))
        root = f"B{i}-0"
        m.register_capability(ms1933._cap(root), coordination_dependencies=((f"R{i}", 0),))
        previous = root
        for d in range(1, DEPTH):
            cid = f"B{i}-{d}"
            m.register_capability(ms1933._cap(cid, (previous,)))
            previous = cid
    return m


def _mask(ids: set[str], ordered: list[str]) -> str:
    value = 0
    for i, item in enumerate(ordered):
        if item in ids:
            value |= 1 << i
    width = max(1, (len(ordered) + 3) // 4)
    return f"{value:0{width}x}"


def _origin(relevant: list[dict]) -> tuple[str, str, int | None]:
    found = []
    for e in relevant:
        p = e.get("payload", {}) or {}
        if str(p.get("reason", "")) != FAULT_REASON:
            continue
        kind = str(e.get("kind", ""))
        if kind == "OPERATIONAL_COUNTERPARTY_INVALIDATED":
            found.append(("COUNTERPARTY", str(p["counterparty_id"]), int(p.get("new_epoch", 0))))
        elif kind == "OPERATIONAL_COORDINATION_INVALIDATED":
            found.append(("COORDINATION", str(p["coordination_id"]), int(p.get("new_epoch", 0))))
        elif kind == "CAPABILITY_INVALIDATED":
            found.append(("CAPABILITY", str(p["root"]), None))
    if len(found) != 1:
        raise AssertionError(f"EXPECTED_ONE_ORIGIN:{found}")
    return found[0]


def _certificate_v2(
    relevant: list[dict], inventory: dict[str, list[str]], graph: list[list[str]],
    stale_caps: set[str], stale_rels: set[str], stale_cp: set[str],
) -> dict:
    origin = _origin(relevant)
    return {
        "v": 2,
        "g": _canonical_graph_sha(graph),
        "i": _ordered_inventory_sha(inventory),
        "t": _sha(relevant),
        "r": hashlib.sha256(FAULT_REASON.encode("utf-8")).hexdigest(),
        "o": [origin[0], origin[1], origin[2]],
        "c": _mask(stale_caps, inventory["capabilities"]),
        "q": _mask(stale_rels, inventory["coordinations"]),
        "p": _mask(stale_cp, inventory["counterparties"]),
        "n": len(relevant),
    }


def _run_fault(branches: int, name: str, action) -> dict:
    inventory = _inventory(branches)
    graph = _graph(branches)
    with tempfile.TemporaryDirectory(prefix=f"ms1938-{branches}-{name}-") as td:
        m = None
        try:
            m = _build(Path(td), branches)
            before = len(m.store.events())
            action(m)
            delta = m.store.events()[before:]
            relevant = [e for e in delta if "INVALIDATED" in str(e.get("kind", "")) or "STALE" in str(e.get("kind", ""))]
            stale_caps = ms1933._stale_caps(m)
            stale_rels = {rid for rid in inventory["coordinations"] if not m.coordinations.is_current(rid)}
            stale_cp = {cid for cid in inventory["counterparties"] if not m.counterparties.is_current(cid)}
            final_vector = {cid: ("STALE" if cid in stale_caps else "CURRENT") for cid in inventory["capabilities"]}
            full_projection = {"events": relevant, "final_capability_vector": final_vector}
            cert = _certificate_v2(relevant, inventory, graph, stale_caps, stale_rels, stale_cp)
            return {
                "name": name,
                "full_projection_bytes": len(_canon(full_projection)),
                "certificate_bytes": len(_canon(cert)),
                "certificate_sha256": _sha(cert),
                "event_count": len(relevant),
                "origin": list(_origin(relevant)),
            }
        finally:
            if m is not None:
                m.biography.close()
                m.evidence.conn.close()
                m.store.conn.close()


def main() -> int:
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    source_start = _source_snapshot()
    started = time.time()

    base_graph = _graph(MIN_BRANCHES)
    reversed_graph = list(reversed(base_graph))
    shuffled_graph = list(base_graph)
    random.Random(1938).shuffle(shuffled_graph)
    topology_drift = json.loads(json.dumps(base_graph))
    topology_drift[topology_drift.index(["R3", "B3-0"])] = ["R3", "B4-0"]
    duplicate_graph = json.loads(json.dumps(base_graph)) + [list(base_graph[0])]

    raw_base_sha = _sha(base_graph)
    raw_reversed_sha = _sha(reversed_graph)
    raw_shuffled_sha = _sha(shuffled_graph)
    canonical_base_sha = _canonical_graph_sha(base_graph)
    canonical_reversed_sha = _canonical_graph_sha(reversed_graph)
    canonical_shuffled_sha = _canonical_graph_sha(shuffled_graph)
    canonical_drift_sha = _canonical_graph_sha(topology_drift)

    duplicate_rejected = False
    duplicate_error = None
    try:
        _canonical_graph_sha(duplicate_graph)
    except ValueError as exc:
        duplicate_rejected = True
        duplicate_error = str(exc)

    inv_base = _inventory(MIN_BRANCHES)
    inv_reversed = json.loads(json.dumps(inv_base))
    inv_reversed["capabilities"] = list(reversed(inv_reversed["capabilities"]))
    inv_reversed["coordinations"] = list(reversed(inv_reversed["coordinations"]))

    versions = []
    raw_graph_hashes_all = set()
    canonical_graph_hashes_all = set()
    raw_graph_archive_bytes = 0
    canonical_graph_archive_bytes = 0
    inventory_archive_bytes = 0
    full_projection_total = 0
    certificate_total = 0

    for branches in range(MIN_BRANCHES, MAX_BRANCHES + 1):
        inventory = _inventory(branches)
        graph = _graph(branches)
        inv_sha = _ordered_inventory_sha(inventory)
        can_sha = _canonical_graph_sha(graph)
        canonical_graph_hashes_all.add(can_sha)
        canonical_graph_archive_bytes += len(_canon(_canonical_graph(graph)))
        inventory_archive_bytes += len(_canon(inventory))

        raw_order_hashes = []
        for j in range(ORDERINGS_PER_VERSION):
            variant = list(graph)
            random.Random(branches * 1000 + j).shuffle(variant)
            h = _sha(variant)
            raw_order_hashes.append(h)
            raw_graph_hashes_all.add(h)
            raw_graph_archive_bytes += len(_canon(variant))
            if _canonical_graph_sha(variant) != can_sha:
                raise AssertionError("CANONICAL_GRAPH_HASH_CHANGED_UNDER_REORDER")

        narrow = _run_fault(
            branches,
            "coordination_specific_fault",
            lambda m: m.change_operational_coordination(f"R{TARGET}", reason=FAULT_REASON),
        )
        broad = _run_fault(
            branches,
            "shared_counterparty_fault",
            lambda m: m.change_operational_counterparty("CP0", reason=FAULT_REASON),
        )
        full_projection_total += narrow["full_projection_bytes"] + broad["full_projection_bytes"]
        certificate_total += narrow["certificate_bytes"] + broad["certificate_bytes"]

        versions.append({
            "branches": branches,
            "capabilities": branches * DEPTH,
            "inventory_sha256": inv_sha,
            "canonical_graph_sha256": can_sha,
            "raw_order_hash_count": len(set(raw_order_hashes)),
            "all_raw_orders_canonicalize_to_one": len({_canonical_graph_sha((lambda v: v)(list(graph))) for _ in [0]}) == 1,
            "narrow_fault": narrow,
            "broad_fault": broad,
        })

    semantic_version_count = MAX_BRANCHES - MIN_BRANCHES + 1
    expected_raw_variant_count = semantic_version_count * ORDERINGS_PER_VERSION
    canonical_manifest_archive_bytes = canonical_graph_archive_bytes + inventory_archive_bytes
    canonical_cert_plus_manifest_bytes = certificate_total + canonical_manifest_archive_bytes
    raw_order_churn_archive_bytes = raw_graph_archive_bytes + inventory_archive_bytes

    source_end = _source_snapshot()

    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "source_snapshot_stable_during_run": source_start == source_end,
        "raw_graph_hash_changes_under_reversal": raw_base_sha != raw_reversed_sha,
        "raw_graph_hash_changes_under_shuffle": raw_base_sha != raw_shuffled_sha,
        "canonical_graph_hash_ignores_edge_order": canonical_base_sha == canonical_reversed_sha == canonical_shuffled_sha,
        "real_topology_drift_changes_canonical_hash": canonical_drift_sha != canonical_base_sha,
        "duplicate_edge_manifest_rejected": duplicate_rejected,
        "ordered_inventory_hash_changes_under_reorder": _ordered_inventory_sha(inv_base) != _ordered_inventory_sha(inv_reversed),
        "one_canonical_graph_hash_per_semantic_version": len(canonical_graph_hashes_all) == semantic_version_count,
        "raw_serialization_creates_all_spurious_variant_hashes": len(raw_graph_hashes_all) == expected_raw_variant_count,
        "canonical_archive_avoids_raw_order_churn": canonical_graph_archive_bytes < raw_graph_archive_bytes,
        "certificates_plus_canonical_manifests_smaller_than_full_projections": canonical_cert_plus_manifest_bytes < full_projection_total,
        "each_dynamic_version_has_compact_certificate_advantage": all(
            v["narrow_fault"]["certificate_bytes"] < v["narrow_fault"]["full_projection_bytes"]
            and v["broad_fault"]["certificate_bytes"] < v["broad_fault"]["full_projection_bytes"]
            for v in versions
        ),
    }

    receipt = {
        "schema": "pcmmad.ms1938.graph-canonicalization-lifecycle.v1",
        "classification": "NON_NOVELTY_TRACE_MANIFEST_LIFECYCLE_EXPERIMENT",
        "discriminator": "SEMANTIC_GRAPH_IDENTITY != SERIALIZATION_EDGE_ORDER",
        "current_repo_head": head,
        "origin_experiment_head": "6b0f012980a625143ea7137be848d6f13b57325b",
        "source_snapshot_start_sha256": source_start,
        "source_snapshot_end_sha256": source_end,
        "source_stable_during_run": source_start == source_end,
        "canonicalization_contract": {
            "graph": "validate 2-endpoint non-self duplicate-free edges; normalize endpoints to strings; lexicographically sort edge tuples before hash",
            "inventory": "DO NOT sort; ordered identity remains semantic because bitmap positions depend on it",
            "certificate_v2": "g binds canonical graph-set hash; i remains ordered inventory hash",
        },
        "base_order_pressure": {
            "raw_base_sha256": raw_base_sha,
            "raw_reversed_sha256": raw_reversed_sha,
            "raw_shuffled_sha256": raw_shuffled_sha,
            "canonical_base_sha256": canonical_base_sha,
            "canonical_reversed_sha256": canonical_reversed_sha,
            "canonical_shuffled_sha256": canonical_shuffled_sha,
            "canonical_topology_drift_sha256": canonical_drift_sha,
            "duplicate_graph_rejected": duplicate_rejected,
            "duplicate_graph_error": duplicate_error,
            "ordered_inventory_base_sha256": _ordered_inventory_sha(inv_base),
            "ordered_inventory_reversed_sha256": _ordered_inventory_sha(inv_reversed),
        },
        "dynamic_history": {
            "branch_versions": [MIN_BRANCHES, MAX_BRANCHES],
            "semantic_version_count": semantic_version_count,
            "graph_serialization_orderings_observed_per_version": ORDERINGS_PER_VERSION,
            "raw_distinct_graph_hash_count": len(raw_graph_hashes_all),
            "canonical_distinct_graph_hash_count": len(canonical_graph_hashes_all),
            "versions": versions,
        },
        "lifecycle_size": {
            "raw_order_churn_graph_archive_bytes": raw_graph_archive_bytes,
            "canonical_graph_archive_bytes": canonical_graph_archive_bytes,
            "inventory_archive_bytes": inventory_archive_bytes,
            "raw_graph_plus_inventory_archive_bytes": raw_order_churn_archive_bytes,
            "canonical_graph_plus_inventory_archive_bytes": canonical_manifest_archive_bytes,
            "full_projection_bytes_24_fault_runs": full_projection_total,
            "certificate_bytes_24_fault_runs": certificate_total,
            "certificates_plus_all_canonical_version_manifests_bytes": canonical_cert_plus_manifest_bytes,
            "bytes_saved_vs_full_projections_even_with_all_version_manifests": full_projection_total - canonical_cert_plus_manifest_bytes,
            "compression_ratio_full_over_certs_plus_manifests": round(full_projection_total / canonical_cert_plus_manifest_bytes, 4),
            "raw_order_churn_to_canonical_graph_archive_ratio": round(raw_graph_archive_bytes / canonical_graph_archive_bytes, 4),
        },
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "interpretation": {
            "earned_statement": "CANONICAL_EDGE_SET_HASH_REMOVES_SERIALIZATION_ORDER_CHURN_WHILE_PRESERVING_REAL_TOPOLOGY_DRIFT_DETECTION",
            "inventory_statement": "BITMAP_INVENTORY_ORDER_REMAINS_SEMANTIC_AND_MUST_STAY_STRICTLY_BOUND",
            "lifecycle_statement": "COMPACT_CERTIFICATE_ADVANTAGE_SURVIVES_MULTI_VERSION_MANIFEST_COST_UNDER_THIS_HISTORY",
            "important_scar": "CANONICALIZE_ONLY_SEMANTICALLY_UNORDERED_STRUCTURE_NOT_POSITION_BEARING_INVENTORIES",
            "next_question": "Whether certificate/manifests should remain experiment-only or justify a project-control implementation for compact server-side readback; no organism adoption is implied.",
        },
        "started_at_epoch": started,
        "duration_seconds": round(time.time() - started, 6),
        "authority": "ENGINEERING_MEASUREMENT_ONLY_NO_NOVELTY_OR_CANONICAL_PROMOTION",
    }
    (REPORT / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
