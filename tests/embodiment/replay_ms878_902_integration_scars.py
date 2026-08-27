from __future__ import annotations
import hashlib, json, tempfile, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from microseed import (
    Microseed, Authority, CapabilityContract, ExternalCapabilityQualifier,
    EpistemicStatus, QualificationState, OperationalFrameContract, OperationalTrace,
)


def q(cid, deps=()):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS878-902-REPLAY",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def frame(fid="FRAME-R"):
    return OperationalFrameContract(
        frame_id=fid,
        purpose="opaque-operational-action-effect-frame",
        signature_sha256=hashlib.sha256(b"frame-r-v1").hexdigest(),
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS878-902",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("HSP_EXTERNAL_FRAME_QUALIFICATION",),
        invariants=("NO_SEMANTIC_IDENTITY_AUTHORITY",),
    )


with tempfile.TemporaryDirectory(prefix="microseed-ms902-replay-") as td:
    ms = Microseed(Path(td))
    ms.register_operational_frame(frame())
    ms.register_capability(q("A")); ms.register_capability(q("B"))
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(f"a{i}", ("A",), ((1.0,0.0),), "r0", frame_id="FRAME-R"))
        ms.record_operational_trace(OperationalTrace(f"b{i}", ("B",), ((0.0,1.0),), "r0", frame_id="FRAME-R"))
    for scope in ("r0","r1"):
        for i in range(10):
            ms.record_operational_trace(OperationalTrace(
                f"m-{scope}-{i}", ("A","B"), ((1.0,0.0),(0.0,2.0)), scope, frame_id="FRAME-R"
            ))
    proposals = ms.discover_capability_candidates()
    cid = proposals[0]["candidate_id"]
    cand = ms.capability_candidates[cid]
    before = ms.compose([cid]).status
    ext = ms.append_evidence("HSP-MS902-HOLDOUT", {"transfer":0.99}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
    ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS902").qualify(cand, qualification_evidence=(ext,))
    ms.admit_capability_candidate(ticket)
    after = ms.compose([cid]).status
    ms.register_capability(q("N", deps=(cid,)))
    second = ms.compose(["N"]).status
    frame_epoch_before = ms.frames.epochs["FRAME-R"]
    stale = sorted(ms.change_operational_frame("FRAME-R", reason="MATERIAL_RELATION_CHANGE"))
    frame_epoch_after = ms.frames.epochs["FRAME-R"]
    post = ms.compose(["N"]).status

    # Separate pending-candidate replay: external ticket issued, then frame changes.
    ms2 = Microseed(Path(td)/"pending")
    ms2.register_operational_frame(frame("FRAME-P"))
    ms2.register_capability(q("PA")); ms2.register_capability(q("PB"))
    for i in range(6):
        ms2.record_operational_trace(OperationalTrace(f"pa{i}", ("PA",), ((1.0,0.0),), "r0", frame_id="FRAME-P"))
        ms2.record_operational_trace(OperationalTrace(f"pb{i}", ("PB",), ((0.0,1.0),), "r0", frame_id="FRAME-P"))
    for scope in ("r0","r1"):
        for i in range(10):
            ms2.record_operational_trace(OperationalTrace(
                f"pm-{scope}-{i}", ("PA","PB"), ((1.0,0.0),(0.0,2.0)), scope, frame_id="FRAME-P"
            ))
    pcid = ms2.discover_capability_candidates()[0]["candidate_id"]
    pc = ms2.capability_candidates[pcid]
    pe = ms2.append_evidence("HSP-PENDING", {"transfer":0.99}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
    pt = ExternalCapabilityQualifier(ms2.evidence, qualifier_id="HSP-MS902").qualify(pc, qualification_evidence=(pe,))
    ms2.change_operational_frame("FRAME-P", reason="AFTER_TICKET")
    pending_rejected = False
    pending_reason = None
    try:
        ms2.admit_capability_candidate(pt)
    except ValueError as exc:
        pending_rejected = True
        pending_reason = str(exc)

    status = ms.status()
    checks = {
        "frame_epoch_bound_into_candidate": cand.operational_signature["frame_epochs"] == [["FRAME-R",0]],
        "proposal_not_admission": before == "NO_PATH",
        "external_admission_reuse": after == "COMPOSED_EPHEMERAL",
        "whole_becomes_part_again": second == "COMPOSED_EPHEMERAL",
        "frame_epoch_advances": frame_epoch_before == 0 and frame_epoch_after == 1,
        "frame_drift_stales_admitted_whole": cid in stale,
        "frame_drift_stales_second_order": "N" in stale,
        "post_drift_execution_conservative": post == "NO_PATH",
        "pending_frame_drift_rejected": pending_rejected and "CANDIDATE_FRAME_EPOCH_DRIFT" in (pending_reason or ""),
        "frame_not_semantic_identity": "NO_SEMANTIC_IDENTITY_AUTHORITY" in ms.frames.frames["FRAME-R"].invariants,
        "higher_level_trace_grouping_still_supplied": "SUPPLIED_HIGHER_LEVEL_OPERATIONAL_TRACE_GROUPING" in cand.assistance_ancestry,
        "prelingual_hard_stop": status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE" and status["next_ms"] >= 1203 and status.get(f"ms{status['next_ms']}_started") is False,
    }
    out = {
        "schema":"microseed.ms878-902-maindev-replay.v0.4",
        "checks":checks,
        "all_pass":all(checks.values()),
        "candidate_id":cid,
        "frame_epoch_before":frame_epoch_before,
        "frame_epoch_after":frame_epoch_after,
        "stale_after_frame_drift":stale,
        "before_external_qualification":before,
        "after_external_admission":after,
        "second_order_before_frame_drift":second,
        "second_order_after_frame_drift":post,
        "pending_frame_drift_rejected":pending_rejected,
        "pending_frame_drift_reason":pending_reason,
        "status":status,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    raise SystemExit(0 if out["all_pass"] else 1)
