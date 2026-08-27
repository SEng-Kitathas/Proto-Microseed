from __future__ import annotations
from dataclasses import replace
import json, tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate,
    ExternalCapabilityQualifier, EpistemicStatus, QualificationState, QueryObligation,
)


def q(cid: str, deps=(), handler=None, scope=None):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS828-852-REPLAY",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler, operational_scope_id=scope,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ms828-852-replay-") as td:
        ms = Microseed(Path(td))
        out = {"schema": "microseed.ms828-852-maindev-replay.v0.2"}

        # MS833/834 boundary: useful but unregistered whole remains unavailable.
        ms.register_capability(q("A"))
        ms.register_capability(q("B"))
        out["unregistered_whole_before_nomination"] = ms.compose(["M"]).status

        # MS834-838: nomination remains proposal-only, then external evidence-bound admission.
        ev = ms.append_evidence(
            "REPLAY-M-TRANSFER",
            {"heldout_transfer": 0.98, "contexts": 100, "decoy_rejected": True},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="REPLAY_OF_MS835_838",
        )
        proposed = CapabilityContract(
            "M", "opaque-composite", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS834-838",), "UNKNOWN", {}, dependencies=("A", "B"),
            qualification=QualificationState.CANDIDATE,
        )
        cand = CapabilityCandidate(
            "M", proposed, (ev,),
            assistance_ancestry=("EXTERNAL_RECURRENCE_MINER", "FIXED_HELDOUT_EVALUATOR"),
            nomination_basis="REPLAY_EXTERNAL_NOMINATION",
            source_trace_ids=("opaque-trace-1", "opaque-trace-2"),
            operational_signature={"structural_pattern": [0, 1, 0]},
        )
        ms.nominate_capability_candidate(cand)
        out["nominated_but_not_admitted"] = ms.compose(["M"]).status
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-REPLAY-QUALIFIER").qualify(cand)
        out["external_ticket_state"] = ticket.state.value
        ms.admit_capability_candidate(ticket)
        out["admitted_whole"] = ms.compose(["M"]).status

        # MS839: whole becomes a part again.
        ms.register_capability(q("D"))
        ms.register_capability(q("N", deps=("M", "D")))
        r2 = ms.compose(["N"])
        out["second_order_status"] = r2.status
        out["second_order_plan"] = list(r2.plan)

        # MS841-843: replay the exact metadata/currentness mismatch that triggered evolution.
        stale = ms.change_capability_dependency("A", reason="REPLAY_PRIMITIVE_DRIFT")
        out["stale_set_after_primitive_drift"] = sorted(stale)
        out["capability_states_after_drift"] = {
            x: ms.capabilities.contracts[x].qualification.value for x in ("A", "M", "N")
        }
        out["development_states_after_drift"] = {
            x: ms.development.records[x].qualification.value for x in ("A", "M", "N")
        }
        out["second_order_after_drift"] = ms.compose(["N"]).status

        # Content-bound ticket tamper attack.
        out["forged_ticket_rejected"] = False
        try:
            # Candidate is already admitted, so use a fresh candidate to test ticket validation.
            ev2 = ms.append_evidence("REPLAY-X", {"ok": True}, EpistemicStatus.PROVED)
            p2 = CapabilityContract(
                "X", "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
                ("REPLAY",), "UNKNOWN", {}, qualification=QualificationState.CANDIDATE,
            )
            c2 = CapabilityCandidate("X", p2, (ev2,), nomination_basis="REPLAY")
            ms.nominate_capability_candidate(c2)
            t2 = ExternalCapabilityQualifier(ms.evidence).qualify(c2)
            ms.admit_capability_candidate(replace(t2, candidate_sha256="0" * 64))
        except ValueError as exc:
            out["forged_ticket_rejected"] = "DIGEST" in str(exc)

        # MS844-845 narrow integration: opaque operational scope blocks cross-regime invocation.
        ms.register_capability(q("LOCAL", handler=lambda x: x + 1, scope="opaque-regime-A"))
        bad = ms.capabilities.invoke(
            "LOCAL", QueryObligation("Q", "opaque", operational_scope_id="opaque-regime-B"), x=1
        )
        good = ms.capabilities.invoke(
            "LOCAL", QueryObligation("Q", "opaque", operational_scope_id="opaque-regime-A"), x=1
        )
        out["wrong_scope"] = bad["reason"]
        out["right_scope_value"] = good["value"]

        status = ms.status()
        out["language"] = status["language"]
        out["endogenous_candidate_discovery"] = status["endogenous_candidate_discovery"]
        out["current_next_ms"] = status["next_ms"]
        out["current_next_started"] = status.get(f"ms{status['next_ms']}_started")

        out["checks"] = {
            "unregistered_remains_no_path": out["unregistered_whole_before_nomination"] == "NO_PATH",
            "nomination_not_admission": out["nominated_but_not_admitted"] == "NO_PATH",
            "external_admission_reuse": out["admitted_whole"] == "COMPOSED_EPHEMERAL",
            "whole_becomes_part_again": out["second_order_status"] == "COMPOSED_EPHEMERAL",
            "transitive_metadata_stale": set(out["capability_states_after_drift"].values()) == {"STALE"},
            "development_registry_agrees": set(out["development_states_after_drift"].values()) == {"STALE"},
            "execution_after_drift_conservative": out["second_order_after_drift"] == "NO_PATH",
            "ticket_tamper_rejected": out["forged_ticket_rejected"],
            "scope_mismatch_unknown": out["wrong_scope"] == "OPERATIONAL_SCOPE_MISMATCH",
            "prelingual_hard_stop": out["language"].startswith("DEFERRED") and out["current_next_ms"] >= 1203 and out["current_next_started"] is False,
            "later_discovery_promotion_still_not_truth_authority": (
                "PROPOSAL_GENERATOR" in out["endogenous_candidate_discovery"]
                and "NOT_TRUTH_AUTHORITY" in out["endogenous_candidate_discovery"]
            ),
        }
        out["all_pass"] = all(out["checks"].values())
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
