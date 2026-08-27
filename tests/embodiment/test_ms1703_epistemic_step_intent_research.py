from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import tempfile

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, FeasibilityState, Microseed,
    Observation, OperationalFrameContract, QualificationState, QueryObligation,
)
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import begin_epistemic_program_trial
from microseed.development.recruitment import RecruitmentOption
from microseed.development.relational_algebra import OpaqueTransitionSample, discover_opaque_action_composition_candidates


def cap(cid: str, calls: list[str]):
    return CapabilityContract(
        cid, 'opaque', {}, {}, (), (), Authority.EFFECT, ('MS1703',), 'CURRENT', {},
        query_obligation_id='Q', qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda _cid=cid, **_: calls.append(_cid) or {'receipt': _cid},
        operational_scope_id='S',
    )


def candidate():
    rows = (
        OpaqueTransitionSample('a0','oa0','s0','A','m0','F',0),
        OpaqueTransitionSample('b0','ob0','m0','B','e0','F',0),
        OpaqueTransitionSample('c0','oc0','s0','C','e0','F',0),
        OpaqueTransitionSample('a1','oa1','s1','A','m1','F',0),
        OpaqueTransitionSample('b1','ob1','m1','B','e1','F',0),
        OpaqueTransitionSample('c1','oc1','s1','C','e1','F',0),
    )
    return [x for x in discover_opaque_action_composition_candidates(rows,min_positive_support=2)
            if (x.direct_action_token,x.first_action_token,x.second_action_token)==('C','A','B')][0]


def obligation():
    return QueryObligation('Q','epistemic-probe',required_authority=Authority.EFFECT,operational_scope_id='S')


def fixture():
    td=tempfile.TemporaryDirectory(); m=Microseed(Path(td.name)); calls=[]
    m.register_operational_frame(OperationalFrameContract('F','opaque-frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1703',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_capability(cap('A',calls)); m.register_capability(cap('B',calls))
    m.observe_opaque_control_state(Observation('CS0','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS0')
    m.append_evidence('E-UNK',{'question':'which opaque relation?'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='MS1703')
    m.record_action_limited_unknown(deficit_id='D',question_key='Q-REL',hypothesis_digest_sha256='a'*64,
        unknown_evidence_id='E-UNK',missing_discriminator_signature_sha256='d'*64)
    trial=begin_epistemic_program_trial(candidate(),deficit_id='D',discrimination_signature_sha256='d'*64,
        capabilities=m.capabilities,obligation=obligation(),current_frame_epochs=dict(m.frames.epochs),
        start_state_id='s0',start_state_evidence_id='E-CS0')
    return td,m,calls,trial


def feasible(state=FeasibilityState.FEASIBLE):
    return RecruitmentOption('A',state,local_cost=0.1,model_evidence_ids=('ASSISTANCE:MS1703_TYPED_FEASIBILITY_INPUT',))


def nominate(m,trial,f=None):
    return m.nominate_epistemic_program_step_intent(trial,f or feasible(),obligation())


def test_no_native_macro_token_is_created_and_only_next_primitive_is_nominated():
    td,m,calls,trial=fixture()
    try:
        r=nominate(m,trial); assert r['status']=='ACTION_INTENT_NOMINATED'
        i=r['intent']; assert i['basis_kind']=='EPISTEMIC_PROGRAM_STEP' and i['capability_id']=='A'
        assert 'A_then_B' not in m.capabilities.contracts and calls==[]
        assert i['execution_authority']==i['truth_authority']==i['semantic_intention_authority']=='NONE'
    finally: td.cleanup()


def test_feasible_next_step_executes_through_ordinary_effect_boundary_with_fresh_context():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial); intent_id=n['intent']['intent_id']
        r=m.execute_bounded_action(intent_id,obligation(),epistemic_step_context=EpistemicStepExecutionContext(trial,feasible()))
        assert r['status']=='ACTION_EXECUTED' and calls==['A']
        assert r['execution']['authority']=='EFFECT'
    finally: td.cleanup()


def test_missing_execution_context_blocks_effect():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial); r=m.execute_bounded_action(n['intent']['intent_id'],obligation())
        assert r['status']=='NO_EXECUTION' and r['reason']=='EPISTEMIC_STEP_EXECUTION_CONTEXT_REQUIRED' and calls==[]
    finally: td.cleanup()


def test_refused_feasibility_abstains_before_intent():
    td,m,calls,trial=fixture()
    try:
        r=nominate(m,trial,feasible(FeasibilityState.REFUSED))
        assert r['status']=='ABSTAIN' and r['commitment']['commitment']=='NO' and calls==[]
    finally: td.cleanup()


def test_unknown_feasibility_abstains_before_intent():
    td,m,calls,trial=fixture()
    try:
        r=nominate(m,trial,feasible(FeasibilityState.UNKNOWN))
        assert r['status']=='ABSTAIN' and r['commitment']['commitment']=='UNKNOWN' and calls==[]
    finally: td.cleanup()


def test_feasibility_change_between_nomination_and_effect_blocks_execution():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial,feasible())
        ctx=EpistemicStepExecutionContext(trial,feasible(FeasibilityState.UNKNOWN))
        r=m.execute_bounded_action(n['intent']['intent_id'],obligation(),epistemic_step_context=ctx)
        assert r['status']=='NO_EXECUTION' and r['reason']=='EPISTEMIC_PROGRAM_STEP_PREMISE_DRIFT' and calls==[]
    finally: td.cleanup()


def test_trial_content_drift_between_nomination_and_effect_blocks_execution():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial)
        changed=replace(trial,start_state_evidence_id='DIFFERENT')
        r=m.execute_bounded_action(n['intent']['intent_id'],obligation(),epistemic_step_context=EpistemicStepExecutionContext(changed,feasible()))
        assert r['status']=='NO_EXECUTION' and r['reason']=='EPISTEMIC_PROGRAM_TRIAL_DRIFT' and calls==[]
    finally: td.cleanup()


def test_deficit_staleness_after_nomination_blocks_execution():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial); m.epistemic_deficits.mark_stale('D',reason='QUESTION_PREMISE_DRIFT')
        r=m.execute_bounded_action(n['intent']['intent_id'],obligation(),epistemic_step_context=EpistemicStepExecutionContext(trial,feasible()))
        assert r['status']=='NO_EXECUTION' and r['reason']=='EPISTEMIC_PROGRAM_STEP_PREMISE_DRIFT' and calls==[]
    finally: td.cleanup()


def test_control_state_drift_after_nomination_blocks_before_effect():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial)
        m.observe_opaque_control_state(Observation('CSX','EXT','opaque-control','sx',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CSX')
        r=m.execute_bounded_action(n['intent']['intent_id'],obligation(),epistemic_step_context=EpistemicStepExecutionContext(trial,feasible()))
        assert r['status']=='NO_EXECUTION' and r['reason']=='CONTROL_STATE_DRIFT' and calls==[]
    finally: td.cleanup()


def test_component_drift_after_nomination_blocks_before_effect():
    td,m,calls,trial=fixture()
    try:
        n=nominate(m,trial); m.invalidate_capability('A',reason='DRIFT')
        r=m.execute_bounded_action(n['intent']['intent_id'],obligation(),epistemic_step_context=EpistemicStepExecutionContext(trial,feasible()))
        assert r['status']=='NO_EXECUTION' and r['reason']=='EFFECT_CAPABILITY_NOT_CURRENT' and calls==[]
    finally: td.cleanup()
