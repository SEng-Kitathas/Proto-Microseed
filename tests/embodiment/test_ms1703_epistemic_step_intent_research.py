from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import tempfile

from microseed import (
    Authority, CapabilityContract, EpistemicStatus, FeasibilityState, Microseed,
    Observation, OperationalFrameContract, QualificationState, QueryObligation,
)
from microseed.development.epistemic_action import derive_epistemic_program_step_local_precheck
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


def local(m,trial,f=None):
    return derive_epistemic_program_step_local_precheck(
        trial=trial, deficit=m.epistemic_deficits.records.get(trial.deficit_id),
        feasibility=f or feasible(), capabilities=m.capabilities, obligation=obligation(),
        current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
    )


def nominate(m,trial,f=None):
    return m.nominate_epistemic_program_step_intent(trial,f or feasible(),obligation())


def test_ms1703_local_precheck_represents_next_primitive_without_macro_or_authority():
    td,m,calls,trial=fixture()
    try:
        c=local(m,trial)
        assert c.licenses_yes(),c.serializable()
        assert c.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_ALL_LICENSED'
        assert c.qualifier('decision_premises')=='LOCAL_PRECHECK_ONLY__NOT_EXECUTABLE'
        assert 'A_then_B' not in m.capabilities.contracts and calls==[]
    finally: td.cleanup()


def test_ms1708_boundary_public_adapter_requires_decision_context_before_intent():
    td,m,calls,trial=fixture()
    try:
        before=len(m.action_closure.intents)
        r=nominate(m,trial)
        assert r['status']=='ABSTAIN' and r['reason']=='EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        assert r['local_precheck']['commitment']=='YES'
        assert len(m.action_closure.intents)==before and calls==[]
    finally: td.cleanup()


def test_refused_feasibility_is_owned_by_local_precheck_before_decision_context():
    td,m,calls,trial=fixture()
    try:
        c=local(m,trial,feasible(FeasibilityState.REFUSED))
        assert c.licenses_no() and c.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_REFUSED'
        r=nominate(m,trial,feasible(FeasibilityState.REFUSED))
        assert r['status']=='ABSTAIN' and r['local_precheck']['commitment']=='NO' and calls==[]
    finally: td.cleanup()


def test_unknown_feasibility_is_owned_by_local_precheck_before_decision_context():
    td,m,calls,trial=fixture()
    try:
        c=local(m,trial,feasible(FeasibilityState.UNKNOWN))
        assert c.commitment.value=='UNKNOWN'
        r=nominate(m,trial,feasible(FeasibilityState.UNKNOWN))
        assert r['status']=='ABSTAIN' and r['local_precheck']['commitment']=='UNKNOWN' and calls==[]
    finally: td.cleanup()


def test_trial_content_drift_breaks_local_route_precheck():
    td,m,calls,trial=fixture()
    try:
        changed=replace(trial,start_state_evidence_id='DIFFERENT')
        c=local(m,changed)
        assert not c.licenses_yes()
        assert calls==[]
    finally: td.cleanup()


def test_deficit_staleness_breaks_local_need_precheck():
    td,m,calls,trial=fixture()
    try:
        m.epistemic_deficits.mark_stale('D',reason='QUESTION_PREMISE_DRIFT')
        c=local(m,trial)
        assert not c.licenses_yes()
        assert 'NOT_ACTION_LIMITED' in c.reason or c.commitment.value=='UNKNOWN'
        assert calls==[]
    finally: td.cleanup()


def test_control_state_drift_breaks_local_route_precheck():
    td,m,calls,trial=fixture()
    try:
        m.observe_opaque_control_state(Observation('CSX','EXT','opaque-control','sx',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CSX')
        c=local(m,trial)
        assert not c.licenses_yes()
        assert calls==[]
    finally: td.cleanup()


def test_component_drift_breaks_local_route_precheck():
    td,m,calls,trial=fixture()
    try:
        m.invalidate_capability('A',reason='DRIFT')
        c=local(m,trial)
        assert not c.licenses_yes()
        assert calls==[]
    finally: td.cleanup()


def test_public_adapter_abstention_creates_no_execution_or_handler_effect():
    td,m,calls,trial=fixture()
    try:
        r=nominate(m,trial)
        assert r['status']=='ABSTAIN'
        assert not m.action_closure.intents and not m.action_closure.executions and calls==[]
    finally: td.cleanup()


def test_local_precheck_has_zero_truth_and_execution_authority_surface():
    td,m,calls,trial=fixture()
    try:
        c=local(m,trial)
        q=dict(c.qualifiers)
        assert q['execution_authority']==q['truth_authority']=='NONE'
        assert q['decision_premises']=='LOCAL_PRECHECK_ONLY__NOT_EXECUTABLE'
        assert calls==[]
    finally: td.cleanup()
