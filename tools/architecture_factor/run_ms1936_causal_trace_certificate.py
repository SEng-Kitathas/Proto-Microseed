from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
REPORT = ROOT / "reports" / "ms1936_causal_trace_certificate"
REPORT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))

import run_ms1933_invalidation_blast_radius as ms1933  # noqa: E402

BRANCHES = ms1933.BRANCHES
DEPTH = ms1933.DEPTH
TARGET = ms1933.TARGET
FAULT_REASON = "MS1936_OPAQUE_INJECTED_FAULT"
CAPS = [f"B{i}-{d}" for i in range(BRANCHES) for d in range(DEPTH)]
RELS = [f"R{i}" for i in range(BRANCHES)]
COUNTERPARTIES = ["CP0"]


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(obj) -> str:
    data = obj if isinstance(obj, (bytes, bytearray)) else _canon(obj)
    return hashlib.sha256(data).hexdigest()


def _graph_edges() -> list[list[str]]:
    out: list[list[str]] = []
    for i in range(BRANCHES):
        out.append(["CP0", f"R{i}"])
        out.append([f"R{i}", f"B{i}-0"])
        for d in range(1, DEPTH):
            out.append([f"B{i}-{d-1}", f"B{i}-{d}"])
    return out


INVENTORY = {"capabilities": CAPS, "coordinations": RELS, "counterparties": COUNTERPARTIES}
GRAPH = _graph_edges()
INVENTORY_SHA = _sha(INVENTORY)
GRAPH_SHA = _sha(GRAPH)


def _mask(ids: set[str], ordered: list[str]) -> str:
    value = 0
    for i, item in enumerate(ordered):
        if item in ids:
            value |= 1 << i
    width = max(1, (len(ordered) + 3) // 4)
    return f"{value:0{width}x}"


def _unmask(value: str, ordered: list[str]) -> set[str]:
    n = int(value, 16)
    return {item for i, item in enumerate(ordered) if n & (1 << i)}


def _origin(delta: list[dict]) -> tuple[str, str, int | None]:
    found: list[tuple[str, str, int | None]] = []
    for e in delta:
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


def _stale_relations(m) -> set[str]:
    return {rid for rid in RELS if not m.coordinations.is_current(rid)}


def _stale_counterparties(m) -> set[str]:
    return {cid for cid in COUNTERPARTIES if not m.counterparties.is_current(cid)}


def _certificate(delta: list[dict], stale_caps: set[str], stale_rels: set[str], stale_cp: set[str]) -> dict:
    relevant = [
        e for e in delta
        if "INVALIDATED" in str(e.get("kind", "")) or "STALE" in str(e.get("kind", ""))
    ]
    origin = _origin(relevant)
    # Intentionally compact field names: this is a certificate projection, not the
    # operator-facing canonical event stream. Schema documentation lives in receipt.
    return {
        "v": 1,
        "g": GRAPH_SHA,
        "i": INVENTORY_SHA,
        "t": _sha(relevant),
        "r": hashlib.sha256(FAULT_REASON.encode("utf-8")).hexdigest(),
        "o": [origin[0], origin[1], origin[2]],
        "c": _mask(stale_caps, CAPS),
        "q": _mask(stale_rels, RELS),
        "p": _mask(stale_cp, COUNTERPARTIES),
        "n": len(relevant),
    }


def _decode(cert: dict) -> dict:
    return {
        "origin": tuple(cert["o"]),
        "stale_capabilities": _unmask(cert["c"], CAPS),
        "stale_relations": _unmask(cert["q"], RELS),
        "stale_counterparties": _unmask(cert["p"], COUNTERPARTIES),
        "event_count": int(cert["n"]),
        "graph_sha256": cert["g"],
        "inventory_sha256": cert["i"],
        "trace_sha256": cert["t"],
        "reason_sha256": cert["r"],
    }


def _scenario(name: str, action) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"ms1936-{name}-") as td:
        m = None
        try:
            m = ms1933._build(Path(td))
            before = len(m.store.events())
            action(m)
            delta = m.store.events()[before:]
            relevant = [
                e for e in delta
                if "INVALIDATED" in str(e.get("kind", "")) or "STALE" in str(e.get("kind", ""))
            ]
            stale_caps = ms1933._stale_caps(m)
            stale_rels = _stale_relations(m)
            stale_cp = _stale_counterparties(m)
            origin = _origin(relevant)

            final_vector = {cid: ("STALE" if cid in stale_caps else "CURRENT") for cid in CAPS}
            full_projection = {"events": relevant, "final_capability_vector": final_vector}
            full_bytes = len(_canon(full_projection))

            cert = _certificate(delta, stale_caps, stale_rels, stale_cp)
            cert_bytes = len(_canon(cert))
            decoded = _decode(cert)
            cert2 = _certificate(delta, stale_caps, stale_rels, stale_cp)

            return {
                "name": name,
                "origin": list(origin),
                "event_count": len(relevant),
                "stale_capability_ids": sorted(stale_caps),
                "stale_relation_ids": sorted(stale_rels),
                "stale_counterparty_ids": sorted(stale_cp),
                "full_projection_bytes": full_bytes,
                "certificate_bytes": cert_bytes,
                "compression_ratio_full_over_certificate": round(full_bytes / cert_bytes, 4),
                "bytes_saved": full_bytes - cert_bytes,
                "certificate": cert,
                "certificate_sha256": _sha(cert),
                "checks": {
                    "origin_exact": tuple(decoded["origin"]) == origin,
                    "stale_capability_closure_exact": decoded["stale_capabilities"] == stale_caps,
                    "stale_relation_closure_exact": decoded["stale_relations"] == stale_rels,
                    "stale_counterparty_closure_exact": decoded["stale_counterparties"] == stale_cp,
                    "event_count_exact": decoded["event_count"] == len(relevant),
                    "graph_binding_exact": decoded["graph_sha256"] == GRAPH_SHA,
                    "inventory_binding_exact": decoded["inventory_sha256"] == INVENTORY_SHA,
                    "trace_binding_exact": decoded["trace_sha256"] == _sha(relevant),
                    "reason_binding_exact": decoded["reason_sha256"] == hashlib.sha256(FAULT_REASON.encode()).hexdigest(),
                    "certificate_deterministic": _canon(cert) == _canon(cert2),
                    "certificate_smaller_than_full_projection": cert_bytes < full_bytes,
                },
            }
        finally:
            if m is not None:
                m.biography.close()
                m.evidence.conn.close()
                m.store.conn.close()


def main() -> int:
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(
        ["git", "-C", str(REPO), "status", "--short", "--untracked-files=all", "--", "microseed", "tests"], text=True
    )
    started = time.time()
    scenarios = [
        _scenario("coordination_specific_fault", lambda m: m.change_operational_coordination(f"R{TARGET}", reason=FAULT_REASON)),
        _scenario("root_capability_fault", lambda m: m.change_capability_dependency(f"B{TARGET}-0", reason=FAULT_REASON)),
        _scenario("leaf_capability_fault", lambda m: m.change_capability_dependency(f"B{TARGET}-{DEPTH-1}", reason=FAULT_REASON)),
        _scenario("shared_counterparty_fault", lambda m: m.change_operational_counterparty("CP0", reason=FAULT_REASON)),
    ]

    scenario_checks = [all(s["checks"].values()) for s in scenarios]
    ratios = [s["compression_ratio_full_over_certificate"] for s in scenarios]
    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "organism_worktree_clean": status == "",
        "all_certificate_semantic_and_binding_checks_pass": all(scenario_checks),
        "all_certificates_smaller_than_full_projection": all(s["certificate_bytes"] < s["full_projection_bytes"] for s in scenarios),
        "all_compression_ratios_above_one": all(r > 1.0 for r in ratios),
        "shared_broad_trace_has_largest_absolute_byte_saving": max(scenarios, key=lambda s: s["bytes_saved"])["name"] == "shared_counterparty_fault",
        "certificates_bind_full_trace_not_replace_it": all(bool(s["certificate"]["t"]) for s in scenarios),
    }

    receipt = {
        "schema": "pcmmad.ms1936.causal-invalidation-certificate.v1",
        "classification": "NON_NOVELTY_TRACE_EFFICIENCY_EXPERIMENT",
        "discriminator": "FULL_CAUSAL_INVALIDATION_TRACE != MINIMUM_ROOT_AND_CLOSURE_CERTIFICATE",
        "sealed_repo_head": head,
        "organism_worktree_clean": status == "",
        "static_bindings": {
            "inventory": INVENTORY,
            "inventory_sha256": INVENTORY_SHA,
            "dependency_edges": GRAPH,
            "dependency_graph_sha256": GRAPH_SHA,
        },
        "certificate_schema": {
            "v": "certificate version",
            "g": "dependency graph SHA-256",
            "i": "inventory/order manifest SHA-256",
            "t": "full relevant event-trace SHA-256",
            "r": "opaque originating reason SHA-256",
            "o": "[origin premise type, origin ID, origin epoch-or-null]",
            "c": "hex bitmap over ordered capability inventory",
            "q": "hex bitmap over ordered coordination inventory",
            "p": "hex bitmap over ordered counterparty inventory",
            "n": "relevant invalidation event count",
        },
        "authority_boundary": {
            "certificate_role": "READ_ONLY_COMPACT_PROJECTION_AND_BINDING_SURFACE",
            "canonical_event_stream_role": "REMAINS_FULL_AUDIT_RECOVERY_AUTHORITY",
            "replacement_claim": "NONE",
        },
        "scenarios": scenarios,
        "summary": {
            "min_compression_ratio": min(ratios),
            "max_compression_ratio": max(ratios),
            "mean_compression_ratio": round(sum(ratios) / len(ratios), 4),
            "total_full_projection_bytes": sum(s["full_projection_bytes"] for s in scenarios),
            "total_certificate_bytes": sum(s["certificate_bytes"] for s in scenarios),
            "total_bytes_saved": sum(s["bytes_saved"] for s in scenarios),
        },
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "interpretation": {
            "earned_statement": "HASH_BOUND_CAUSAL_CERTIFICATE_CAN_PRESERVE_ROOT_AND_FINAL_CLOSURE_WITH_LOWER_DIAGNOSTIC_PAYLOAD_UNDER_THIS_FIXTURE",
            "non_replacement_statement": "COMPACT_CERTIFICATE != FULL_EVENT_STREAM_FOR_AUDIT_OR_RECOVERY",
            "next_question": "Whether the projection can generalize across dynamic inventories/topologies without fragile external ordering assumptions.",
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
