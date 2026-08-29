from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT
REPORT = ROOT / "reports" / "ms1935_authority_coupling"
REPORT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(REPO))

from microseed.runtime.commitment import (  # noqa: E402
    RelationalCommitment,
    TernaryCommitment,
    conjoin_required_commitments,
)

AXES = ("NEED", "PRIORITY", "INFORMATION", "FEASIBILITY", "ROUTE")


def _commit(axis: str, value: str, case_id: str) -> RelationalCommitment:
    return RelationalCommitment(
        commitment_id=f"{case_id}:{axis}",
        target_id=case_id,
        commitment=TernaryCommitment(value),
        reason=f"SYNTHETIC_{axis}_{value}",
        premise_ids=(f"PREMISE:{case_id}:{axis}",),
    )


def _microseed_stance(vector: dict[str, str], *, stuck_yes_axis: str | None = None) -> str:
    rows = []
    for axis in AXES:
        value = "YES" if axis == stuck_yes_axis else vector[axis]
        rows.append(_commit(axis, value, vector["CASE_ID"]))
    c = conjoin_required_commitments(
        rows,
        commitment_id=f"COMBINED:{vector['CASE_ID']}:{stuck_yes_axis or 'NONE'}",
        target_id=vector["CASE_ID"],
        reason_prefix="MS1935_REQUIRED_PREMISE",
    )
    return c.commitment.value


def _centralized_typed_stance(vector: dict[str, str], *, stuck_yes_axis: str | None = None) -> str:
    # Same independently-addressable premise semantics, centralized in one manager.
    values = [("YES" if axis == stuck_yes_axis else vector[axis]) for axis in AXES]
    if "NO" in values:
        return "NO"
    if all(v == "YES" for v in values):
        return "YES"
    return "UNKNOWN"


def _central_shared_evaluator_stuck_yes(vector: dict[str, str]) -> str:
    # Named coupled baseline: every premise type routes through one shared evaluator.
    # A single stuck-YES mutation in that shared evaluator returns YES for every axis.
    values = ["YES" for _ in AXES]
    return "YES" if all(v == "YES" for v in values) else "UNKNOWN"


def _cases() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    # Five distinct all-licensed contexts.
    for i in range(5):
        row = {a: "YES" for a in AXES}
        row["CASE_ID"] = f"ALL_YES_{i}"
        out.append(row)

    # Four sole-NO and two sole-UNKNOWN contexts per premise type.
    for axis in AXES:
        for i in range(4):
            row = {a: "YES" for a in AXES}
            row[axis] = "NO"
            row["CASE_ID"] = f"ONLY_{axis}_NO_{i}"
            out.append(row)
        for i in range(2):
            row = {a: "YES" for a in AXES}
            row[axis] = "UNKNOWN"
            row["CASE_ID"] = f"ONLY_{axis}_UNKNOWN_{i}"
            out.append(row)

    # One double-NO context for every unordered premise pair. These should remain
    # blocked when only one independently-addressable premise evaluator is faulty.
    for a, b in itertools.combinations(AXES, 2):
        row = {x: "YES" for x in AXES}
        row[a] = "NO"
        row[b] = "NO"
        row["CASE_ID"] = f"DOUBLE_NO_{a}_{b}"
        out.append(row)

    return out


def _classify(expected: str, observed: str) -> str:
    if expected == observed:
        return "CORRECT"
    if observed == "YES" and expected != "YES":
        return "FALSE_AUTHORIZATION"
    if expected == "YES" and observed != "YES":
        return "FALSE_REFUSAL_OR_ABSTENTION"
    return "OTHER_STANCE_ERROR"


def _evaluate_site(cases: list[dict[str, str]], axis: str) -> dict:
    rows = []
    for case in cases:
        correct = _microseed_stance(case)
        local_mut = _microseed_stance(case, stuck_yes_axis=axis)
        central_typed_mut = _centralized_typed_stance(case, stuck_yes_axis=axis)
        rows.append(
            {
                "case_id": case["CASE_ID"],
                "correct": correct,
                "microseed_typed_mutation": local_mut,
                "centralized_typed_mutation": central_typed_mut,
                "microseed_error": _classify(correct, local_mut),
                "centralized_typed_error": _classify(correct, central_typed_mut),
            }
        )

    def count(key: str, label: str) -> int:
        return sum(r[key] == label for r in rows)

    return {
        "mutated_premise_axis": axis,
        "mutation": "ONE_PREMISE_EVALUATOR_STUCK_YES",
        "case_count": len(rows),
        "microseed_false_authorizations": count("microseed_error", "FALSE_AUTHORIZATION"),
        "centralized_typed_false_authorizations": count("centralized_typed_error", "FALSE_AUTHORIZATION"),
        "microseed_false_refusals_or_abstentions": count("microseed_error", "FALSE_REFUSAL_OR_ABSTENTION"),
        "centralized_typed_false_refusals_or_abstentions": count("centralized_typed_error", "FALSE_REFUSAL_OR_ABSTENTION"),
        "microseed_wrong_case_ids": [r["case_id"] for r in rows if r["microseed_error"] != "CORRECT"],
        "centralized_typed_wrong_case_ids": [r["case_id"] for r in rows if r["centralized_typed_error"] != "CORRECT"],
        "typed_central_matches_microseed_every_case": all(
            r["microseed_typed_mutation"] == r["centralized_typed_mutation"] for r in rows
        ),
        "double_no_cases_remain_blocked_under_single_typed_fault": all(
            r["microseed_typed_mutation"] == "NO"
            for r in rows
            if r["case_id"].startswith("DOUBLE_NO_")
        ),
    }


def main() -> int:
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(
        ["git", "-C", str(REPO), "status", "--short", "--untracked-files=all", "--", "microseed", "tests"], text=True
    )
    started = time.time()
    cases = _cases()

    # Verify the pure centralized typed control is extensionally identical to the
    # actual Microseed conjunction before applying mutations.
    baseline_equivalence = all(
        _microseed_stance(c) == _centralized_typed_stance(c) for c in cases
    )

    typed_sites = [_evaluate_site(cases, axis) for axis in AXES]

    shared_rows = []
    for case in cases:
        correct = _microseed_stance(case)
        observed = _central_shared_evaluator_stuck_yes(case)
        shared_rows.append(
            {
                "case_id": case["CASE_ID"],
                "correct": correct,
                "observed": observed,
                "error": _classify(correct, observed),
            }
        )
    shared_false_auth = sum(r["error"] == "FALSE_AUTHORIZATION" for r in shared_rows)
    shared_false_refusal = sum(r["error"] == "FALSE_REFUSAL_OR_ABSTENTION" for r in shared_rows)

    correct_counts = {
        stance: sum(_microseed_stance(c) == stance for c in cases)
        for stance in ("YES", "NO", "UNKNOWN")
    }

    # All typed site mutations should corrupt only the four sole-NO + two
    # sole-UNKNOWN contexts for that one premise = 6 unsafe false authorizations.
    expected_typed_false_auth = 6
    per_site_false_auth = [r["microseed_false_authorizations"] for r in typed_sites]

    checks = {
        "descends_from_ms1924": subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", "6b0f012980a625143ea7137be848d6f13b57325b", head], capture_output=True).returncode == 0,
        "organism_worktree_clean": status == "",
        "centralized_typed_unmutated_matches_microseed_all_cases": baseline_equivalence,
        "microseed_typed_mutation_false_auth_is_six_each_axis": all(x == expected_typed_false_auth for x in per_site_false_auth),
        "centralized_typed_mutation_matches_microseed_each_axis": all(r["typed_central_matches_microseed_every_case"] for r in typed_sites),
        "double_no_cases_contained_under_single_typed_fault": all(r["double_no_cases_remain_blocked_under_single_typed_fault"] for r in typed_sites),
        "shared_evaluator_stuck_yes_false_authorizes_every_non_yes_case": shared_false_auth == (len(cases) - correct_counts["YES"]),
        "shared_evaluator_stuck_yes_has_no_false_refusals": shared_false_refusal == 0,
        "shared_evaluator_has_larger_unsafe_blast_radius_than_any_typed_site": shared_false_auth > max(per_site_false_auth),
        "authorized_cases_remain_yes_under_stuck_yes_mutations": all(
            (_microseed_stance(c, stuck_yes_axis=axis) == "YES")
            for axis in AXES for c in cases if _microseed_stance(c) == "YES"
        ),
    }

    source = REPO / "microseed" / "runtime" / "commitment.py"
    receipt = {
        "schema": "pcmmad.ms1935.authority-coupling.v1",
        "classification": "NON_NOVELTY_ARCHITECTURE_FACTOR_EXPERIMENT",
        "discriminator": "INDEPENDENT_TYPED_PREMISE_FACTORIZATION -> UNSAFE_AUTHORITY_FAULT_CONTAINMENT",
        "sealed_repo_head": head,
        "organism_worktree_clean": status == "",
        "microseed_gate_source": {
            "path": "microseed/runtime/commitment.py",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "semantic_rule": "NO vetoes; YES only if every required premise licenses YES; otherwise UNKNOWN",
            "program_step_axes_grounding": list(AXES),
        },
        "fixture": {
            "premise_axes": list(AXES),
            "case_count": len(cases),
            "correct_stance_counts": correct_counts,
            "single_fault_budget_per_run": 1,
            "case_construction": {
                "all_yes": 5,
                "sole_no_per_axis": 4,
                "sole_unknown_per_axis": 2,
                "double_no_pair_cases": 10,
            },
        },
        "architectures": {
            "MICROSEED_TYPED_PREMISE_GATE": "Actual conjoin_required_commitments semantics; one independently addressable premise evaluator is mutated per run.",
            "CENTRALIZED_TYPED_SUBMODULE_BASELINE": "One central manager containing the same five independently addressable typed premise evaluators and the same conjunction semantics.",
            "CENTRAL_SHARED_PREMISE_EVALUATOR_BASELINE": "All five premise types route through one shared evaluator function; the single injected fault makes that shared evaluator return YES for every premise.",
        },
        "typed_site_mutations": typed_sites,
        "shared_evaluator_mutation": {
            "mutation": "ONE_SHARED_EVALUATOR_STUCK_YES",
            "case_count": len(shared_rows),
            "false_authorizations": shared_false_auth,
            "false_refusals_or_abstentions": shared_false_refusal,
            "wrong_case_ids": [r["case_id"] for r in shared_rows if r["error"] != "CORRECT"],
        },
        "checks": checks,
        "passed": sum(bool(v) for v in checks.values()),
        "total": len(checks),
        "all_pass": all(checks.values()),
        "interpretation": {
            "factorized_result": "A single stuck-YES fault in one typed premise evaluator only removes that premise's veto; cases with another independent NO remain blocked.",
            "fairness_control_result": "A centralized manager with the same typed submodule factorization matches Microseed exactly under corresponding single-site mutations.",
            "coupled_baseline_result": "A single stuck-YES fault in one evaluator shared across all premise types removes every premise veto and false-authorizes every non-YES case in the matrix.",
            "earned_statement": "INDEPENDENT_PREMISE_FACTORIZATION_BOUNDS_SINGLE_EVALUATOR_UNSAFE_AUTHORITY_FAULT_BLAST_RADIUS_UNDER_THIS_MATRIX",
            "rejected_overclaim": "PHYSICAL_DISTRIBUTION_OF_PREMISE_OWNERS_IS_REQUIRED_FOR_FAULT_CONTAINMENT",
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
