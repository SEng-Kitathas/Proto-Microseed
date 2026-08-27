from __future__ import annotations
from pathlib import Path
import tempfile
import pytest

from microseed import (
    Microseed, Authority, QualificationState, CapabilityContract,
    RecruitmentTopologyContract, OperationalCounterpartyContract,
    OperationalCoordinationContract, OperationalTrace,
    ExternalCapabilityQualifier, EpistemicStatus,
)


def make_ms():
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1502-")
    return td, Microseed(Path(td.name))


def cap(cid: str):
    return CapabilityContract(
        cid, "opaque-effect", {}, {}, (), (), Authority.DERIVED_READ_ONLY,
        ("MS1478-1502-TEST",), "CURRENT", {},
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def counterparty(cid: str):
    c = OperationalCounterpartyContract(
        counterparty_id=cid, purpose="opaque-independent-causal-relation",
        signature_sha256="", authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS1053-1077",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def coordination(rid="R"):
    c = OperationalCoordinationContract(
        coordination_id=rid, purpose="opaque-mutual-action-contingency",
        participant_counterparty_epochs=(("CPA", 0), ("CPB", 0)),
        signature_sha256="", authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS1078-1102",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("HSP_EXTERNAL_COORDINATION_QUALIFICATION",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def topology(ms: Microseed, tid="T"):
    t = RecruitmentTopologyContract(
        topology_id=tid, purpose="opaque-operational-recruitment-topology",
        relations=(("A", "B"),),
        capability_epochs=(("A", ms.capabilities.epochs["A"]), ("B", ms.capabilities.epochs["B"])),
        signature_sha256="", authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS978-1027",), currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("HSP_EXTERNAL_TOPOLOGY_QUALIFICATION",),
        invariants=("NO_SEMANTIC_ROLE_AUTHORITY",),
    )
    t.signature_sha256 = t.computed_signature_sha256()
    return t


def seeded():
    td, ms = make_ms()
    ms.register_capability(cap("A")); ms.register_capability(cap("B"))
    ms.register_operational_counterparty(counterparty("CPA"))
    ms.register_operational_counterparty(counterparty("CPB"))
    ms.register_operational_coordination(coordination())
    ms.register_recruitment_topology(topology(ms))
    return td, ms


def seed_discovery_traces(ms: Microseed):
    for i in range(5):
        ms.record_operational_trace(OperationalTrace(f"a{i}", ("A",), ((1.0, 0.0),), "baseline"))
        ms.record_operational_trace(OperationalTrace(f"b{i}", ("B",), ((0.0, 1.0),), "baseline"))
    for scope in ("s0", "s1"):
        for i in range(8):
            ms.record_operational_trace(OperationalTrace(
                f"ab-{scope}-{i}", ("A", "B"), ((1.0, 0.0), (0.0, 2.0)), scope,
                topology_ids=("T",), coordination_ids=("R",),
            ))


def discovered(ms: Microseed):
    props = ms.discover_capability_candidates()
    assert props
    cid = props[0]["candidate_id"]
    return ms.capability_candidates[cid]


def test_operational_trace_captures_existing_relation_epochs_and_coordination_counterparties():
    td, ms = seeded()
    try:
        t = ms.record_operational_trace(OperationalTrace(
            "joint", ("A", "B"), ((1.0,), (2.0,)), "s",
            topology_ids=("T",), coordination_ids=("R",),
        ))
        assert t.topology_epochs == (("T", 0),)
        assert t.coordination_epochs == (("R", 0),)
        assert t.counterparty_ids == ("CPA", "CPB")
        assert t.counterparty_epochs == (("CPA", 0), ("CPB", 0))
    finally: td.cleanup()


def test_discovered_composite_preserves_topology_counterparty_coordination_ancestry():
    td, ms = seeded()
    try:
        seed_discovery_traces(ms); c = discovered(ms); sig = c.operational_signature
        assert sig["topology_epochs"] == [["T", 0]]
        assert sig["counterparty_epochs"] == [["CPA", 0], ["CPB", 0]]
        assert sig["coordination_epochs"] == [["R", 0]]
        assert "MS1478-1502-COMPOSITION-ANCESTRY-PRESERVATION" in c.proposed_contract.lineage
        assert "COORDINATION_EPOCH_BOUND" in c.proposed_contract.invariants
        assert c.proposed_contract.qualification == QualificationState.CANDIDATE
    finally: td.cleanup()


def test_coordination_drift_after_external_ticket_blocks_pending_discovered_composite():
    td, ms = seeded()
    try:
        seed_discovery_traces(ms); c = discovered(ms)
        qe = ms.append_evidence("Q-MS1502", {"heldout": "joint"}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS1502").qualify(c, qualification_evidence=(qe,))
        ms.change_operational_coordination("R", reason="JOINT_CONVENTION_DRIFT")
        with pytest.raises(ValueError, match="CANDIDATE_COORDINATION_EPOCH_DRIFT:R"):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()


def test_topology_drift_after_external_ticket_blocks_pending_discovered_composite():
    td, ms = seeded()
    try:
        seed_discovery_traces(ms); c = discovered(ms)
        qe = ms.append_evidence("Q-T-MS1502", {"heldout": "topology"}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS1502").qualify(c, qualification_evidence=(qe,))
        ms.change_recruitment_topology("T", reason="JOINT_TOPOLOGY_DRIFT")
        with pytest.raises(ValueError, match="CANDIDATE_TOPOLOGY_EPOCH_DRIFT:T"):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()


def test_admitted_discovered_composite_stales_when_bound_coordination_drifts():
    td, ms = seeded()
    try:
        seed_discovery_traces(ms); c = discovered(ms)
        qe = ms.append_evidence("Q-ADMIT-MS1502", {"heldout": "clean"}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS1502").qualify(c, qualification_evidence=(qe,))
        admitted = ms.admit_capability_candidate(ticket)
        assert admitted.qualification in {QualificationState.QUALIFIED, QualificationState.SHADOW_QUALIFIED}
        stale = ms.change_operational_coordination("R", reason="POST_ADMISSION_DRIFT")
        assert admitted.capability_id in stale
        assert ms.capabilities.contracts[admitted.capability_id].qualification == QualificationState.STALE
        assert ms.capabilities.contracts["A"].qualification == QualificationState.SHADOW_QUALIFIED
        assert ms.capabilities.contracts["B"].qualification == QualificationState.SHADOW_QUALIFIED
    finally: td.cleanup()


def test_counterparty_drift_selectively_reaches_discovered_composite_via_existing_coordination_lineage():
    td, ms = seeded()
    try:
        seed_discovery_traces(ms); c = discovered(ms)
        qe = ms.append_evidence("Q-CP-MS1502", {"heldout": "clean"}, EpistemicStatus.PROVED, source="HSP_EXTERNAL")
        ticket = ExternalCapabilityQualifier(ms.evidence, qualifier_id="HSP-MS1502").qualify(c, qualification_evidence=(qe,))
        admitted = ms.admit_capability_candidate(ticket)
        stale = ms.change_operational_counterparty("CPA", reason="CHILD_PHENOTYPE_DRIFT")
        assert admitted.capability_id in stale
        assert not ms.coordinations.is_current("R")
    finally: td.cleanup()


def test_stale_or_unknown_joint_relation_cannot_be_smuggled_into_trace():
    td, ms = seeded()
    try:
        with pytest.raises(ValueError, match="unknown/stale operational coordination:NOPE"):
            ms.record_operational_trace(OperationalTrace("bad0", ("A",), ((1.0,),), coordination_ids=("NOPE",)))
        ms.change_operational_coordination("R", reason="STALE")
        with pytest.raises(ValueError, match="unknown/stale operational coordination:R"):
            ms.record_operational_trace(OperationalTrace("bad1", ("A",), ((1.0,),), coordination_ids=("R",)))
    finally: td.cleanup()


def test_no_new_multi_child_planner_registry_or_semantic_child_authority_api():
    td, ms = seeded()
    try:
        for name in (
            "multi_child_planner", "multi_child_registry", "semantic_child_registry",
            "discover_child_roles", "auto_qualify_composition", "infer_transaction_semantics",
        ):
            assert not hasattr(ms, name)
    finally: td.cleanup()


def test_ms1502_release_boundary_is_superseded_without_rolling_back_its_authority_ceilings():
    td, ms = make_ms()
    try:
        s = ms.status()
        assert s["research_terminal_ms"] == 1527
        assert s["integration_evidence_through_ms"] == 1527
        assert s["next_ms"] == 1528 and s["next_started"] is False
        assert s["ms1478_started"] is True and s["ms1503_started"] is True and s["ms1528_started"] is False
        assert s["frontier"] == "ATTN-MS1527-POST-REENTRY-WHOLE-ORGANISM-HOSTILE-EMBODIMENT"
        assert s["multi_child_planner_authority"] == "NONE"
        assert s["composition_self_qualification_authority"] == "NONE"
        assert s["reentry_manager_authority"] == "NONE"
        assert s["reentry_self_qualification_authority"] == "NONE"
    finally: td.cleanup()
