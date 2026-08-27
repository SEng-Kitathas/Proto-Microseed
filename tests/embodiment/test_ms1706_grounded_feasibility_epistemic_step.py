from __future__ import annotations
from pathlib import Path
import tempfile

from microseed import Authority, CapabilityContract, EpistemicStatus, Microseed, Observation, OperationalFrameContract, QualificationState, QueryObligation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import begin_epistemic_program_trial
from microseed.development.relational_algebra import OpaqueTransitionSample, discover_opaque_action_composition_candidates


def candidate():
    rows=(
        OpaqueTransitionSample('a0','oa0','s0','A','m0','F',0), OpaqueTransitionSample('b0','ob0','m0','B','e0','F',0), OpaqueTransitionSample('c0','oc0','s0','C','e0','F',0),
        OpaqueTransitionSample('a1','oa1','s1','A','m1','F',0), OpaqueTransitionSample('b1','ob1','m1','B','e1','F',0), OpaqueTransitionSample('c1','oc1','s1','C','e1','F',0),
    )
    return [x for x in discover_opaque_action_composition_candidates(rows,min_positive_support=2) if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')][0]


def act_ob(): return QueryObligation('Q','epistemic-probe',required_authority=Authority.EFFECT,operational_scope_id='S')
def feas_ob(): return QueryObligation('Q-FEAS','feasibility:A',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def fixture(*, feasibility_authority=Authority.DERIVED_READ_ONLY, target='A', depend=True):
    td=tempfile.TemporaryDirectory();m=Microseed(Path(td.name));calls=[];world={'state':'FEASIBLE'}
    for cid in ('A','B'):
        m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1706',),'CURRENT',{},dependencies=(),query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid) or {'receipt':_cid},operational_scope_id='S'))
    deps=('A',) if depend else ()
    m.register_capability(CapabilityContract('FEAS-A','bounded-execution-time-feasibility',{'target_capability_id':target},{'output':'FeasibilityState'},(),(),feasibility_authority,('MS1706',),'CURRENT',{},dependencies=deps,query_obligation_id='Q-FEAS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: {'feasibility':world['state'],'reason':'FRESH_TEST_WORLD'},operational_scope_id='S'))
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS1706',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
    m.append_evidence('E-U',{'q':'x'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1706')
    m.record_action_limited_unknown(deficit_id='D',question_key='Q-REL',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64)
    trial=begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256='d'*64,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id='E-CS')
    return td,m,calls,world,trial


def nominate(m,trial): return m.nominate_grounded_epistemic_program_step_intent(trial,'FEAS-A',feas_ob(),act_ob())
def ctx(trial): return EpistemicStepExecutionContext(trial,feasibility_capability_id='FEAS-A',feasibility_obligation=feas_ob())

def test_fresh_grounded_feasible_nominates_and_executes_only_through_effect_boundary():
    td,m,calls,w,t=fixture()
    try:
        n=nominate(m,t);assert n['status']=='ACTION_INTENT_NOMINATED';assert n['intent']['capability_id']=='A';assert n['feasibility_basis']['feasibility']=='FEASIBLE';assert calls==[]
        r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t));assert r['status']=='ACTION_EXECUTED' and calls==['A']
    finally:td.cleanup()

def test_fresh_refusal_at_nomination_abstains():
    td,m,calls,w,t=fixture();w['state']='REFUSED'
    try:
        n=nominate(m,t);assert n['status']=='ABSTAIN' and n['feasibility_basis']['feasibility']=='REFUSED' and calls==[]
    finally:td.cleanup()

def test_fresh_unknown_at_nomination_abstains():
    td,m,calls,w,t=fixture();w['state']='UNKNOWN'
    try:
        n=nominate(m,t);assert n['status']=='ABSTAIN' and n['feasibility_basis']['feasibility']=='UNKNOWN' and calls==[]
    finally:td.cleanup()

def test_feasible_at_nomination_refused_before_effect_blocks_execution():
    td,m,calls,w,t=fixture()
    try:
        n=nominate(m,t);w['state']='REFUSED';r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t));assert r['status']=='NO_EXECUTION' and calls==[]
    finally:td.cleanup()

def test_feasibility_capability_invalidation_after_nomination_blocks_execution():
    td,m,calls,w,t=fixture()
    try:
        n=nominate(m,t);m.invalidate_capability('FEAS-A',reason='FEASIBILITY_BASIS_LOST');r=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(t));assert r['status']=='NO_EXECUTION' and calls==[]
    finally:td.cleanup()

def test_wrong_target_feasibility_capability_never_nominates():
    td,m,calls,w,t=fixture(target='B')
    try:
        n=nominate(m,t);assert n['status']=='ABSTAIN' and n['feasibility_basis']['reason']=='FEASIBILITY_CAPABILITY_TARGET_MISMATCH' and calls==[]
    finally:td.cleanup()

def test_feasibility_capability_must_depend_on_target_effect_capability():
    td,m,calls,w,t=fixture(depend=False)
    try:
        n=nominate(m,t);assert n['status']=='ABSTAIN' and n['feasibility_basis']['reason']=='FEASIBILITY_CAPABILITY_TARGET_DEPENDENCY_MISSING' and calls==[]
    finally:td.cleanup()

def test_feasibility_capability_cannot_carry_effect_authority():
    td,m,calls,w,t=fixture(feasibility_authority=Authority.EFFECT)
    try:
        n=nominate(m,t);assert n['status']=='ABSTAIN' and n['feasibility_basis']['reason']=='FEASIBILITY_CAPABILITY_REQUIRES_DERIVED_READ_ONLY' and calls==[]
    finally:td.cleanup()
