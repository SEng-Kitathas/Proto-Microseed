from dataclasses import replace
from pathlib import Path
import tempfile

from microseed import (
    Microseed, Authority, CapabilityContract, CapabilityCandidate,
    ExternalCapabilityQualifier, EpistemicStatus, QualificationState, QueryObligation,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms852-")
    return td, Microseed(Path(td.name))


def qualified(cid, *, deps=(), handler=None, scope=None):
    return CapabilityContract(
        cid, "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("TEST",), "CURRENT", {}, dependencies=tuple(deps),
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=handler, operational_scope_id=scope,
    )


def test_transitive_invalidation_matches_development_graph():
    td, ms = make_ms()
    try:
        for c in (
            qualified("P"), qualified("M1", deps=("P",)),
            qualified("M2", deps=("M1",)), qualified("M3", deps=("M2",)),
        ):
            ms.register_capability(c)
        stale = ms.change_capability_dependency("P", reason="CHILD_POLICY_DRIFT")
        assert stale == {"P", "M1", "M2", "M3"}
        assert all(ms.capabilities.contracts[x].qualification == QualificationState.STALE for x in stale)
        assert all(ms.development.records[x].qualification == QualificationState.STALE for x in stale)
        assert ms.compose(["M3"]).status == "NO_PATH"
    finally:
        td.cleanup()


def test_candidate_nomination_is_not_admission():
    td, ms = make_ms()
    try:
        ms.register_capability(qualified("A"))
        ev = ms.append_evidence("E-CAND", {"transfer": 0.98}, EpistemicStatus.PRESSURE_SUPPORTED)
        proposed = CapabilityContract(
            "M", "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS834-837",), "UNKNOWN", {}, dependencies=("A",),
            qualification=QualificationState.CANDIDATE,
        )
        cand = CapabilityCandidate(
            "M", proposed, (ev,), assistance_ancestry=("EXTERNAL_RECURRENCE_MINER",),
            nomination_basis="RECURRENCE_PLUS_HELD_OUT_TRANSFER",
            source_trace_ids=("TRACE-1", "TRACE-2"),
            operational_signature={"shape": [0, 1, 0]},
        )
        digest = ms.nominate_capability_candidate(cand)
        assert digest == cand.digest()
        assert "M" not in ms.capabilities.contracts
        assert ms.compose(["M"]).status == "NO_PATH"
    finally:
        td.cleanup()


def test_external_qualification_admits_whole_and_second_order_reuse():
    td, ms = make_ms()
    try:
        ms.register_capability(qualified("A", handler=lambda: 1))
        ms.register_capability(qualified("B", handler=lambda: 2))
        ev = ms.append_evidence(
            "E-M-QUAL", {"heldout_transfer": 0.98, "contexts": 100},
            EpistemicStatus.PRESSURE_SUPPORTED, source="HSP-LAB",
        )
        proposed = CapabilityContract(
            "M", "opaque-composite", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("MS834-839",), "UNKNOWN", {}, dependencies=("A", "B"),
            qualification=QualificationState.CANDIDATE,
        )
        cand = CapabilityCandidate(
            "M", proposed, (ev,), assistance_ancestry=("EXTERNAL_RECURRENCE_MINER", "FIXED_HELDOUT_EVALUATOR"),
            nomination_basis="EXTERNAL_LAB_CANDIDATE",
        )
        ms.nominate_capability_candidate(cand)
        external = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS852-TEST")
        ticket = external.qualify(cand)
        assert ticket.state == QualificationState.SHADOW_QUALIFIED
        admitted = ms.admit_capability_candidate(ticket, handler=lambda: 3)
        assert admitted.qualification == QualificationState.SHADOW_QUALIFIED
        assert ms.compose(["M"]).status == "COMPOSED_EPHEMERAL"

        ms.register_capability(qualified("D", handler=lambda: 4))
        ms.register_capability(qualified("N", deps=("M", "D"), handler=lambda: 7))
        r = ms.compose(["N"])
        assert r.status == "COMPOSED_EPHEMERAL"
        assert r.plan.index("M") < r.plan.index("N")

        stale = ms.change_capability_dependency("A", reason="PREREQUISITE_DRIFT")
        assert {"A", "M", "N"}.issubset(stale)
        assert ms.capabilities.contracts["N"].qualification == QualificationState.STALE
        assert ms.compose(["N"]).status == "NO_PATH"
    finally:
        td.cleanup()


def test_forged_candidate_digest_ticket_is_rejected():
    td, ms = make_ms()
    try:
        ev = ms.append_evidence("E-FORGE", {"ok": True}, EpistemicStatus.PROVED)
        proposed = CapabilityContract(
            "X", "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("TEST",), "UNKNOWN", {}, qualification=QualificationState.CANDIDATE,
        )
        cand = CapabilityCandidate("X", proposed, (ev,), nomination_basis="TEST")
        ms.nominate_capability_candidate(cand)
        ticket = ExternalCapabilityQualifier(ms.evidence).qualify(cand)
        forged = replace(ticket, candidate_sha256="0" * 64)
        try:
            ms.admit_capability_candidate(forged)
        except ValueError as exc:
            assert "DIGEST" in str(exc)
        else:
            raise AssertionError("forged ticket admitted")
        assert "X" not in ms.capabilities.contracts
    finally:
        td.cleanup()


def test_zero_and_negative_evidence_do_not_admit():
    td, ms = make_ms()
    try:
        p0 = CapabilityContract(
            "ZERO", "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("TEST",), "UNKNOWN", {}, qualification=QualificationState.CANDIDATE,
        )
        c0 = CapabilityCandidate("ZERO", p0, (), nomination_basis="EMPTY")
        ms.nominate_capability_candidate(c0)
        t0 = ExternalCapabilityQualifier(ms.evidence).qualify(c0)
        assert t0.state == QualificationState.REJECTED
        try:
            ms.admit_capability_candidate(t0)
        except ValueError:
            pass
        else:
            raise AssertionError("zero-evidence candidate admitted")

        neg = ms.append_evidence(
            "E-NEG-CAND", {"counterexample": True}, EpistemicStatus.VIOLATED,
            negative=True, source="HOSTILE",
        )
        pn = CapabilityContract(
            "NEG", "opaque", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
            ("TEST",), "UNKNOWN", {}, qualification=QualificationState.CANDIDATE,
        )
        cn = CapabilityCandidate("NEG", pn, (neg,), nomination_basis="FLATTERING")
        ms.nominate_capability_candidate(cn)
        tn = ExternalCapabilityQualifier(ms.evidence).qualify(cn)
        assert tn.state == QualificationState.REJECTED
    finally:
        td.cleanup()


def test_operational_scope_is_not_semantic_context_authority():
    td, ms = make_ms()
    try:
        c = qualified("LOCAL", handler=lambda x: x + 1, scope="regime-opaque-7")
        ms.register_capability(c)
        wrong = ms.capabilities.invoke(
            "LOCAL", QueryObligation("Q", "opaque", operational_scope_id="regime-opaque-9"), x=1
        )
        right = ms.capabilities.invoke(
            "LOCAL", QueryObligation("Q", "opaque", operational_scope_id="regime-opaque-7"), x=1
        )
        assert wrong["status"] == "UNKNOWN_INCOMPLETE"
        assert wrong["reason"] == "OPERATIONAL_SCOPE_MISMATCH"
        assert right["value"] == 2
        assert ms.development.records["LOCAL"].notes[0].startswith("OPERATIONAL_SCOPE:")
    finally:
        td.cleanup()
