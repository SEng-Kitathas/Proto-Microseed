from __future__ import annotations
from pathlib import Path
import hashlib
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, ExternalCapabilityQualifier,
    EpistemicStatus, QualificationState, OperationalFrameContract,
    EpisodeSchemaContract, OperationalTrace,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms927-")
    return td, Microseed(Path(td.name))


def q(cid, deps=()):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS927-TEST",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def frame(fid="FRAME-EP", signature="frame-ep-v1"):
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


def episode_schema(sid="EP-1", fid="FRAME-EP", signature="episode-schema-v1"):
    return EpisodeSchemaContract(
        schema_id=sid,
        purpose="opaque-operational-episode-grouping-schema",
        signature_sha256=hashlib.sha256(signature.encode()).hexdigest(),
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS903-927",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNAL_EPISODE_SCHEMA_QUALIFICATION",),
        frame_epochs=((fid, 0),),
        invariants=("NO_SEMANTIC_EPISODE_OR_IDENTITY_AUTHORITY",),
    )


def build_episode_bound_discovery(ms):
    ms.register_operational_frame(frame())
    ms.register_episode_schema(episode_schema())
    ms.register_capability(q("A")); ms.register_capability(q("B"))
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(
            f"a{i}", ("A",), ((1.0, 0.0),), "r0",
            frame_id="FRAME-EP", episode_schema_id="EP-1",
        ))
        ms.record_operational_trace(OperationalTrace(
            f"b{i}", ("B",), ((0.0, 1.0),), "r0",
            frame_id="FRAME-EP", episode_schema_id="EP-1",
        ))
    for scope in ("r0", "r1"):
        for i in range(10):
            ms.record_operational_trace(OperationalTrace(
                f"m-{scope}-{i}", ("A", "B"), ((1.0, 0.0), (0.0, 2.0)), scope,
                frame_id="FRAME-EP", episode_schema_id="EP-1",
            ))
    proposals = ms.discover_capability_candidates()
    assert proposals
    return proposals[0]["candidate_id"]


def external_ticket(ms, cid, eid="HSP-MS927-HOLDOUT"):
    cand = ms.capability_candidates[cid]
    ext = ms.append_evidence(
        eid, {"heldout_transfer": 0.99, "negative_control": 0.01},
        EpistemicStatus.PRESSURE_SUPPORTED, source="HSP_EXTERNAL",
    )
    return ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS927").qualify(
        cand, qualification_evidence=(ext,)
    )


def test_episode_bound_trace_captures_epoch_and_candidate_ancestry():
    td, ms = make_ms()
    try:
        cid = build_episode_bound_discovery(ms)
        cand = ms.capability_candidates[cid]
        assert cand.operational_signature["episode_schema_epochs"] == [["EP-1", 0]]
        assert cand.operational_signature["frame_epochs"] == [["FRAME-EP", 0]]
        assert "QUALIFIED_OPERATIONAL_EPISODE_SCHEMA:EP-1@0" in cand.assistance_ancestry
        assert "SUPPLIED_TRACE_BOUNDARIES" not in cand.assistance_ancestry
        assert "SUPPLIED_HIGHER_LEVEL_OPERATIONAL_TRACE_GROUPING" not in cand.assistance_ancestry
        assert "EPISODE_SCHEMA_EPOCH_BOUND" in cand.proposed_contract.invariants
    finally:
        td.cleanup()


def test_pending_candidate_episode_schema_drift_blocks_admission():
    td, ms = make_ms()
    try:
        cid = build_episode_bound_discovery(ms)
        ticket = external_ticket(ms, cid)
        stale = ms.change_episode_schema("EP-1", reason="MATERIAL_GROUPING_CHANGE")
        assert stale == set()
        try:
            ms.admit_capability_candidate(ticket)
        except ValueError as exc:
            assert "CANDIDATE_EPISODE_SCHEMA_EPOCH_DRIFT:EP-1" in str(exc)
        else:
            raise AssertionError("episode-schema-stale pending candidate admitted")
    finally:
        td.cleanup()


def test_admitted_episode_bound_capability_and_second_order_dependent_stale_transitively():
    td, ms = make_ms()
    try:
        cid = build_episode_bound_discovery(ms)
        ms.admit_capability_candidate(external_ticket(ms, cid))
        ms.register_capability(q("N", deps=(cid,)))
        stale = ms.change_episode_schema("EP-1", reason="MATERIAL_GROUPING_CHANGE")
        assert stale == {cid, "N"}
        assert ms.capabilities.contracts[cid].qualification == QualificationState.STALE
        assert ms.capabilities.contracts["N"].qualification == QualificationState.STALE
        assert ms.development.records[cid].qualification == QualificationState.STALE
        assert ms.development.records["N"].qualification == QualificationState.STALE
        assert ms.compose(["N"]).status == "NO_PATH"
    finally:
        td.cleanup()


def test_episode_schema_can_stale_while_lower_frame_remains_current():
    td, ms = make_ms()
    try:
        ms.register_operational_frame(frame())
        ms.register_episode_schema(episode_schema())
        ms.change_episode_schema("EP-1", reason="ORDER_RELATION_CHANGED")
        assert ms.frames.is_current("FRAME-EP")
        assert not ms.episodes.is_current("EP-1")
    finally:
        td.cleanup()


def test_frame_drift_stales_frame_bound_episode_schema():
    td, ms = make_ms()
    try:
        ms.register_operational_frame(frame())
        ms.register_episode_schema(episode_schema())
        ms.change_operational_frame("FRAME-EP", reason="LOWER_RELATION_CHANGED")
        assert not ms.episodes.is_current("EP-1")
        assert ms.development.records["EP-1"].qualification == QualificationState.STALE
    finally:
        td.cleanup()


def test_episode_schema_provenance_persists_in_trace_without_selfhood_claim():
    with tempfile.TemporaryDirectory(prefix="microseed-ms927-persist-") as td:
        root = Path(td)
        ms = Microseed(root)
        ms.register_operational_frame(frame())
        ms.register_episode_schema(episode_schema())
        ms.register_capability(q("A"))
        ms.record_operational_trace(OperationalTrace(
            "persist-1", ("A",), ((1.0,),), "r0",
            frame_id="FRAME-EP", episode_schema_id="EP-1",
        ))
        ms2 = Microseed(root)
        t = ms2.operational_traces["persist-1"]
        assert t.episode_schema_id == "EP-1"
        assert t.episode_schema_epoch == 0
        assert ms2.status()["identity_claim"] == "NOT_QUALIFIED"
        # Registry currentness is deliberately not inferred merely from historical bytes.
        assert not ms2.episodes.is_current("EP-1")


def test_episode_grouping_mechanism_not_silently_promoted_into_entity():
    td, ms = make_ms()
    try:
        assert not hasattr(ms, "record_operational_event")
        assert not hasattr(ms, "propose_episode_grouping")
        s = ms.status()
        assert "NOT_ENTITY_TRUTH_AUTHORITY" in s["episode_grouping"]
        assert s["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        assert s["research_terminal_ms"] >= 1152
        assert s["next_ms"] >= 1203
        assert s["next_ms"] >= 1278
    finally:
        td.cleanup()
