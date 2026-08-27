from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate,
    ExternalCapabilityQualifier, EpistemicStatus, QualificationState,
    OperationalTrace,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms877-")
    return td, Microseed(Path(td.name))


def q(cid, deps=()):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS877-TEST",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def build_discovery_traces(ms, a="A", b="B"):
    ms.register_capability(q(a)); ms.register_capability(q(b))
    for i in range(6):
        ms.record_operational_trace(OperationalTrace(f"a{i}", (a,), ((1.0, 0.0),), "r0"))
        ms.record_operational_trace(OperationalTrace(f"b{i}", (b,), ((0.0, 1.0),), "r0"))
    for scope in ("r0", "r1"):
        for i in range(10):
            ms.record_operational_trace(
                OperationalTrace(f"m-{scope}-{i}", (a, b), ((1.0, 0.0), (0.0, 2.0)), scope)
            )


def test_endogenous_discovery_is_proposal_only():
    td, ms = make_ms()
    try:
        build_discovery_traces(ms)
        proposals = ms.discover_capability_candidates()
        assert proposals
        cid = proposals[0]["candidate_id"]
        assert cid in ms.capability_candidates
        assert cid not in ms.capabilities.contracts
        assert ms.compose([cid]).status == "NO_PATH"
        cand = ms.capability_candidates[cid]
        assert cand.evidence[0].disposition == EpistemicStatus.UNKNOWN_INCOMPLETE
        assert "SUPPLIED_TRACE_BOUNDARIES" in cand.assistance_ancestry
    finally:
        td.cleanup()


def test_unknown_nomination_evidence_cannot_self_green():
    td, ms = make_ms()
    try:
        build_discovery_traces(ms)
        cid = ms.discover_capability_candidates()[0]["candidate_id"]
        cand = ms.capability_candidates[cid]
        ticket = ExternalCapabilityQualifier(ms.evidence).qualify(cand)
        assert ticket.state == QualificationState.REJECTED
        assert "NON_SUPPORTIVE_EVIDENCE" in ticket.reason
    finally:
        td.cleanup()


def test_external_post_nomination_evidence_can_qualify_without_rewriting_proposal():
    td, ms = make_ms()
    try:
        build_discovery_traces(ms)
        cid = ms.discover_capability_candidates()[0]["candidate_id"]
        cand = ms.capability_candidates[cid]
        before = cand.digest()
        ext = ms.append_evidence(
            "HSP-HOLDOUT-MS877", {"heldout": 0.99, "shuffled_control": 0.02},
            EpistemicStatus.PRESSURE_SUPPORTED, source="HSP_EXTERNAL",
        )
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS877").qualify(
            cand, qualification_evidence=(ext,)
        )
        assert ticket.state == QualificationState.SHADOW_QUALIFIED
        assert cand.digest() == before
        assert ticket.evidence_ids == tuple(x.evidence_id for x in cand.evidence)
        assert tuple(x.evidence_id for x in ticket.qualification_evidence) == (ext.evidence_id,)
        ms.admit_capability_candidate(ticket)
        assert ms.compose([cid]).status == "COMPOSED_EPHEMERAL"
    finally:
        td.cleanup()


def test_pending_candidate_dependency_drift_blocks_admission():
    td, ms = make_ms()
    try:
        build_discovery_traces(ms)
        cid = ms.discover_capability_candidates()[0]["candidate_id"]
        cand = ms.capability_candidates[cid]
        ext = ms.append_evidence("HSP-DRIFT", {"ok": True}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence).qualify(cand, qualification_evidence=(ext,))
        ms.change_capability_dependency("A", reason="AFTER_NOMINATION")
        try:
            ms.admit_capability_candidate(ticket)
        except ValueError as exc:
            assert "CANDIDATE_DEPENDENCY" in str(exc)
        else:
            raise AssertionError("stale pending candidate admitted")
    finally:
        td.cleanup()


def test_ticket_decision_cannot_be_forged_stronger_than_external_evidence():
    td, ms = make_ms()
    try:
        build_discovery_traces(ms)
        cid = ms.discover_capability_candidates()[0]["candidate_id"]
        cand = ms.capability_candidates[cid]
        ext = ms.append_evidence("HSP-FORGE", {"ok": True}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence).qualify(cand, qualification_evidence=(ext,))
        forged = replace(ticket, authority=Authority.EFFECT)
        try:
            ms.admit_capability_candidate(forged)
        except ValueError as exc:
            assert "DECISION_MISMATCH" in str(exc) or "EFFECT_AUTHORITY" in str(exc)
        else:
            raise AssertionError("forged stronger ticket admitted")
    finally:
        td.cleanup()


def test_trace_persists_as_history_without_selfhood_claim():
    with tempfile.TemporaryDirectory(prefix="microseed-ms877-persist-") as td:
        p = Path(td)
        ms = Microseed(p)
        ms.register_capability(q("A"))
        ms.record_operational_trace(OperationalTrace("persist-1", ("A",), ((1.0,),), "r0"))
        assert len(ms.operational_traces) == 1
        # A new runtime can recover the trace bytes, but capability registry and identity
        # are not thereby reconstructed/qualified.
        ms2 = Microseed(p)
        assert "persist-1" in ms2.operational_traces
        assert ms2.status()["identity_claim"] == "NOT_QUALIFIED"
