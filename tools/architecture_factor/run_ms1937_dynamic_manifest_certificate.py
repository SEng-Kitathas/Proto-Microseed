from __future__ import annotations

import hashlib

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
REPORT = ROOT / "reports" / "ms1937_dynamic_manifest_certificate"
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


import run_ms1936_causal_trace_certificate as ms1936  # noqa: E402


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(obj) -> str:
    import hashlib
    return hashlib.sha256(_canon(obj)).hexdigest()


def _verify_with_manifests(cert: dict, inventory: dict, graph: list[list[str]]) -> dict:
    inv_sha = _sha(inventory)
    graph_sha = _sha(graph)
    if inv_sha != cert["i"]:
        return {
            "status": "REJECTED",
            "reason": "INVENTORY_MANIFEST_BINDING_MISMATCH",
            "expected_inventory_sha256": cert["i"],
            "supplied_inventory_sha256": inv_sha,
        }
    if graph_sha != cert["g"]:
        return {
            "status": "REJECTED",
            "reason": "DEPENDENCY_GRAPH_BINDING_MISMATCH",
            "expected_graph_sha256": cert["g"],
            "supplied_graph_sha256": graph_sha,
        }

    caps = list(inventory["capabilities"])
    rels = list(inventory["coordinations"])
    cps = list(inventory["counterparties"])
    decoded = {
        "origin": list(cert["o"]),
        "stale_capabilities": sorted(ms1936._unmask(cert["c"], caps)),
        "stale_relations": sorted(ms1936._unmask(cert["q"], rels)),
        "stale_counterparties": sorted(ms1936._unmask(cert["p"], cps)),
        "event_count": int(cert["n"]),
    }
    return {"status": "VERIFIED", "reason": "EXACT_REFERENCED_MANIFESTS", "decoded": decoded}


def _verify_from_registry(cert: dict, inv_registry: dict[str, dict], graph_registry: dict[str, list[list[str]]]) -> dict:
    inventory = inv_registry.get(cert["i"])
    graph = graph_registry.get(cert["g"])
    if inventory is None:
        return {"status": "ABSTAIN", "reason": "REFERENCED_INVENTORY_MANIFEST_NOT_AVAILABLE"}
    if graph is None:
        return {"status": "ABSTAIN", "reason": "REFERENCED_DEPENDENCY_GRAPH_NOT_AVAILABLE"}
    return _verify_with_manifests(cert, inventory, graph)


def _v2_append_inventory() -> tuple[dict, list[list[str]]]:
    inv = json.loads(json.dumps(ms1936.INVENTORY))
    inv["coordinations"].append("R8")
    inv["capabilities"].extend(["B8-0", "B8-1", "B8-2"])
    graph = json.loads(json.dumps(ms1936.GRAPH))
    graph.extend([["CP0", "R8"], ["R8", "B8-0"], ["B8-0", "B8-1"], ["B8-1", "B8-2"]])
    return inv, graph


def _reordered_inventory() -> dict:
    inv = json.loads(json.dumps(ms1936.INVENTORY))
    inv["capabilities"] = list(reversed(inv["capabilities"]))
    inv["coordinations"] = list(reversed(inv["coordinations"]))
    return inv


def _topology_drift_graph() -> list[list[str]]:
    graph = json.loads(json.dumps(ms1936.GRAPH))
    # Replace one branch-root edge with a cross-branch edge while retaining IDs.
    old = ["R3", "B3-0"]
    new = ["R3", "B4-0"]
    idx = graph.index(old)
    graph[idx] = new
    return graph


def _cert_scenarios() -> list[dict]:
    return [
        ms1936._scenario(
            "coordination_specific_fault",
            lambda m: m.change_operational_coordination(f"R{ms1936.TARGET}", reason=ms1936.FAULT_REASON),
        ),
        ms1936._scenario(
            "root_capability_fault",
            lambda m: m.change_capability_dependency(f"B{ms1936.TARGET}-0", reason=ms1936.FAULT_REASON),
        ),
        ms1936._scenario(
            "leaf_capability_fault",
            lambda m: m.change_capability_dependency(f"B{ms1936.TARGET}-{ms1936.DEPTH-1}", reason=ms1936.FAULT_REASON),
        ),
        ms1936._scenario(
            "shared_counterparty_fault",
            lambda m: m.change_operational_counterparty("CP0", reason=ms1936.FAULT_REASON),
        ),
    ]


def main() -> int:
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    source_start = _source_snapshot()
    started = time.time()

    scenarios = _cert_scenarios()
    inv_v1 = ms1936.INVENTORY
    graph_v1 = ms1936.GRAPH
    inv_v2, graph_v2 = _v2_append_inventory()
    inv_reordered = _reordered_inventory()
    graph_drift = _topology_drift_graph()

    inv_registry = {_sha(inv_v1): inv_v1, _sha(inv_v2): inv_v2}
    graph_registry = {_sha(graph_v1): graph_v1, _sha(graph_v2): graph_v2}

    rows = []
    for scenario in scenarios:
        cert = scenario["certificate"]
        exact = _verify_with_manifests(cert, inv_v1, graph_v1)
        appended_current = _verify_with_manifests(cert, inv_v2, graph_v2)
        reordered = _verify_with_manifests(cert, inv_reordered, graph_v1)
        topology_drift = _verify_with_manifests(cert, inv_v1, graph_drift)

        # Simulate a runtime that has advanced to V2 and does NOT retain V1.
        current_only_inv_registry = {_sha(inv_v2): inv_v2}
        current_only_graph_registry = {_sha(graph_v2): graph_v2}
        no_archive = _verify_from_registry(cert, current_only_inv_registry, current_only_graph_registry)

        # Archived V1 remains content-addressable even after current runtime moves V2.
        archived = _verify_from_registry(cert, inv_registry, graph_registry)

        # Demonstrate why strict manifest binding matters: because V2 appends new IDs,
        # naive decode with the V2 ordering may LOOK correct for old bit positions.
        naive_v2_decode = {
            "stale_capabilities": sorted(ms1936._unmask(cert["c"], inv_v2["capabilities"])),
            "stale_relations": sorted(ms1936._unmask(cert["q"], inv_v2["coordinations"])),
        }
        original = {
            "stale_capabilities": scenario["stale_capability_ids"],
            "stale_relations": scenario["stale_relation_ids"],
        }

        rows.append(
            {
                "name": scenario["name"],
                "certificate_sha256": scenario["certificate_sha256"],
                "exact_v1_verification": exact,
                "appended_v2_current_manifest_verification": appended_current,
                "reordered_inventory_verification": reordered,
                "topology_only_drift_verification": topology_drift,
                "current_v2_registry_without_v1_archive": no_archive,
                "archived_v1_registry_after_v2_current": archived,
                "naive_v2_decode_happens_to_match_old_closure": naive_v2_decode == original,
            }
        )

    manifest_v1_bytes = len(_canon({"inventory": inv_v1, "graph": graph_v1}))
    cert_total = sum(s["certificate_bytes"] for s in scenarios)
    full_total = sum(s["full_projection_bytes"] for s in scenarios)
    cert_plus_manifest = cert_total + manifest_v1_bytes

    source_end = _source_snapshot()

    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "source_snapshot_stable_during_run": source_start == source_end,
        "exact_v1_manifest_verifies_all": all(r["exact_v1_verification"]["status"] == "VERIFIED" for r in rows),
        "append_growth_current_manifest_rejected_all": all(r["appended_v2_current_manifest_verification"]["status"] == "REJECTED" for r in rows),
        "reordered_inventory_rejected_all": all(r["reordered_inventory_verification"]["status"] == "REJECTED" for r in rows),
        "topology_only_drift_rejected_all": all(r["topology_only_drift_verification"]["status"] == "REJECTED" for r in rows),
        "current_only_registry_without_archive_abstains_all": all(r["current_v2_registry_without_v1_archive"]["status"] == "ABSTAIN" for r in rows),
        "archived_v1_registry_recovers_all": all(r["archived_v1_registry_after_v2_current"]["status"] == "VERIFIED" for r in rows),
        "append_growth_can_look_naively_compatible_but_is_still_rejected": any(r["naive_v2_decode_happens_to_match_old_closure"] for r in rows),
        "certificate_plus_one_shared_manifest_smaller_than_full_projections": cert_plus_manifest < full_total,
    }

    receipt = {
        "schema": "pcmmad.ms1937.dynamic-manifest-certificate.v1",
        "classification": "NON_NOVELTY_TRACE_PORTABILITY_EXPERIMENT",
        "discriminator": "BITMAP_CERTIFICATE_DECODE_REQUIRES_EXACT_CONTENT_ADDRESSED_INVENTORY_AND_GRAPH_MANIFESTS",
        "current_repo_head": head,
        "origin_experiment_head": "6b0f012980a625143ea7137be848d6f13b57325b",
        "source_snapshot_start_sha256": source_start,
        "source_snapshot_end_sha256": source_end,
        "source_stable_during_run": source_start == source_end,
        "v1": {
            "inventory_sha256": _sha(inv_v1),
            "graph_sha256": _sha(graph_v1),
            "combined_manifest_bytes": manifest_v1_bytes,
        },
        "v2_append_growth": {
            "inventory_sha256": _sha(inv_v2),
            "graph_sha256": _sha(graph_v2),
            "new_coordination": "R8",
            "new_capabilities": ["B8-0", "B8-1", "B8-2"],
        },
        "drift_cases": {
            "reordered_inventory_sha256": _sha(inv_reordered),
            "topology_only_drift_graph_sha256": _sha(graph_drift),
        },
        "verification_rows": rows,
        "amortized_size": {
            "full_projection_bytes_four_scenarios": full_total,
            "certificates_bytes_four_scenarios": cert_total,
            "one_v1_inventory_plus_graph_manifest_bytes": manifest_v1_bytes,
            "certificates_plus_shared_v1_manifest_bytes": cert_plus_manifest,
            "bytes_saved_vs_full_even_including_one_manifest": full_total - cert_plus_manifest,
            "compression_ratio_full_over_certificates_plus_manifest": round(full_total / cert_plus_manifest, 4),
        },
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "interpretation": {
            "earned_statement": "CONTENT_ADDRESSED_MANIFEST_BINDING_PREVENTS_SILENT_CERTIFICATE_MISDECODE_ACROSS_INVENTORY_OR_TOPOLOGY_DRIFT_UNDER_THIS_FIXTURE",
            "recovery_statement": "OLD_CERTIFICATE_DECODE_REQUIRES_EXACT_REFERENCED_ARCHIVED_MANIFEST",
            "important_scar": "APPEND_ONLY_INVENTORY_GROWTH_CAN_PRESERVE_OLD_BITMAP_POSITIONS_AND_LOOK_PLAUSIBLE_BUT_MUST_STILL_FAIL_CURRENT_MANIFEST_BINDING",
            "next_question": "Canonicalize semantically unordered graph representations and measure manifest/certificate lifecycle costs under longer dynamic histories.",
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
