from __future__ import annotations
from pathlib import Path
import tempfile

from microseed import (
    Authority, CapabilityContract, EpisodeSchemaContract, EpistemicStatus, Microseed, Observation,
    OperationalFrameContract, QualificationState, QueryObligation, ValueVariableContract,
)
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import begin_epistemic_program_trial
from microseed.development.relational_algebra import OpaqueTransitionSample, discover_opaque_action_composition_candidates
from microseed.development.rehearsal import RehearsalTransitionRelation


def candidate():
    rows=(
        OpaqueTransitionSample('a0','oa0','s0','A','m0','F',0),OpaqueTransitionSample('b0','ob0','m0','B','e0','F',0),OpaqueTransitionSample('c0','oc0','s0','C','e0','F',0),
        OpaqueTransitionSample('a1','oa1','s1','A','m1','F',0),OpaqueTransitionSample('b1','ob1','m1','B','e1','F',0),OpaqueTransitionSample('c1','oc1','s1','C','e1','F',0),
    )
    return [x for x in discover_opaque_action_composition_candidates(rows,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')][0]

def rel(state,cap,next_state,effect): return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))
def act_ob(): return QueryObligation('Q','epistemic-probe',required_authority=Authority.EFFECT,operational_scope_id='S')
def fob(cap): return QueryObligation('QF-'+cap,'feas:'+cap,required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')

def fixture():
    td=tempfile.TemporaryDirectory();m=Microseed(Path(td.name));calls=[];world={'A':'FEASIBLE','B':'FEASIBLE'}
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('T',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('T',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_value_state('V',-1.0)
    m.register_episode_schema(EpisodeSchemaContract('EP','opaque-episode','e'*64,Authority.DERIVED_READ_ONLY,('T',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    for cid in ('A','B'):
        m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('T',),'CURRENT',{},query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid) or {'receipt':_cid},operational_scope_id='S'))
        m.register_capability(CapabilityContract('FEAS-'+cid,'feas',{'target_capability_id':cid},{},(),(),Authority.DERIVED_READ_ONLY,('T',),'CURRENT',{},dependencies=(cid,),query_obligation_id='QF-'+cid,qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:{'feasibility':world[_cid],'reason':'FRESH_WORLD'},operational_scope_id='S'))
    m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
    m.append_evidence('E-U',{'unknown':'which relational alternative controls regulatory consequence?'},EpistemicStatus.UNKNOWN_INCOMPLETE)
    m.record_action_limited_unknown(deficit_id='D',question_key='QX',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),))
    trial=begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256='d'*64,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id='E-CS')
    h1=(rel('s0','A','s1',2.0),rel('s0','B','bx',0.0),rel('s1','B','s2',0.0));h2=(rel('s0','A','s1',0.0),rel('s0','B','bx',2.0),rel('s1','B','s3',0.0))
    dc=EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
    return td,m,calls,world,trial,dc

def nominate(m,t,dc): return m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob())
def ctx(t,dc): return EpistemicStepExecutionContext(t,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc)

def test_decision_bearing_current_safe_unknown_nominates_only_next_primitive():
    td,m,calls,w,t,dc=fixture()
    try:
        n=nominate(m,t,dc);assert n['status']=='ACTION_INTENT_NOMINATED';assert n['intent']['capability_id']=='A';assert n['priority']['commitment']=='YES';assert calls==[]
    finally:td.cleanup()

def test_endogenous_priority_plus_fresh_feasibility_executes_through_ordinary_effect_only():
    td,m,calls,w,t,dc=fixture()
    try:
        n=nominate(m,t,dc);r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc));assert r['status']=='ACTION_EXECUTED' and calls==['A']
    finally:td.cleanup()

def test_regulatory_pressure_disappears_between_nomination_and_effect_blocks():
    td,m,calls,w,t,dc=fixture()
    try:
        n=nominate(m,t,dc);m.observe_value_state('V',5.0);r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc));assert r['status']=='NO_EXECUTION' and calls==[]
    finally:td.cleanup()

def test_alternative_action_becomes_unavailable_so_decision_bearing_disappears_before_effect():
    td,m,calls,w,t,dc=fixture()
    try:
        n=nominate(m,t,dc);w['B']='REFUSED';r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc));assert r['status']=='NO_EXECUTION' and calls==[]
    finally:td.cleanup()

def test_relational_episode_epoch_drift_blocks_priority_before_effect():
    td,m,calls,w,t,dc=fixture()
    try:
        n=nominate(m,t,dc);m.change_episode_schema('EP',reason='RELATION_FRAME_CHANGED');r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t,dc));assert r['status']=='NO_EXECUTION' and calls==[]
    finally:td.cleanup()

def test_same_action_under_all_alternatives_never_initiates():
    td,m,calls,w,t,dc=fixture()
    try:
        same=EpistemicDecisionBearingContext((dc.relation_sets[0],dc.relation_sets[0]),dc.feasibility_routes);n=nominate(m,t,same);assert n['status']=='ABSTAIN' and n['priority']['commitment']=='NO' and calls==[]
    finally:td.cleanup()

def test_zero_pressure_never_initiates():
    td,m,calls,w,t,dc=fixture()
    try:
        m.observe_value_state('V',5.0);n=nominate(m,t,dc);assert n['status']=='ABSTAIN' and n['priority']['commitment']=='NO' and calls==[]
    finally:td.cleanup()

def test_decision_context_has_no_authority_surface():
    td,m,calls,w,t,dc=fixture()
    try:
        assert dc.authority==dc.execution_authority==dc.truth_authority=='NONE'
        try: EpistemicDecisionBearingContext(dc.relation_sets,dc.feasibility_routes,authority='EFFECT');raise AssertionError('should reject')
        except ValueError as e: assert 'AUTHORITY_ESCALATION' in str(e)
    finally:td.cleanup()
