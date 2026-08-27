from pathlib import Path
import tempfile
import pytest
from microseed import (
    Microseed, Authority, QualificationState, FeasibilityState, CapabilityContract,
    OperationalFrameContract, EpisodeSchemaContract, ValueVariableContract, RecruitmentTopologyContract,
    OperationalCounterpartyContract, OperationalCoordinationContract, RecruitmentOption,
    RehearsalTransitionObservation, CounterfactualRehearsalConfig, QueryObligation, Observation,
    TernaryCommitment,
)

def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1402-'); return td,Microseed(Path(td.name))

def cap(cid, *, effect=False, handler=None):
    return CapabilityContract(cid,'opaque',{},{},(),(),Authority.EFFECT if effect else Authority.DERIVED_READ_ONLY,('MS1378-1402',),'CURRENT',{},
        query_obligation_id='ACT' if effect else None, qualification=QualificationState.SHADOW_QUALIFIED,handler=handler,
        operational_scope_id='SCOPE' if effect else None)

def setup_world(ms):
    fr=OperationalFrameContract('F','opaque-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED)
    ms.register_operational_frame(fr)
    v=ValueVariableContract('V','opaque-regulatory',2.0,3.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE','SUPPLIED_VIABILITY_INTERVAL'))
    ms.register_value_variable(v); ms.observe_value_state('V',0.0)
    cp=OperationalCounterpartyContract('CP','opaque-counterparty','',Authority.DERIVED_READ_ONLY,('MS1053-1077',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED); cp.signature_sha256=cp.computed_signature_sha256(); ms.register_operational_counterparty(cp)
    co=OperationalCoordinationContract('R','opaque-coordination',(('CP',0),),'',Authority.DERIVED_READ_ONLY,('MS1078-1102',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED); co.signature_sha256=co.computed_signature_sha256(); ms.register_operational_coordination(co)
    ms.register_capability(cap('A',effect=True,handler=lambda **_: {'receipt':'A'}))
    ms.register_capability(cap('B',effect=True,handler=lambda **_: {'receipt':'B'}))
    ms.register_capability(cap('C',effect=True,handler=lambda **_: {'receipt':'C'}),coordination_dependencies=(('R',0),))
    ms.register_capability(cap('READ',effect=False,handler=lambda **_: {'receipt':'READ'}))
    topo=RecruitmentTopologyContract('T','opaque-topology',(('A','B'),('B','C')),(('A',0),('B',0),('C',0)),'',Authority.DERIVED_READ_ONLY,('MS1003-1027',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED); topo.signature_sha256=topo.computed_signature_sha256(); ms.register_recruitment_topology(topo)
    ep=EpisodeSchemaContract('E','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),),coordination_epochs=(('R',0),)); ms.register_episode_schema(ep)
    ms.observe_opaque_control_state(Observation('CS0','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS0')

def rows():
    out=[]; k=0
    for s,a,nxt,eff,coord in (('S0','A','SA',.8,None),('S0','B','S1',-.4,None),('S1','C','S2',2.6,'R'),('S1','A','SA',.8,None)):
        for _ in range(12):
            k+=1; out.append(RehearsalTransitionObservation(f'EV{k}',s,a,nxt,eff,0,'F',0,'E',0,'T',0,coord,0 if coord else None))
    return tuple(out)

def opts(): return (RecruitmentOption('A',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('B',FeasibilityState.FEASIBLE,local_cost=.1),RecruitmentOption('C',FeasibilityState.FEASIBLE,local_cost=.1))
def act_obligation(): return QueryObligation('ACT','opaque-action',required_authority=Authority.EFFECT,operational_scope_id='SCOPE')

def test_rehearsal_now_carries_stepwise_predictions_for_closed_loop_feedback():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
        assert p.sequence==('B','C') and p.predicted_state_path==('S0','S1','S2') and p.predicted_step_value_effects==pytest.approx((-.4,2.6))
    finally: td.cleanup()

def test_trch_yes_licenses_intent_but_not_execution_authority():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
        c=ms.derive_bounded_action_commitment(p.proposal_id); assert c.commitment==TernaryCommitment.YES and c.licenses_yes() and c.qualifier('execution_authority')=='NONE'
        r=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); assert r['status']=='ACTION_INTENT_NOMINATED' and r['execution_authority']=='NONE'
    finally: td.cleanup()

def test_effect_authority_and_action_obligation_are_separate_from_commitment():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
        bad=QueryObligation('ACT','bad',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='SCOPE')
        assert ms.nominate_bounded_action_intent(p.proposal_id,bad)['reason']=='ACTION_OBLIGATION_MUST_REQUIRE_EFFECT'
        ms.capabilities.contracts['B'].authority=Authority.DERIVED_READ_ONLY
        assert ms.nominate_bounded_action_intent(p.proposal_id,act_obligation())['reason']=='ACTION_REQUIRES_EFFECT_AUTHORITY'
    finally: td.cleanup()

def test_missing_or_wrong_current_state_produces_abstention_not_default_action():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V')
        ms.action_closure.current_state=None
        c=ms.derive_bounded_action_commitment(p.proposal_id); assert c.commitment==TernaryCommitment.UNKNOWN and c.binding==TernaryCommitment.UNKNOWN
        ms.action_closure.set_state(__import__('microseed').OpaqueControlStateWitness('OTHER','EO'))
        c=ms.derive_bounded_action_commitment(p.proposal_id); assert c.applicability==TernaryCommitment.NO and c.abstains()
    finally: td.cleanup()

def test_execution_does_not_fabricate_observation_or_update_state():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); iid=ir['intent']['intent_id']
        er=ms.execute_bounded_action(iid,act_obligation()); assert er['status']=='ACTION_EXECUTED' and er['observation_recorded'] is False
        assert ms.action_closure.current_state.state_id=='S0' and ms.values.latest['V'][1]==0.0 and len(ms.action_closure.outcomes)==0
    finally: td.cleanup()

def test_external_observed_outcome_closes_one_step_and_forces_redeliberation():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); er=ms.execute_bounded_action(ir['intent']['intent_id'],act_obligation()); eid=er['execution']['execution_id']
        obs=Observation('OUT1','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY)
        out=ms.record_bounded_action_outcome(eid,obs,evidence_id='E-OUT1')
        assert out['status']=='ACTION_OUTCOME_OBSERVED' and out['requires_redeliberation']
        assert out['outcome']['prediction_commitment']['commitment']=='YES'
        assert ms.action_closure.current_state.state_id=='S1' and ms.values.latest['V'][1]==pytest.approx(-.4)
        assert ms.derive_bounded_action_commitment(p.proposal_id).applicability==TernaryCommitment.NO
    finally: td.cleanup()

def test_redeliberation_from_actual_state_can_complete_viability_path():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); er=ms.execute_bounded_action(ir['intent']['intent_id'],act_obligation()); eid=er['execution']['execution_id']
        ms.record_bounded_action_outcome(eid,Observation('O1','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY),evidence_id='EO1')
        p2=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S1',value_id='V'); assert p2.sequence==('C',)
        ir2=ms.nominate_bounded_action_intent(p2.proposal_id,act_obligation()); er2=ms.execute_bounded_action(ir2['intent']['intent_id'],act_obligation()); e2=er2['execution']['execution_id']
        ms.record_bounded_action_outcome(e2,Observation('O2','EXT',f'action-execution:{e2}',{'next_state_id':'S2','value_id':'V','observed_value':2.2},authority=Authority.OBSERVATION_ONLY),evidence_id='EO2')
        assert ms.value_pressure('V')['pressure_magnitude']==0.0 and ms.action_closure.current_state.state_id=='S2'
    finally: td.cleanup()

def test_wrong_model_is_preserved_as_violation_and_cannot_open_loop_continue():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); er=ms.execute_bounded_action(ir['intent']['intent_id'],act_obligation()); eid=er['execution']['execution_id']
        out=ms.record_bounded_action_outcome(eid,Observation('OW','EXT',f'action-execution:{eid}',{'next_state_id':'BAD','value_id':'V','observed_value':-1.0},authority=Authority.OBSERVATION_ONLY),evidence_id='EW')
        assert out['outcome']['prediction_commitment']['commitment']=='NO' and ms.action_closure.current_state.state_id=='BAD'
        assert ms.derive_bounded_action_commitment(p.proposal_id).applicability==TernaryCommitment.NO
    finally: td.cleanup()

def test_outcome_requires_content_bound_observation_and_is_single_use():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); er=ms.execute_bounded_action(ir['intent']['intent_id'],act_obligation()); eid=er['execution']['execution_id']
        bad=Observation('BAD','EXT','wrong',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY)
        assert ms.record_bounded_action_outcome(eid,bad,evidence_id='EBAD')['status']=='OUTCOME_REJECTED'
        good=Observation('GOOD','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY)
        assert ms.record_bounded_action_outcome(eid,good,evidence_id='EGOOD')['status']=='ACTION_OUTCOME_OBSERVED'
        assert ms.record_bounded_action_outcome(eid,good,evidence_id='EGOOD2')['reason']=='EXECUTION_ALREADY_HAS_OUTCOME'
    finally: td.cleanup()

def test_restart_preserves_control_history_but_not_execution_access():
    td,ms=make_ms()
    try:
        setup_world(ms); p=ms.nominate_counterfactual_rehearsal(rows(),opts(),start_state_id='S0',value_id='V'); ir=ms.nominate_bounded_action_intent(p.proposal_id,act_obligation()); er=ms.execute_bounded_action(ir['intent']['intent_id'],act_obligation()); eid=er['execution']['execution_id']
        ms.record_bounded_action_outcome(eid,Observation('O','EXT',f'action-execution:{eid}',{'next_state_id':'S1','value_id':'V','observed_value':-.4},authority=Authority.OBSERVATION_ONLY),evidence_id='EOUT')
        ms2=Microseed(Path(td.name)); st=ms2.bounded_control_loop_status(); assert st['current_state']['state_id']=='S1' and st['outcome_count']==1
        assert ms2.derive_bounded_action_commitment(p.proposal_id).commitment==TernaryCommitment.UNKNOWN
    finally: td.cleanup()

def test_no_general_policy_or_semantic_intention_api_promoted():
    td,ms=make_ms()
    try:
        st=ms.bounded_control_loop_status(); assert st['general_policy_authority']=='NONE' and st['semantic_intention_authority']=='NONE'
        assert not hasattr(ms,'autonomous_policy') and not hasattr(ms,'execute_plan') and not hasattr(ms,'settle_intention')
    finally: td.cleanup()
