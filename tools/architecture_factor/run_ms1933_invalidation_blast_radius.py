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
REPORT = ROOT / "reports" / "ms1933_invalidation_blast_radius"
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


from microseed import (  # noqa: E402
    Authority,
    CapabilityContract,
    Microseed,
    OperationalCoordinationContract,
    OperationalCounterpartyContract,
    QualificationState,
)

BRANCHES = 8
DEPTH = 3
TARGET = 3
TOTAL_CAPS = BRANCHES * DEPTH


def _cp() -> OperationalCounterpartyContract:
    c = OperationalCounterpartyContract(
        counterparty_id="CP0",
        purpose="ms1933-common-opaque-premise",
        signature_sha256="",
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS1933-EXPERIMENT",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXPERIMENTAL_FIXTURE",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _coord(i: int) -> OperationalCoordinationContract:
    c = OperationalCoordinationContract(
        coordination_id=f"R{i}",
        purpose="ms1933-branch-specific-opaque-premise",
        participant_counterparty_epochs=(("CP0", 0),),
        signature_sha256="",
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS1933-EXPERIMENT",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXPERIMENTAL_FIXTURE",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _cap(cid: str, deps: tuple[str, ...] = ()) -> CapabilityContract:
    return CapabilityContract(
        cid,
        "ms1933-opaque-capability",
        {},
        {},
        (),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1933-EXPERIMENT",),
        "CURRENT",
        {},
        dependencies=deps,
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: 1,
    )


def _build(state: Path) -> Microseed:
    m = Microseed(state)
    m.register_operational_counterparty(_cp())
    for i in range(BRANCHES):
        m.register_operational_coordination(_coord(i))
        root = f"B{i}-0"
        m.register_capability(_cap(root), coordination_dependencies=((f"R{i}", 0),))
        previous = root
        for d in range(1, DEPTH):
            cid = f"B{i}-{d}"
            m.register_capability(_cap(cid, (previous,)))
            previous = cid
    return m


def _stale_caps(m: Microseed) -> set[str]:
    return {
        cid
        for cid, c in m.capabilities.contracts.items()
        if c.currentness != "CURRENT" or c.qualification == QualificationState.STALE
    }


def _current_caps(m: Microseed) -> set[str]:
    return set(m.capabilities.contracts) - _stale_caps(m)


def _scenario(name: str, action) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"ms1933-{name}-") as td:
        m = None
        try:
            m = _build(Path(td))
            before_current = _current_caps(m)
            before_rel_current = {
                rid for rid in m.coordinations.contracts if m.coordinations.is_current(rid)
            }
            assert len(before_current) == TOTAL_CAPS, (name, len(before_current))
            assert len(before_rel_current) == BRANCHES, (name, len(before_rel_current))

            returned = set(action(m))
            stale = _stale_caps(m)
            current = _current_caps(m)
            stale_relations = {
                rid for rid in m.coordinations.contracts if not m.coordinations.is_current(rid)
            }

            # Named baseline: one global authorization epoch shared by all 24 contexts.
            # Any load-bearing premise change increments it, so all contexts must recheck.
            global_recheck = TOTAL_CAPS
            local_recheck = len(stale)
            avoided = global_recheck - local_recheck
            gain = (global_recheck / local_recheck) if local_recheck else None

            return {
                "name": name,
                "returned_stale_ids": sorted(returned),
                "local_stale_capability_ids": sorted(stale),
                "local_current_capability_ids": sorted(current),
                "local_stale_capability_count": local_recheck,
                "local_stale_relation_ids": sorted(stale_relations),
                "local_stale_relation_count": len(stale_relations),
                "global_authorization_epoch_baseline_recheck_count": global_recheck,
                "rechecks_avoided_vs_global_epoch": avoided,
                "locality_gain_vs_global_epoch": gain,
                "unrelated_current_count": len(current),
            }
        finally:
            if m is not None:
                m.biography.close()
                m.evidence.conn.close()
                m.store.conn.close()


def main() -> int:
    head = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    source_start = _source_snapshot()

    started = time.time()
    scenarios = [
        _scenario(
            "coordination_specific_drift",
            lambda m: m.change_operational_coordination(
                f"R{TARGET}", reason="MS1933_COORDINATION_SPECIFIC_DRIFT"
            ),
        ),
        _scenario(
            "root_capability_drift",
            lambda m: m.change_capability_dependency(
                f"B{TARGET}-0", reason="MS1933_ROOT_CAPABILITY_DRIFT"
            ),
        ),
        _scenario(
            "leaf_capability_drift",
            lambda m: m.change_capability_dependency(
                f"B{TARGET}-{DEPTH - 1}", reason="MS1933_LEAF_CAPABILITY_DRIFT"
            ),
        ),
        _scenario(
            "shared_counterparty_drift",
            lambda m: m.change_operational_counterparty(
                "CP0", reason="MS1933_SHARED_COUNTERPARTY_DRIFT"
            ),
        ),
    ]

    by = {row["name"]: row for row in scenarios}
    source_end = _source_snapshot()

    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "source_snapshot_stable_during_run": source_start == source_end,
        "coordination_specific_stales_exact_branch": by["coordination_specific_drift"]["local_stale_capability_count"] == DEPTH,
        "coordination_specific_stales_one_relation": by["coordination_specific_drift"]["local_stale_relation_count"] == 1,
        "root_drift_stales_exact_downstream_branch": by["root_capability_drift"]["local_stale_capability_count"] == DEPTH,
        "leaf_drift_stales_only_leaf": by["leaf_capability_drift"]["local_stale_capability_count"] == 1,
        "shared_counterparty_drift_stales_all_capabilities": by["shared_counterparty_drift"]["local_stale_capability_count"] == TOTAL_CAPS,
        "shared_counterparty_drift_stales_all_relations": by["shared_counterparty_drift"]["local_stale_relation_count"] == BRANCHES,
        "narrow_coordination_avoids_global_rechecks": by["coordination_specific_drift"]["rechecks_avoided_vs_global_epoch"] == TOTAL_CAPS - DEPTH,
        "broad_shared_premise_loses_locality_advantage": by["shared_counterparty_drift"]["rechecks_avoided_vs_global_epoch"] == 0,
    }

    receipt = {
        "schema": "pcmmad.ms1933.invalidation-blast-radius.v1",
        "classification": "NON_NOVELTY_ARCHITECTURE_FACTOR_EXPERIMENT",
        "discriminator": "LOCAL_DEPENDENCY_INVALIDATION != GLOBAL_AUTHORIZATION_EPOCH_RECHECK_BLAST_RADIUS",
        "current_repo_head": head,
        "origin_experiment_head": "6b0f012980a625143ea7137be848d6f13b57325b",
        "source_snapshot_start_sha256": source_start,
        "source_snapshot_end_sha256": source_end,
        "source_stable_during_run": source_start == source_end,
        "fixture": {
            "branches": BRANCHES,
            "capability_chain_depth": DEPTH,
            "total_capabilities": TOTAL_CAPS,
            "common_counterparty_count": 1,
            "independent_coordination_relation_count": BRANCHES,
        },
        "baseline": {
            "name": "GLOBAL_AUTHORIZATION_EPOCH_BASELINE",
            "definition": "A single global authorization epoch is bound by every active capability authorization context. Any load-bearing premise drift increments the epoch, requiring all active contexts to recheck before use. Recheck uses the same underlying owners, so extensional decisions can remain identical after revalidation.",
            "scope_claim": "SPECIFIC_NAMED_BASELINE_ONLY_NOT_ALL_GLOBAL_MANAGERS",
        },
        "scenarios": scenarios,
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "started_at_epoch": started,
        "duration_seconds": round(time.time() - started, 6),
        "authority": "ENGINEERING_MEASUREMENT_ONLY_NO_NOVELTY_OR_CANONICAL_PROMOTION",
    }
    (REPORT / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
