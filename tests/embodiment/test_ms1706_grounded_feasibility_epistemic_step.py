from __future__ import annotations
from pathlib import Path
import tempfile

from microseed import Authority, CapabilityContract, EpistemicStatus, Microseed, Observation, OperationalFrameContract, QualificationState, QueryObligation
from microseed.development.epistemic_action import derive_epistemic_program_step_local_precheck, derive_grounded_feasibility_option
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


def fixture(*, feasibility_authority=Authority.DERIVED_READ_ONLY, target='A', depend=True, feasibility_currentness='CURRENT'):
    td=tempfile.TemporaryDirectory();m=Microseed(Path(td.name));calls=[];world={'state':'FEASIBLE'}
    for cid in ('A','B'):
        m.register_capability(CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1706',),'CURRENT',{},dependencies=(),query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda _cid=cid,**_:calls.append(_cid) or {'receipt':_cid},operational_scope_id='S'))
    deps=('A',) if depend else ()
    m.register_capability(CapabilityContract('FEAS-A','bounded-execution-time-feasibility',{'target_capability_id':target},{'output':'FeasibilityState'},(),(),feasibility_authority,('MS1706',),feasibility_currentness,{},dependencies=deps,query_obligation_id='Q-FEAS',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: {'feasibility':world['state'],'reason':'FRESH_TEST_WORLD'},operational_scope_id='S'))
    m.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS1706',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_opaque_control_state(Observation('CS','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS')
    m.append_evidence('E-U',{'q':'x'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1706')
    m.record_action_limited_unknown(deficit_id='D',question_key='Q-REL',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64)
    trial=begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256='d'*64,capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id='E-CS')
    return td,m,calls,world,trial


def grounded(m,trial):
    option,basis=derive_grounded_feasibility_option(
        target_capability_id=trial.steps[len(trial.step_records)], feasibility_capability_id='FEAS-A',
        feasibility_obligation=feas_ob(), capabilities=m.capabilities,
    )
    return option,basis


def local(m,trial):
    option,basis=grounded(m,trial)
    c=derive_epistemic_program_step_local_precheck(
        trial=trial,deficit=m.epistemic_deficits.records.get(trial.deficit_id),feasibility=option,
        capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),
        current_state=m.action_closure.current_state,
    )
    return c,basis


def nominate(m,trial): return m.nominate_grounded_epistemic_program_step_intent(trial,'FEAS-A',feas_ob(),act_ob())


def test_fresh_grounded_feasible_earns_local_precheck_but_not_decision_authority():
    td,m,calls,w,t=fixture()
    try:
        c,b=local(m,t)
        assert c.licenses_yes() and b['feasibility']=='FEASIBLE'
        assert c.qualifier('decision_premises')=='LOCAL_PRECHECK_ONLY__NOT_EXECUTABLE'
        n=nominate(m,t)
        assert n['status']=='ABSTAIN' and n['reason']=='EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        assert calls==[] and not m.action_closure.intents
    finally:td.cleanup()


def test_fresh_refusal_is_owned_by_grounded_feasibility_before_decision_context():
    td,m,calls,w,t=fixture();w['state']='REFUSED'
    try:
        c,b=local(m,t); assert b['feasibility']=='REFUSED' and c.licenses_no()
        n=nominate(m,t); assert n['status']=='ABSTAIN' and n['feasibility_basis']['feasibility']=='REFUSED' and calls==[]
    finally:td.cleanup()


def test_fresh_unknown_is_owned_by_grounded_feasibility_before_decision_context():
    td,m,calls,w,t=fixture();w['state']='UNKNOWN'
    try:
        c,b=local(m,t); assert b['feasibility']=='UNKNOWN' and c.commitment.value=='UNKNOWN'
        n=nominate(m,t); assert n['status']=='ABSTAIN' and n['feasibility_basis']['feasibility']=='UNKNOWN' and calls==[]
    finally:td.cleanup()


def test_wrong_target_feasibility_capability_never_passes_grounded_owner():
    td,m,calls,w,t=fixture(target='B')
    try:
        option,basis=grounded(m,t)
        assert basis['reason']=='FEASIBILITY_CAPABILITY_TARGET_MISMATCH'
        assert option.feasibility.value=='UNKNOWN'
        n=nominate(m,t); assert n['status']=='ABSTAIN' and n['feasibility_basis']['reason']=='FEASIBILITY_CAPABILITY_TARGET_MISMATCH' and calls==[]
    finally:td.cleanup()


def test_feasibility_capability_must_depend_on_target_effect_capability():
    td,m,calls,w,t=fixture(depend=False)
    try:
        option,basis=grounded(m,t)
        assert basis['reason']=='FEASIBILITY_CAPABILITY_TARGET_DEPENDENCY_MISSING'
        assert option.feasibility.value=='UNKNOWN'
        assert nominate(m,t)['status']=='ABSTAIN' and calls==[]
    finally:td.cleanup()


def test_feasibility_capability_cannot_carry_effect_authority():
    td,m,calls,w,t=fixture(feasibility_authority=Authority.EFFECT)
    try:
        option,basis=grounded(m,t)
        assert basis['reason']=='FEASIBILITY_CAPABILITY_REQUIRES_DERIVED_READ_ONLY'
        assert option.feasibility.value=='UNKNOWN'
        assert nominate(m,t)['status']=='ABSTAIN' and calls==[]
    finally:td.cleanup()


def test_noncurrent_feasibility_capability_is_rejected_by_currentness_owner():
    td,m,calls,w,t=fixture()
    try:
        m.invalidate_capability('FEAS-A',reason='MS1914_FEASIBILITY_CURRENTNESS_HOSTILE')
        option,basis=grounded(m,t)
        assert basis['reason']=='FEASIBILITY_CAPABILITY_NOT_CURRENT'
        assert option.feasibility.value=='UNKNOWN'
        assert nominate(m,t)['status']=='ABSTAIN' and calls==[]
    finally:td.cleanup()


def test_qualified_but_noncurrent_feasibility_capability_hits_explicit_currentness_guard():
    td,m,calls,w,t=fixture(feasibility_currentness='STALE')
    try:
        assert m.capabilities.contracts['FEAS-A'].qualification==QualificationState.SHADOW_QUALIFIED
        assert m.capabilities.contracts['FEAS-A'].currentness=='STALE'
        option,basis=grounded(m,t)
        assert basis['reason']=='FEASIBILITY_CAPABILITY_NOT_CURRENT'
        assert option.feasibility.value=='UNKNOWN'
        assert nominate(m,t)['status']=='ABSTAIN' and calls==[]
    finally:td.cleanup()


def test_grounded_feasibility_local_precheck_never_fires_effect_handler():
    td,m,calls,w,t=fixture()
    try:
        c,b=local(m,t)
        assert c.licenses_yes() and b['feasibility']=='FEASIBLE'
        assert calls==[] and not m.action_closure.executions
    finally:td.cleanup()


def test_ms1708_boundary_keeps_feasible_route_distinct_from_lawful_initiation():
    td,m,calls,w,t=fixture()
    try:
        c,b=local(m,t); assert c.licenses_yes()
        n=nominate(m,t)
        assert n['status']=='ABSTAIN' and n['reason']=='EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        assert n['local_precheck']['commitment']=='YES' and calls==[]
    finally:td.cleanup()
