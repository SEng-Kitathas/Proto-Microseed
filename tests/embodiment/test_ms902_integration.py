from __future__ import annotations
from pathlib import Path
import hashlib
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, ExternalCapabilityQualifier,
    EpistemicStatus, QualificationState, OperationalFrameContract, OperationalTrace,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms902-")
    return td, Microseed(Path(td.name))


def q(cid, deps=()):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS902-TEST",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def frame(fid="FRAME-1", signature="frame-signature-v1"):
    return OperationalFrameContract(
        frame_id=fid,
        purpose="opaque-operational-action-effect-frame",
        signature_sha256=hashlib.sha256(signature.encode()).hexdigest(),
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS878-902",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNAL_FRAME_QUALIFICATION",),
        invariants=("NO_SEMANTIC_IDENTITY_AUTHORITY",),
    )


def build_frame_bound_discovery(ms, fid="FRAME-1"):
    ms.register_operational_frame(frame(fid))
    ms.register_capability(q("A")); ms.register_capability(q("B"))
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(
            f"a{i}", ("A",), ((1.0, 0.0),), "r0", frame_id=fid
        ))
        ms.record_operational_trace(OperationalTrace(
            f"b{i}", ("B",), ((0.0, 1.0),), "r0", frame_id=fid
        ))
    for scope in ("r0", "r1"):
        for i in range(10):
            ms.record_operational_trace(OperationalTrace(
                f"m-{scope}-{i}", ("A", "B"), ((1.0, 0.0), (0.0, 2.0)),
                scope, frame_id=fid,
            ))
    proposals = ms.discover_capability_candidates()
    assert proposals
    return proposals[0]["candidate_id"]


def external_ticket(ms, cid, eid="HSP-MS902-HOLDOUT"):
    cand = ms.capability_candidates[cid]
    ext = ms.append_evidence(
        eid, {"heldout_transfer": 0.99, "negative_control": 0.01},
        EpistemicStatus.PRESSURE_SUPPORTED, source="HSP_EXTERNAL",
    )
    return ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS902").qualify(
        cand, qualification_evidence=(ext,)
    )


def test_frame_bound_trace_captures_epoch_and_candidate_ancestry():
    td, ms = make_ms()
    try:
        cid = build_frame_bound_discovery(ms)
        cand = ms.capability_candidates[cid]
        assert cand.operational_signature["frame_epochs"] == [["FRAME-1", 0]]
        assert "QUALIFIED_OPERATIONAL_FRAME:FRAME-1@0" in cand.assistance_ancestry
        assert "SUPPLIED_EFFECT_COORDINATES" not in cand.assistance_ancestry
        assert "STABLE_CAPABILITY_HANDLE_IDENTITY" not in cand.assistance_ancestry
        assert "SUPPLIED_HIGHER_LEVEL_OPERATIONAL_TRACE_GROUPING" in cand.assistance_ancestry
    finally:
        td.cleanup()


def test_pending_candidate_frame_drift_blocks_admission():
    td, ms = make_ms()
    try:
        cid = build_frame_bound_discovery(ms)
        ticket = external_ticket(ms, cid)
        stale = ms.change_operational_frame("FRAME-1", reason="MATERIAL_RELATION_CHANGE")
        assert stale == set()
        try:
            ms.admit_capability_candidate(ticket)
        except ValueError as exc:
            assert "CANDIDATE_FRAME_EPOCH_DRIFT:FRAME-1" in str(exc)
        else:
            raise AssertionError("frame-stale pending candidate admitted")
    finally:
        td.cleanup()


def test_admitted_frame_bound_capability_and_second_order_dependent_stale_transitively():
    td, ms = make_ms()
    try:
        cid = build_frame_bound_discovery(ms)
        ticket = external_ticket(ms, cid)
        ms.admit_capability_candidate(ticket)
        n = q("N", deps=(cid,))
        ms.register_capability(n)
        assert ms.capabilities.contracts[cid].qualification == QualificationState.SHADOW_QUALIFIED
        assert ms.capabilities.contracts["N"].qualification == QualificationState.SHADOW_QUALIFIED
        stale = ms.change_operational_frame("FRAME-1", reason="MATERIAL_RELATION_CHANGE")
        assert stale == {cid, "N"}
        assert ms.capabilities.contracts[cid].qualification == QualificationState.STALE
        assert ms.capabilities.contracts["N"].qualification == QualificationState.STALE
        assert ms.development.records[cid].qualification == QualificationState.STALE
        assert ms.development.records["N"].qualification == QualificationState.STALE
        assert ms.compose(["N"]).status == "NO_PATH"
    finally:
        td.cleanup()


def test_stale_frame_rejects_new_trace():
    td, ms = make_ms()
    try:
        ms.register_operational_frame(frame())
        ms.register_capability(q("A"))
        ms.change_operational_frame("FRAME-1", reason="MATERIAL_RELATION_CHANGE")
        try:
            ms.record_operational_trace(OperationalTrace(
                "late", ("A",), ((1.0,),), "r0", frame_id="FRAME-1"
            ))
        except ValueError as exc:
            assert "unknown/stale operational frame:FRAME-1" in str(exc)
        else:
            raise AssertionError("trace recorded against stale frame")
    finally:
        td.cleanup()


def test_frame_contract_is_not_semantic_identity_authority():
    td, ms = make_ms()
    try:
        f = frame()
        ms.register_operational_frame(f)
        snap = ms.frames.snapshot()["FRAME-1"]["contract"]
        assert snap["authority"] == Authority.DERIVED_READ_ONLY
        assert "NO_SEMANTIC_IDENTITY_AUTHORITY" in snap["invariants"]
        assert ms.status()["biography_identity_claim"] == "NOT_QUALIFIED"
        assert ms.status()["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally:
        td.cleanup()
