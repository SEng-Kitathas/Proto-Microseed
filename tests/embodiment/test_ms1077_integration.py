from __future__ import annotations
from pathlib import Path
import tempfile
import pytest
from microseed import (Microseed, Authority, QualificationState, CapabilityContract, OperationalCounterpartyContract, CapabilityCandidate, ExternalCapabilityQualifier, EpistemicStatus)

def make_ms():
    td=tempfile.TemporaryDirectory(prefix="microseed-ms1077-"); return td,Microseed(Path(td.name))

def cp_contract(cid="CP0"):
    c=OperationalCounterpartyContract(counterparty_id=cid,purpose="opaque-independent-causal-relation",signature_sha256="",authority=Authority.DERIVED_READ_ONLY,lineage=("MS1053-1077",),currentness="CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("HSP_EXTERNAL_COUNTERPARTY_QUALIFICATION",),invariants=("NO_SEMANTIC_IDENTITY_AUTHORITY",))
    c.signature_sha256=c.computed_signature_sha256(); return c

def test_counterparty_contract_has_hard_identity_authority_ceiling():
    td,ms=make_ms()
    try:
        c=cp_contract(); ms.register_operational_counterparty(c)
        assert c.semantic_identity_authority=="NONE" and c.numerical_identity_authority=="NONE"
        assert c.genealogy_authority=="NONE" and c.value_state_authority=="NONE"
        bad=cp_contract("CPBAD"); bad.semantic_identity_authority="SEMANTIC_PERSON"; bad.signature_sha256=bad.computed_signature_sha256()
        with pytest.raises(ValueError,match="FORBIDDEN_AUTHORITY"):
            ms.register_operational_counterparty(bad)
    finally: td.cleanup()

def test_distributed_capability_stales_transitively_when_counterparty_changes():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp_contract())
        a=CapabilityContract("JOINT","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED)
        b=CapabilityContract("HIGHER","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CURRENT",{},dependencies=("JOINT",),qualification=QualificationState.SHADOW_QUALIFIED)
        ms.register_capability(a,counterparty_dependencies=(("CP0",0),)); ms.register_capability(b)
        stale=ms.change_operational_counterparty("CP0",reason="PARTNER_DRIFT")
        assert {"JOINT","HIGHER"}<=stale
        assert ms.compose(["HIGHER"]).status=="NO_PATH"
    finally: td.cleanup()

def test_pending_candidate_rejected_when_counterparty_epoch_drifts_after_external_qualification():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp_contract())
        ev=ms.append_evidence("P","proposal observed",EpistemicStatus.PRESSURE_SUPPORTED)
        qev=ms.append_evidence("Q","heldout supported",EpistemicStatus.PROVED)
        c=CapabilityContract("JC","opaque",{}, {},(),(),Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CANDIDATE",{},qualification=QualificationState.CANDIDATE)
        cand=CapabilityCandidate("JC",c,(ev,),nomination_basis="CONTROL",operational_signature={"counterparty_epochs":[["CP0",0]]})
        ms.nominate_capability_candidate(cand)
        ticket=ExternalCapabilityQualifier(ms.evidence).qualify(cand,qualification_evidence=(qev,))
        ms.change_operational_counterparty("CP0",reason="DRIFT_AFTER_TICKET")
        with pytest.raises(ValueError,match="CANDIDATE_COUNTERPARTY_EPOCH_DRIFT"):
            ms.admit_capability_candidate(ticket)
    finally: td.cleanup()

def test_counterparty_handle_does_not_create_identity_api():
    td,ms=make_ms()
    try:
        ms.register_operational_counterparty(cp_contract())
        assert not hasattr(ms,"claim_other_identity") and not hasattr(ms,"infer_person_identity")
        s=ms.status(); assert s["counterparty_semantic_identity_authority"]=="NONE"
        assert s["counterparty_numerical_identity_authority"]=="NONE"
    finally: td.cleanup()

def test_ms1077_frontier_and_ms1078_hard_stop():
    td,ms=make_ms()
    try:
        s=ms.status(); assert s["research_terminal_ms"]>=1152; assert s["integration_evidence_through_ms"]>=1152
        assert s["next_ms"]>=1203; assert s["next_ms"] >= 1278
        assert s["frontier"].startswith("ATTN-MS")
        assert s["language"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    finally: td.cleanup()
