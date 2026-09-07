from __future__ import annotations

from dataclasses import replace

from microseed import EpistemicStatus
from microseed.development.action_closure import OpaqueControlStateWitness
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import act_ob
from scratch.ms2014_endogenous_referent_opportunity_enumeration import _base_fixture
from tests.embodiment.test_lang_active_acquisition_revalidation_opportunity_surface import (
    _close, _register, _targets,
)


def _prepare():
    td,m,*_=_base_fixture()
    op,target,_shared=_targets(m)
    rec=_register(m,target,replay=True)
    selected=next(
        x for x in m._current_owned_referent_epistemic_opportunities(act_ob())
        if str(x['content_signature_sha256'])==str(op['content_signature_sha256'])
    )
    before=(m.evidence.count(),len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions))
    nominated=m.nominate_current_native_referent_association_revalidation_opportunity(rec.record_id,act_ob())
    after=(m.evidence.count(),len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions))
    assert nominated['status']=='ASSOCIATION_REVALIDATION_OPPORTUNITY_PERSISTED_AND_NOMINATED',nominated
    assert nominated['selected_probe_action_id']=='P2'
    assert nominated['deficit_delta']==1 and nominated['intent_delta']==1 and nominated['execution_delta']==0,nominated
    assert after[0]-before[0]==1 and after[1]-before[1]==1 and after[2]-before[2]==1 and after[3]==before[3]
    assert nominated['execution_authority']==nominated['effect_authority']=='NONE'
    unknown=m.evidence.get(nominated['unknown_evidence_id'])
    assert unknown is not None and unknown['disposition']=='UNKNOWN_INCOMPLETE',unknown
    assert unknown['payload']['kind']=='NATIVE_REFERENT_ASSOCIATION_REVALIDATION_ACQUISITION_UNKNOWN'
    assert unknown['payload']['association_record_id']==rec.record_id
    assert unknown['payload']['association_selection_authority']=='CONTENT_UNIQUENESS_ONLY'
    assert unknown['payload']['remaining_token_presentation']=='EXOGENOUS'
    return td,m,op,target,rec,selected,nominated


def _ctx(selected):
    return EpistemicStepExecutionContext(
        selected['trial'],decision_context=selected['decision_context'],
    )


def _execute(m,selected,nominated,obligation=None):
    return m.execute_bounded_action(
        nominated['nomination']['intent']['intent_id'],
        act_ob() if obligation is None else obligation,
        epistemic_step_context=_ctx(selected),
    )


def _confirm_association_currentness(m,rec,target):
    evidence_id='ACTIVE-ACQ-ASSOC-CURRENTNESS-CONFIRM'
    m.append_evidence(
        evidence_id,
        {
            'kind':'OPAQUE_ASSOCIATION_CURRENTNESS_OBSERVATION',
            'record_id':rec.record_id,
            'left_opaque_id':rec.left_opaque_id,
            'observed_right_digest_sha256':target,
        },
        EpistemicStatus.NARROWED,
        source='ACTIVE_ACQUISITION_CURRENTNESS_TEST',
    )
    return m.assess_opaque_evidence_association_currentness(
        rec.record_id,witness_evidence_id=evidence_id,
    )


def test_nomination_materializes_pressure_and_intent_but_never_executes():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        assert nominated['nomination']['status']=='ACTION_INTENT_NOMINATED'
        intent=nominated['nomination']['intent']
        assert intent['capability_id']=='P2'
        assert intent['execution_authority']=='NONE'
        assert len(m.action_closure.executions)==2  # fixture history only
        deficit=m.epistemic_deficits.records[nominated['selected_deficit_id']]
        ancestry=set(deficit.assistance_ancestry)
        assert 'ENDOGENOUS_UNKNOWN_MATERIALIZED_AFTER_NATIVE_ASSOCIATION_REVALIDATION_SELECTION' in ancestry
        assert f'ASSOCIATION_REVALIDATION_RECORD:{rec.record_id}' in ancestry
    finally:_close(m,td)


def test_explicit_effect_call_executes_only_after_fresh_association_and_ordinary_effect_reauthorization():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated)
        assert out['status']=='ACTION_EXECUTED',out
        assert len(m.action_closure.executions)==before+1
        assert out['handler_value']=={'receipt':'P2'}
        packet=out['execution']
        premises=set(packet['execution_premise_ids'])
        assert nominated['unknown_evidence_id'] in premises
        assert rec.record_id in premises
        assert op['content_signature_sha256'] in premises
        assert target in premises
        assert packet['authority']=='EFFECT'
        assert packet['truth_authority']=='NONE'
        assert packet['observation_authority']=='NONE'
    finally:_close(m,td)


def test_association_becoming_current_after_nomination_removes_pressure_and_blocks_effect():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        assessed=_confirm_association_currentness(m,rec,target)
        assert assessed['status']=='CURRENTNESS_CONFIRMED',assessed
        assert m.opaque_evidence_association_status(rec.record_id)['status']=='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION'
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated)
        assert out['status']=='NO_EXECUTION',out
        assert out['reason']=='CURRENT_ASSOCIATION_REVALIDATION_OPPORTUNITY_REQUIRED_AT_EXECUTION',out
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_probe_capability_drift_is_blocked_by_ordinary_effect_gate_before_execution():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        m.change_capability_dependency('P2',reason='ACTIVE_ACQ_EFFECT_TIME_P2_DRIFT')
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated)
        assert out['status']=='NO_EXECUTION' and out['reason']=='EFFECT_CAPABILITY_NOT_CURRENT',out
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_control_state_drift_blocks_before_epistemic_need_can_become_effect_authority():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        intent=m.action_closure.intents[nominated['nomination']['intent']['intent_id']]
        m.action_closure.set_state(OpaqueControlStateWitness('DRIFTED-CONTROL-STATE',intent.control_state_evidence_id))
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated)
        assert out['status']=='NO_EXECUTION' and out['reason']=='CONTROL_STATE_DRIFT',out
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_obligation_drift_blocks_before_effect_even_when_information_need_remains():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        wrong=replace(act_ob(),obligation_id='ACTIVE-ACQ-WRONG-OBLIGATION')
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated,wrong)
        assert out['status']=='NO_EXECUTION' and out['reason']=='ACTION_OBLIGATION_DRIFT',out
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_forged_selected_unknown_pointer_cannot_bypass_association_execution_ancestry():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        deficit_id=nominated['selected_deficit_id']
        original=m.epistemic_deficits.records[deficit_id]
        unknown=m.evidence.get(nominated['unknown_evidence_id'])
        raw_id=str(unknown['payload']['source_raw_observation_evidence_id'])
        m.epistemic_deficits.records[deficit_id]=replace(original,unknown_evidence_id=raw_id)
        before=len(m.action_closure.executions)
        out=_execute(m,selected,nominated)
        assert out['status']=='NO_EXECUTION',out
        assert out['reason'] in {
            'EPISTEMIC_PROGRAM_STEP_PREMISE_DRIFT',
            'ASSOCIATION_REVALIDATION_SELECTION_NOMINATION_ANCESTRY_REQUIRED_AT_EXECUTION',
        },out
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_second_nomination_is_idempotent_and_adds_no_more_pressure_or_intents():
    td,m,op,target,rec,selected,nominated=_prepare()
    try:
        before=(m.evidence.count(),len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions))
        second=m.nominate_current_native_referent_association_revalidation_opportunity(rec.record_id,act_ob())
        after=(m.evidence.count(),len(m.epistemic_deficits.records),len(m.action_closure.intents),len(m.action_closure.executions))
        assert second['status']=='ABSTAIN',second
        assert second['reason']=='ASSOCIATION_REVALIDATION_EPISTEMIC_DEFICIT_ALREADY_PERSISTED',second
        assert before==after
        assert second['deficit_delta']==second['intent_delta']==second['execution_delta']==0
    finally:_close(m,td)
