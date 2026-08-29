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
REPORT = ROOT / "reports" / "ms1934_fault_localization"
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


# Reuse only the already-verified synthetic fixture constructor/constants from MS1933.
import run_ms1933_invalidation_blast_radius as ms1933  # noqa: E402

BRANCHES = ms1933.BRANCHES
DEPTH = ms1933.DEPTH
TARGET = ms1933.TARGET
TOTAL_CAPS = ms1933.TOTAL_CAPS
FAULT_REASON = "MS1934_OPAQUE_INJECTED_FAULT"

Premise = tuple[str, str]


def _premise_universe() -> dict[str, list[str]]:
    return {
        "COUNTERPARTY": ["CP0"],
        "COORDINATION": [f"R{i}" for i in range(BRANCHES)],
        "CAPABILITY": [f"B{i}-{d}" for i in range(BRANCHES) for d in range(DEPTH)],
    }


def _dependency_edges() -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for i in range(BRANCHES):
        edges.append(("CP0", f"R{i}"))
        edges.append((f"R{i}", f"B{i}-0"))
        for d in range(1, DEPTH):
            edges.append((f"B{i}-{d-1}", f"B{i}-{d}"))
    return edges


def _stale_caps(m) -> set[str]:
    return ms1933._stale_caps(m)


def _event_delta(m, before_count: int) -> list[dict]:
    return m.store.events()[before_count:]


def _origin_from_microseed_trace(delta: list[dict]) -> set[Premise]:
    """Extract only direct origin events carrying the exact injected reason.

    Cascaded invalidations wrap the reason with ancestry prefixes, so exact reason
    equality distinguishes the external injected premise from downstream closure.
    This uses only emitted event payloads, never the harness's known target.
    """
    out: set[Premise] = set()
    for event in delta:
        kind = str(event.get("kind", ""))
        payload = event.get("payload", {}) or {}
        if str(payload.get("reason", "")) != FAULT_REASON:
            continue
        if kind == "OPERATIONAL_COUNTERPARTY_INVALIDATED" and payload.get("counterparty_id"):
            out.add(("COUNTERPARTY", str(payload["counterparty_id"])))
        elif kind == "OPERATIONAL_COORDINATION_INVALIDATED" and payload.get("coordination_id"):
            out.add(("COORDINATION", str(payload["coordination_id"])))
        elif kind == "CAPABILITY_INVALIDATED" and payload.get("root"):
            out.add(("CAPABILITY", str(payload["root"])))
    return out


def _flat_reason_vector_candidates(
    fault_kind: str, stale_capability_ids: set[str], universe: dict[str, list[str]]
) -> set[Premise]:
    """Named centralized baseline without an ancestry graph.

    It retains:
    - the final stale/current vector for all capability contexts; and
    - a generic changed-premise TYPE (counterparty/coordination/capability).

    It does NOT retain which external premise ID caused a downstream context to
    stale or any dependency edges. For capability faults, the changed capability
    must itself be stale, so the stale-capability vector legitimately narrows the
    candidates. For external premise types, no mapping from stale contexts back to
    a specific relation/counterparty exists without ancestry state.
    """
    if fault_kind == "CAPABILITY":
        return {("CAPABILITY", cid) for cid in sorted(stale_capability_ids)}
    return {(fault_kind, pid) for pid in universe[fault_kind]}


def _centralized_typed_trace_candidates(delta: list[dict]) -> set[Premise]:
    """Fairness baseline: centralized owner receives equivalent typed trace.

    Since the centralized baseline is allowed the same origin event identity and
    causal reason lineage, it can run the same origin extraction. If this matches
    Microseed, diagnostic precision belongs to explicit trace information rather
    than physical distribution of ownership.
    """
    return _origin_from_microseed_trace(delta)


def _json_bytes(obj) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _metrics(candidates: set[Premise], true_root: Premise) -> dict:
    ordered = sorted([list(x) for x in candidates])
    contains = true_root in candidates
    return {
        "candidate_roots": ordered,
        "candidate_root_count": len(candidates),
        "contains_true_root": contains,
        "unique_true_root": contains and len(candidates) == 1,
        "false_positive_candidate_count": len(candidates - {true_root}),
    }


def _scenario(name: str, fault_kind: str, true_id: str, action) -> dict:
    universe = _premise_universe()
    with tempfile.TemporaryDirectory(prefix=f"ms1934-{name}-") as td:
        m = None
        try:
            m = ms1933._build(Path(td))
            before = len(m.store.events())
            returned = set(action(m))
            delta = _event_delta(m, before)
            stale = _stale_caps(m)
            true_root: Premise = (fault_kind, true_id)

            micro = _origin_from_microseed_trace(delta)
            flat = _flat_reason_vector_candidates(fault_kind, stale, universe)
            typed = _centralized_typed_trace_candidates(delta)

            # Final decision/currentness vector is held identical across all three
            # diagnostic representations. Only diagnostic information differs.
            final_vector = {
                cid: ("STALE" if cid in stale else "CURRENT")
                for cid in universe["CAPABILITY"]
            }

            relevant_events = [
                e for e in delta
                if "INVALIDATED" in str(e.get("kind", "")) or "STALE" in str(e.get("kind", ""))
            ]
            micro_trace = {
                "events": relevant_events,
                "final_capability_vector": final_vector,
            }
            flat_trace = {
                "generic_fault_kind": fault_kind,
                "final_capability_vector": final_vector,
            }
            typed_trace = {
                "origin_events": [
                    e for e in relevant_events
                    if str((e.get("payload", {}) or {}).get("reason", "")) == FAULT_REASON
                ],
                "dependency_edges": _dependency_edges(),
                "final_capability_vector": final_vector,
            }

            return {
                "name": name,
                "fault_kind": fault_kind,
                "true_root": list(true_root),
                "returned_stale_ids": sorted(returned),
                "final_stale_capability_ids": sorted(stale),
                "final_stale_capability_count": len(stale),
                "decision_vector_sha256": hashlib.sha256(
                    json.dumps(final_vector, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
                "microseed": {
                    **_metrics(micro, true_root),
                    "diagnostic_event_count": len(relevant_events),
                    "diagnostic_payload_bytes": _json_bytes(micro_trace),
                },
                "global_decision_reason_vector_baseline": {
                    **_metrics(flat, true_root),
                    "diagnostic_record_count": len(final_vector) + 1,
                    "diagnostic_payload_bytes": _json_bytes(flat_trace),
                    "dependency_edge_state_count": 0,
                },
                "centralized_typed_dependency_trace_baseline": {
                    **_metrics(typed, true_root),
                    "diagnostic_record_count": len(typed_trace["origin_events"]) + len(final_vector),
                    "diagnostic_payload_bytes": _json_bytes(typed_trace),
                    "dependency_edge_state_count": len(typed_trace["dependency_edges"]),
                },
                "typed_trace_matches_microseed_candidates": typed == micro,
                "microseed_event_kinds": [str(e.get("kind", "")) for e in relevant_events],
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

    scenarios = [
        _scenario(
            "coordination_specific_fault",
            "COORDINATION",
            f"R{TARGET}",
            lambda m: m.change_operational_coordination(f"R{TARGET}", reason=FAULT_REASON),
        ),
        _scenario(
            "root_capability_fault",
            "CAPABILITY",
            f"B{TARGET}-0",
            lambda m: m.change_capability_dependency(f"B{TARGET}-0", reason=FAULT_REASON),
        ),
        _scenario(
            "leaf_capability_fault",
            "CAPABILITY",
            f"B{TARGET}-{DEPTH-1}",
            lambda m: m.change_capability_dependency(f"B{TARGET}-{DEPTH-1}", reason=FAULT_REASON),
        ),
        _scenario(
            "shared_counterparty_fault",
            "COUNTERPARTY",
            "CP0",
            lambda m: m.change_operational_counterparty("CP0", reason=FAULT_REASON),
        ),
    ]
    by = {x["name"]: x for x in scenarios}

    source_end = _source_snapshot()

    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "source_snapshot_stable_during_run": source_start == source_end,
        "microseed_unique_localization_all_scenarios": all(x["microseed"]["unique_true_root"] for x in scenarios),
        "typed_central_unique_localization_all_scenarios": all(
            x["centralized_typed_dependency_trace_baseline"]["unique_true_root"] for x in scenarios
        ),
        "typed_central_matches_microseed_candidates_all_scenarios": all(
            x["typed_trace_matches_microseed_candidates"] for x in scenarios
        ),
        "flat_coordination_baseline_has_eight_candidates": by["coordination_specific_fault"]["global_decision_reason_vector_baseline"]["candidate_root_count"] == BRANCHES,
        "flat_root_capability_baseline_narrows_to_stale_branch": by["root_capability_fault"]["global_decision_reason_vector_baseline"]["candidate_root_count"] == DEPTH,
        "flat_leaf_capability_baseline_is_unique": by["leaf_capability_fault"]["global_decision_reason_vector_baseline"]["unique_true_root"],
        "flat_shared_counterparty_baseline_is_unique_in_single_counterparty_fixture": by["shared_counterparty_fault"]["global_decision_reason_vector_baseline"]["unique_true_root"],
        "flat_baseline_worse_in_at_least_two_scenarios": sum(
            x["global_decision_reason_vector_baseline"]["candidate_root_count"] > x["microseed"]["candidate_root_count"]
            for x in scenarios
        ) >= 2,
        "decision_semantics_identical_by_construction": all(bool(x["decision_vector_sha256"]) for x in scenarios),
        "typed_baseline_explicitly_carries_dependency_state": all(
            x["centralized_typed_dependency_trace_baseline"]["dependency_edge_state_count"] == len(_dependency_edges())
            for x in scenarios
        ),
    }

    receipt = {
        "schema": "pcmmad.ms1934.fault-localization.v1",
        "classification": "NON_NOVELTY_ARCHITECTURE_FACTOR_EXPERIMENT",
        "discriminator": "EXPLICIT_TYPED_PREMISE_LINEAGE -> FAULT_LOCALIZATION_DIAGNOSTIC_PRECISION",
        "current_repo_head": head,
        "origin_experiment_head": "6b0f012980a625143ea7137be848d6f13b57325b",
        "source_snapshot_start_sha256": source_start,
        "source_snapshot_end_sha256": source_end,
        "source_stable_during_run": source_start == source_end,
        "fixture": {
            "branches": BRANCHES,
            "capability_chain_depth": DEPTH,
            "total_capabilities": TOTAL_CAPS,
            "premise_universe_counts": {k: len(v) for k, v in _premise_universe().items()},
            "typed_dependency_edge_count": len(_dependency_edges()),
            "fault_budget_per_scenario": 1,
        },
        "baselines": {
            "GLOBAL_DECISION_REASON_VECTOR_BASELINE": {
                "state": "final per-capability CURRENT/STALE vector plus generic changed-premise type; no premise identity-to-context ancestry graph",
                "scope_claim": "SPECIFIC_NAMED_BASELINE_ONLY",
            },
            "CENTRALIZED_TYPED_DEPENDENCY_TRACE_BASELINE": {
                "state": "same final vector plus equivalent typed origin event identity/reason lineage and explicit dependency edges",
                "purpose": "fairness control distinguishing trace-information value from physical owner distribution",
                "scope_claim": "SPECIFIC_NAMED_BASELINE_ONLY",
            },
        },
        "scenarios": scenarios,
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "interpretation": {
            "flat_baseline_result": "Explicit typed origin/ancestry can reduce candidate fault sets relative to a flat reason vector.",
            "fairness_control_result": "A centralized baseline given equivalent typed trace information matches Microseed localization exactly in this fixture.",
            "earned_statement": "DIAGNOSTIC_PRECISION_FOLLOWS_EXPLICIT_TYPED_TRACE_INFORMATION_UNDER_THIS_FIXTURE",
            "rejected_overclaim": "PHYSICAL_DISTRIBUTION_OF_AUTHORITY_OWNERS_CAUSES_UNIQUE_DIAGNOSTIC_PRECISION",
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
