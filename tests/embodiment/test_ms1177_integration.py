from pathlib import Path
import hashlib
import tempfile

import pytest

from microseed import (
    Microseed, CapabilityContract, OperationalFrameContract,
    Authority, QualificationState, EpistemicStatus, EpistemicCurrentnessAnchor,
)
from microseed.development.epistemic import EpistemicDeficitState


def new():
    td=tempfile.TemporaryDirectory(prefix="microseed-ms1177-")
    return td,Microseed(Path(td.name))


def frame(frame_id="F0"):
    return OperationalFrameContract(
        frame_id=frame_id,
        purpose="opaque-question-premise",
        signature_sha256=hashlib.sha256(frame_id.encode()).hexdigest(),
        authority=Authority.DERIVED_READ_ONLY,
        lineage=("MS1153-1177",),
        currentness="CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("EXTERNAL_FRAME_QUALIFICATION",),
    )


def unknown(m, evidence_id="u"):
    return m.append_evidence(
        evidence_id,{"opaque":True},EpistemicStatus.UNKNOWN_INCOMPLETE,source="TEST"
    )


def deficit(m, did, *, q="Q", hyp="a", frame_id=None, evidence_id=None):
    eid=evidence_id or f"u-{did}"
    if m.evidence.get(eid) is None:
        unknown(m,eid)
    anchors=()
    if frame_id is not None:
        anchors=(EpistemicCurrentnessAnchor("FRAME",frame_id,m.frames.epochs[frame_id]),)
    return m.record_action_limited_unknown(
        deficit_id=did,question_key=q,hypothesis_digest_sha256=hyp*64,
        unknown_evidence_id=eid,missing_discriminator_signature_sha256="b"*64,
        premise_anchors=anchors,
    )


def test_premise_drift_selectively_stales_current_pressure_but_preserves_history():
    td,m=new()
    try:
        m.register_operational_frame(frame("F0")); m.register_operational_frame(frame("F1"))
        deficit(m,"D0",frame_id="F0"); deficit(m,"D1",frame_id="F1")
        assert m.epistemic_development_pressure_ids()==("D0","D1")
        m.change_operational_frame("F0",reason="TEST_PREMISE_DRIFT")
        d0=m.epistemic_deficit_status("D0"); d1=m.epistemic_deficit_status("D1")
        assert d0["state"]=="STALE" and d0["unknown_evidence_id"]=="u-D0"
        assert d1["state"]=="ACTION_LIMITED"
        assert m.epistemic_development_pressure_ids()==("D1",)
    finally: td.cleanup()


def test_probe_loss_reopens_same_current_question_while_premise_drift_stales_it():
    td,m=new()
    try:
        m.register_operational_frame(frame("F0")); deficit(m,"D",frame_id="F0")
        probe=CapabilityContract(
            "probe","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1128-1152",),
            "CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1,
        )
        m.register_capability(probe); m.bind_probe_capability("D","probe")
        assert m.epistemic_deficit_status("D")["state"]=="PROBE_AVAILABLE"
        m.change_capability_dependency("probe",reason="TEST_ACCESS_LOSS")
        assert m.epistemic_deficit_status("D")["state"]=="ACTION_LIMITED"
        assert "D" in m.epistemic_development_pressure_ids()
        m.change_operational_frame("F0",reason="TEST_QUESTION_PREMISE_DRIFT")
        assert m.epistemic_deficit_status("D")["state"]=="STALE"
        assert "D" not in m.epistemic_development_pressure_ids()
    finally: td.cleanup()


def test_transitively_staled_capability_premise_stales_deficit_even_without_epoch_increment():
    td,m=new()
    try:
        parent=CapabilityContract(
            "parent","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1153-1177",),
            "CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1,
        )
        child=CapabilityContract(
            "child","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1153-1177",),
            "CURRENT",{},dependencies=("parent",),qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1,
        )
        m.register_capability(parent); m.register_capability(child)
        unknown(m,"u-cap")
        m.record_action_limited_unknown(
            deficit_id="D-cap",question_key="Q-cap",hypothesis_digest_sha256="e"*64,
            unknown_evidence_id="u-cap",missing_discriminator_signature_sha256="f"*64,
            premise_anchors=(EpistemicCurrentnessAnchor("CAPABILITY_PREMISE","child",0),),
        )
        assert m.capabilities.epochs["child"]==0
        m.change_capability_dependency("parent",reason="TRANSITIVE_PREMISE_DRIFT")
        assert m.capabilities.epochs["child"]==0
        assert m.epistemic_deficit_status("D-cap")["state"]=="STALE"
    finally: td.cleanup()


def test_explicit_content_bound_relevant_evidence_requests_revisit_without_answer_authority():
    td,m=new()
    try:
        deficit(m,"D")
        e=m.append_evidence("new-e",{"delta":1},EpistemicStatus.PRESSURE_SUPPORTED,source="TEST")
        basis=hashlib.sha256(b"external relevance relation").hexdigest()
        st=m.request_epistemic_revisit("D",e.evidence_id,relevance_basis_sha256=basis)
        assert st["state"]=="REVISIT_REQUIRED"
        assert st["truth_authority"]=="NONE" and st["semantic_question_authority"]=="NONE"
        assert st["relevant_evidence_ids"]==("new-e",)
        st2=m.request_epistemic_revisit("D",e.evidence_id,relevance_basis_sha256=basis)
        assert st2["relevant_evidence_ids"]==("new-e",)
        assert m.epistemic_revisit_required_ids()==("D",)
        assert "RESOLVED" not in {x.value for x in EpistemicDeficitState}
    finally: td.cleanup()


def test_stale_deficit_rejects_new_probe_and_revisit_and_never_reenters_pressure():
    td,m=new()
    try:
        deficit(m,"D"); m.stale_epistemic_deficit("D",reason="HYPOTHESIS_REVISION")
        probe=CapabilityContract(
            "probe","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1128-1152",),
            "CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:1,
        )
        m.register_capability(probe)
        with pytest.raises(ValueError,match="STALE_EPISTEMIC_DEFICIT"):
            m.bind_probe_capability("D","probe")
        e=m.append_evidence("e",{"delta":1},EpistemicStatus.PRESSURE_SUPPORTED,source="TEST")
        with pytest.raises(ValueError,match="STALE_EPISTEMIC_DEFICIT"):
            m.request_epistemic_revisit("D",e.evidence_id,relevance_basis_sha256="c"*64)
        assert m.epistemic_development_pressure_ids()==()
        assert m.epistemic_revisit_required_ids()==()
    finally: td.cleanup()


def test_hypothesis_revision_creates_new_content_bound_deficit_instead_of_rewriting_old_unknown():
    td,m=new()
    try:
        old=deficit(m,"D-old",q="Q0",hyp="a")
        m.stale_epistemic_deficit("D-old",reason="BOUNDED_HYPOTHESIS_SET_CHANGED")
        newr=deficit(m,"D-new",q="Q0",hyp="c")
        assert old.hypothesis_digest_sha256=="a"*64
        assert m.epistemic_deficit_status("D-old")["hypothesis_digest_sha256"]=="a"*64
        assert newr.hypothesis_digest_sha256=="c"*64
        assert m.epistemic_deficit_status("D-old")["unknown_evidence_id"]=="u-D-old"
        assert m.epistemic_development_pressure_ids()==("D-new",)
    finally: td.cleanup()


def test_restart_replay_preserves_stale_and_revisit_states_without_requeueing_stale_unknown():
    td=tempfile.TemporaryDirectory(prefix="microseed-ms1177-restart-")
    try:
        root=Path(td.name); m=Microseed(root)
        deficit(m,"D-stale"); deficit(m,"D-revisit")
        m.stale_epistemic_deficit("D-stale",reason="HYPOTHESIS_REVISION")
        e=m.append_evidence("relevant",{"delta":1},EpistemicStatus.PRESSURE_SUPPORTED,source="TEST")
        m.request_epistemic_revisit("D-revisit",e.evidence_id,relevance_basis_sha256="d"*64)
        del m
        m2=Microseed(root)
        assert m2.epistemic_deficit_status("D-stale")["state"]=="STALE"
        assert m2.epistemic_deficit_status("D-revisit")["state"]=="REVISIT_REQUIRED"
        assert m2.epistemic_development_pressure_ids()==()
        assert m2.epistemic_revisit_required_ids()==("D-revisit",)
        assert m2.status()["identity_claim"]=="NOT_QUALIFIED"
    finally: td.cleanup()


def test_ms1177_ceiling_remains_in_ancestry_after_later_bounded_relevance_integration():
    td,m=new()
    try:
        s=m.status()
        assert s["embodiment"].startswith("PROTO_MICROSEED_MAINDEV_INTEGRATION_V")
        assert s["research_terminal_ms"]>=1177 and s["integration_evidence_through_ms"]>=1177
        assert s["next_ms"]>=1203 and s['next_ms'] >= 1278
        assert s["frontier"].startswith("ATTN-MS")
        assert s["epistemic_relevance_classifier"].startswith("BOUNDED_OPERATIONAL_BEARING_VERIFIER")
        assert s["epistemic_projection_discovery"].startswith("BOUNDED_ACTION_CONDITIONED_PREDICTIVE_EQUIVALENCE")
        assert not hasattr(m, "qualify_epistemic_projection_candidate")
        assert s["question_revisit_scheduler"].startswith("NOT_INTEGRATED")
        assert not hasattr(m,"discover_epistemic_projection")
        assert not hasattr(m,"schedule_question_revisits")
        assert s["language"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally: td.cleanup()
