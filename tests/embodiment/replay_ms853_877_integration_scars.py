from __future__ import annotations
import json, tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from microseed import (
    Microseed, Authority, CapabilityContract, ExternalCapabilityQualifier,
    EpistemicStatus, QualificationState, OperationalTrace,
)


def q(cid: str, deps=()):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS853-877-REPLAY",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ms853-877-replay-") as td:
        ms = Microseed(Path(td))
        out = {"schema": "microseed.ms853-877-maindev-replay.v0.3"}
        ms.register_capability(q("A")); ms.register_capability(q("B"))

        for i in range(6):
            ms.record_operational_trace(OperationalTrace(f"a{i}", ("A",), ((1.0, 0.0),), "r0"))
            ms.record_operational_trace(OperationalTrace(f"b{i}", ("B",), ((0.0, 1.0),), "r0"))
        for scope in ("r0", "r1"):
            for i in range(10):
                ms.record_operational_trace(
                    OperationalTrace(f"m-{scope}-{i}", ("A", "B"), ((1.0, 0.0), (0.0, 2.0)), scope)
                )

        proposals = ms.discover_capability_candidates()
        out["proposal_count"] = len(proposals)
        cid = proposals[0]["candidate_id"] if proposals else None
        out["candidate_id"] = cid
        cand = ms.capability_candidates[cid] if cid else None
        out["proposal_evidence_disposition"] = cand.evidence[0].disposition.value if cand else None
        out["before_external_qualification"] = ms.compose([cid]).status if cid else None

        default_ticket = ExternalCapabilityQualifier(ms.evidence).qualify(cand)
        out["self_evidence_ticket_state"] = default_ticket.state.value
        out["self_evidence_ticket_reason"] = default_ticket.reason

        external = ms.append_evidence(
            "HSP-MS877-REPLAY",
            {"heldout_transfer": 0.99, "shuffled_control": 0.01},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="HSP_EXTERNAL_REPLAY",
        )
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS877-REPLAY").qualify(
            cand, qualification_evidence=(external,)
        )
        out["external_ticket_state"] = ticket.state.value
        out["candidate_digest_before_admission"] = cand.digest()
        ms.admit_capability_candidate(ticket)
        out["after_external_admission"] = ms.compose([cid]).status
        out["candidate_digest_after_admission"] = cand.digest()

        # Whole becomes a part again.
        ms.register_capability(q("D"))
        ms.register_capability(q("N", deps=(cid, "D")))
        out["second_order_before_drift"] = ms.compose(["N"]).status

        stale = ms.change_capability_dependency("A", reason="MS877_REPLAY_DRIFT")
        out["stale_after_dependency_drift"] = sorted(stale)
        out["second_order_after_drift"] = ms.compose(["N"]).status

        # Pending candidate attack: build a fresh candidate under new current primitives.
        ms2 = Microseed(Path(td) / "pending")
        ms2.register_capability(q("P")); ms2.register_capability(q("Q"))
        for i in range(6):
            ms2.record_operational_trace(OperationalTrace(f"p{i}", ("P",), ((1.0, 0.0),), "r0"))
            ms2.record_operational_trace(OperationalTrace(f"q{i}", ("Q",), ((0.0, 1.0),), "r0"))
        for scope in ("r0", "r1"):
            for i in range(10):
                ms2.record_operational_trace(OperationalTrace(f"pq-{scope}-{i}", ("P", "Q"), ((1.0, 0.0), (0.0, 2.0)), scope))
        pcid = ms2.discover_capability_candidates()[0]["candidate_id"]
        pc = ms2.capability_candidates[pcid]
        pe = ms2.append_evidence("HSP-PENDING", {"heldout": True}, EpistemicStatus.PROVED, source="HSP_EXTERNAL_REPLAY")
        pt = ExternalCapabilityQualifier(ms2.evidence).qualify(pc, qualification_evidence=(pe,))
        ms2.change_capability_dependency("P", reason="DRIFT_AFTER_NOMINATION")
        out["pending_drift_rejected"] = False
        try:
            ms2.admit_capability_candidate(pt)
        except ValueError as exc:
            out["pending_drift_rejected"] = "CANDIDATE_DEPENDENCY" in str(exc)
            out["pending_drift_reason"] = str(exc)

        status = ms.status()
        out["status"] = status
        out["checks"] = {
            "endogenous_proposal_exists": bool(proposals),
            "proposal_not_admission": out["before_external_qualification"] == "NO_PATH",
            "self_generated_unknown_not_supportive": out["self_evidence_ticket_state"] == "REJECTED",
            "external_post_nomination_evidence_qualifies": out["external_ticket_state"] == "SHADOW_QUALIFIED",
            "proposal_history_not_rewritten": out["candidate_digest_before_admission"] == out["candidate_digest_after_admission"],
            "admitted_whole_reusable": out["after_external_admission"] == "COMPOSED_EPHEMERAL",
            "whole_becomes_part_again": out["second_order_before_drift"] == "COMPOSED_EPHEMERAL",
            "transitive_stale_after_prerequisite_drift": cid in stale and "N" in stale and out["second_order_after_drift"] == "NO_PATH",
            "pending_candidate_drift_rejected": out["pending_drift_rejected"],
            "prelingual_hard_stop": status["language"].startswith("DEFERRED") and status["next_ms"] >= 1203 and status.get(f"ms{status['next_ms']}_started") is False,
            "trace_frame_not_laundered": (
                "SUPPLIED_TRACE_BOUNDARIES" in cand.assistance_ancestry
                and "SUPPLIED_EFFECT_COORDINATES" in cand.assistance_ancestry
                and "STABLE_CAPABILITY_HANDLE_IDENTITY" in cand.assistance_ancestry
            ),
        }
        out["all_pass"] = all(out["checks"].values())
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["all_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
