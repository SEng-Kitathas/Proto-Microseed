from __future__ import annotations

from pathlib import Path
import hashlib
import tempfile
import pytest

from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, CapabilityContract,
    OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract, RecruitmentTopologyContract,
    OperationalCounterpartyContract, OperationalCoordinationContract,
    RecruitmentOption, RehearsalTransitionObservation, CounterfactualRehearsalConfig,
    CapabilityCandidate, ExternalCapabilityQualifier, EpistemicStatus,
)


def make_ms():
    td=tempfile.TemporaryDirectory(prefix="microseed-ms1352-"); return td,Microseed(Path(td.name))

def cap(cid):
    return CapabilityContract(cid,"opaque",{},{},(),(),Authority.DERIVED_READ_ONLY,("MS1328-1352",),"CURRENT",{},qualification=QualificationState.SHADOW_QUALIFIED)

def setup_world(ms: Microseed):
    fr=OperationalFrameContract("F","opaque-frame","f"*64,Authority.DERIVED_READ_ONLY,("MS878-902",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED)
    ms.register_operational_frame(fr)
    v=ValueVariableContract("V","opaque-regulatory",2.0,3.0,"v"*64,Authority.DERIVED_READ_ONLY,("MS953-977",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE","SUPPLIED_VIABILITY_INTERVAL"))
    ms.register_value_variable(v); ms.observe_value_state("V",0.0)
    cp=OperationalCounterpartyContract("CP","opaque-counterparty","",Authority.DERIVED_READ_ONLY,("MS1053-1077",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED)
    cp.signature_sha256=cp.computed_signature_sha256(); ms.register_operational_counterparty(cp)
    co=OperationalCoordinationContract("R","opaque-coordination",(("CP",0),),"",Authority.DERIVED_READ_ONLY,("MS1078-1102",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED)
    co.signature_sha256=co.computed_signature_sha256(); ms.register_operational_coordination(co)
    ms.register_capability(cap("A")); ms.register_capability(cap("B")); ms.register_capability(cap("C"),coordination_dependencies=(("R",0),))
    topo=RecruitmentTopologyContract("T","opaque-topology",(("A","B"),("B","C")),(("A",0),("B",0),("C",0)),"",Authority.DERIVED_READ_ONLY,("MS1003-1027",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED)
    topo.signature_sha256=topo.computed_signature_sha256(); ms.register_recruitment_topology(topo)
    ep=EpisodeSchemaContract("E","opaque-episode","e"*64,Authority.DERIVED_READ_ONLY,("MS1103-1127",),"CURRENT",qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(("F",0),),value_epochs=(("V",0),),coordination_epochs=(("R",0),))
    ms.register_episode_schema(ep)

def rows():
    out=[]; k=0
    for s,a,nxt,eff,coord in (("S0","A","SA",.8,None),("S0","B","S1",-.4,None),("S1","C","S2",2.6,"R"),("S1","A","SA",.8,None)):
        for _ in range(12):
            k+=1
            out.append(RehearsalTransitionObservation(f"EV{k}",s,a,nxt,eff,0,"F",0,"E",0,"T",0,coord,0 if coord else None))
    return tuple(out)

def opts(c_feas=FeasibilityState.FEASIBLE):
    return (RecruitmentOption("A",FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption("B",FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption("C",c_feas,local_cost=.1))

def test_bounded_rehearsal_beats_myopic_without_authority_gain():
    td,ms=make_ms()
    try:
        setup_world(ms)
        p1=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V",config=CounterfactualRehearsalConfig(max_horizon=1))
        p2=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V",config=CounterfactualRehearsalConfig(max_horizon=2))
        assert p1.sequence == ("A",) and p1.residual_pressure == pytest.approx(1.2)
        assert p2.sequence == ("B","C") and p2.residual_pressure == 0.0
        assert p2.authority == Authority.MODEL_OUTPUT_ONLY.value
        assert p2.truth_authority == p2.execution_authority == p2.qualification_authority == "NONE"
        assert p2.semantic_goal_authority == "NONE"
    finally: td.cleanup()

def test_refusal_and_unknown_are_not_overridden_by_rehearsal():
    for f in (FeasibilityState.REFUSED,FeasibilityState.UNKNOWN):
        td,ms=make_ms()
        try:
            setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(f),start_state_id="S0",value_id="V")
            assert p.sequence == ("A",)
        finally: td.cleanup()

def test_ambiguous_transition_is_not_forced_into_a_prediction():
    td,ms=make_ms()
    try:
        setup_world(ms); rr=list(rows())
        cidx=[i for i,r in enumerate(rr) if r.capability_id=="C"]
        for i in cidx[len(cidx)//2:]:
            old=rr[i]; rr[i]=RehearsalTransitionObservation(old.evidence_id,old.state_id,old.capability_id,"SX",-.2,old.capability_epoch,old.frame_id,old.frame_epoch,old.episode_schema_id,old.episode_schema_epoch,old.topology_id,old.topology_epoch,old.coordination_id,old.coordination_epoch)
        p=ms.nominate_counterfactual_rehearsal(rr,opts(),start_state_id="S0",value_id="V")
        assert p.sequence == ("A",) and p.residual_pressure > 0
    finally: td.cleanup()

def test_value_currentness_is_required_for_rehearsal():
    td,ms=make_ms()
    try:
        setup_world(ms); ms.change_value_variable("V",reason="DRIFT")
        assert ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V") is None
    finally: td.cleanup()

def test_frame_episode_topology_and_coordination_currentness_filter_stale_evidence():
    for kind in ("frame","episode","topology","coordination"):
        td,ms=make_ms()
        try:
            setup_world(ms)
            if kind=="frame": ms.change_operational_frame("F",reason="DRIFT")
            elif kind=="episode": ms.change_episode_schema("E",reason="DRIFT")
            elif kind=="topology": ms.change_recruitment_topology("T",reason="DRIFT")
            else: ms.change_operational_coordination("R",reason="DRIFT")
            p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V")
            assert p is None or p.sequence != ("B","C")
        finally: td.cleanup()

def test_capability_epoch_drift_filters_old_transition_evidence():
    td,ms=make_ms()
    try:
        setup_world(ms); ms.change_capability_dependency("B",reason="DRIFT")
        p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V")
        assert p is None or p.sequence != ("B","C")
    finally: td.cleanup()

def test_proposal_currentness_rechecks_all_bound_ancestry():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V")
        assert ms.counterfactual_rehearsal_status(p.proposal_id)["status"]=="CURRENT_REHEARSAL_PROPOSAL"
        ms.change_episode_schema("E",reason="DRIFT")
        st=ms.counterfactual_rehearsal_status(p.proposal_id); assert st["status"]=="UNKNOWN_INCOMPLETE" and "EPISODE" in st["reason"]
    finally: td.cleanup()

def test_restart_preserves_history_but_does_not_create_execute_or_qualify_api():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V"); pid=p.proposal_id
        ms2=Microseed(Path(td.name))
        assert pid in ms2.counterfactual_rehearsals.proposals
        assert not hasattr(ms2,"execute_counterfactual_rehearsal")
        assert not hasattr(ms2,"qualify_counterfactual_rehearsal")
    finally: td.cleanup()

def test_registry_rejects_forged_authority():
    from microseed.development.rehearsal import CounterfactualRehearsalProposal, CounterfactualRehearsalRegistry
    p=CounterfactualRehearsalProposal("P","S",("A",),"X",1,1,0,(),(),(("A",0),),(("F",0),),(("E",0),),("V",0),authority=Authority.EFFECT.value)
    with pytest.raises(ValueError,match="REHEARSAL_AUTHORITY_ESCALATION"):
        CounterfactualRehearsalRegistry().add(p)

def test_budget_exhaustion_abstains_instead_of_returning_partial_plan():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V",config=CounterfactualRehearsalConfig(max_nodes=1))
        assert p is None
    finally: td.cleanup()

def test_status_keeps_general_planner_unqualified():
    td,ms=make_ms()
    try:
        s=ms.status(); assert s["language"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        assert not hasattr(ms,"plan") and not hasattr(ms,"generate_goal")
    finally: td.cleanup()


def test_external_qualification_of_rehearsed_whole_enlarges_second_order_capability_closure():
    td,ms=make_ms()
    try:
        setup_world(ms)
        ms.register_capability(cap("E2"))
        # Higher-order consumer exists but is unreachable until BC is actually admitted.
        x=CapabilityContract("X","opaque-higher-whole",{},{},(),(),Authority.DERIVED_READ_ONLY,("MS1328-1352",),"CURRENT",{},dependencies=("BC","E2"),qualification=QualificationState.SHADOW_QUALIFIED)
        ms.register_capability(x)
        assert ms.compose(["X"]).status == "NO_PATH"
        rehearsal=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id="S0",value_id="V")
        assert rehearsal.sequence == ("B","C")
        # Rehearsal is only nomination ancestry; independent evidence qualifies the whole.
        pe=ms.append_evidence("MS1352-REHEARSAL-NOMINATION",{"proposal_id":rehearsal.proposal_id},EpistemicStatus.UNKNOWN_INCOMPLETE)
        qc=CapabilityContract("BC","opaque-rehearsed-whole",{},{},(),(),Authority.DERIVED_READ_ONLY,("MS1328-1352",),"CANDIDATE",{},dependencies=("B","C"),qualification=QualificationState.CANDIDATE)
        cand=CapabilityCandidate("BC",qc,(pe,),assistance_ancestry=rehearsal.assistance_ancestry,nomination_basis="COUNTERFACTUAL_REHEARSAL_PROPOSAL",source_trace_ids=rehearsal.source_evidence_ids)
        ms.nominate_capability_candidate(cand)
        he=ms.append_evidence("HSP-MS1352-HOLDOUT",{"heldout_success":.975},EpistemicStatus.PROVED,source="HSP_EXTERNAL")
        ticket=ExternalCapabilityQualifier(ms.evidence,qualifier_id="HSP-MS1352").qualify(cand,qualification_evidence=(he,))
        ms.admit_capability_candidate(ticket)
        r=ms.compose(["X"])
        assert r.status == "COMPOSED_EPHEMERAL" and "BC" in r.plan and "X" in r.plan
        assert rehearsal.qualification_authority == "NONE"
    finally: td.cleanup()
