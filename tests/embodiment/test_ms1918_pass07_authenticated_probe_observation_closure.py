from __future__ import annotations

from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus, _close


def _install_observation(m, payload: dict[str, object], *, bind_frame: bool = True):
    m.register_capability(CapabilityContract(
        'OBS-1918','direct-probe-observation',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1918',),'CURRENT',{},
        query_obligation_id='OBS-1918-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:dict(payload),operational_scope_id='S'))
    m.register_capability(CapabilityContract(
        'BASIS-1918','direct-probe-observation-use',{}, {},('NO_TRUTH_AUTHORITY',),(),Authority.DERIVED_READ_ONLY,('MS1918',),'CURRENT',{},
        dependencies=('OBS-1918',),query_obligation_id='BASIS-1918-Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S'))
    if bind_frame:
        m.frames.bind_capability('F','OBS-1918')


def _execute_probe(m):
    surface=m.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
    assert surface['status']=='CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE',surface
    prior=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())['trial']
    dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
    nominated=m.nominate_grounded_epistemic_program_step_intent(prior,'FEAS-B',fob('B'),act_ob(),decision_context=dc)
    assert nominated['status']=='ACTION_INTENT_NOMINATED',nominated
    executed=m.execute_bounded_action(
        nominated['intent']['intent_id'],act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(
            prior,feasibility_capability_id='FEAS-B',feasibility_obligation=fob('B'),decision_context=dc))
    assert executed['status']=='ACTION_EXECUTED',executed
    return prior,dc,nominated,executed


def _assured_observe(m, execution_id: str, *, evidence_id='E-MS1918', capture_id='C-MS1918'):
    return m.record_bounded_action_outcome_via_observation_basis(
        execution_id,
        observation_capability_id='OBS-1918',
        observation_obligation=QueryObligation('OBS-1918-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
        basis_capability_id='BASIS-1918',
        basis_obligation=QueryObligation('BASIS-1918-Q','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
        evidence_id=evidence_id,capture_id=capture_id)


def _advance(m, prior, nominated, executed):
    eid=executed['execution']['execution_id']
    intent=m.action_closure.intents[nominated['intent']['intent_id']]
    execution=m.action_closure.executions[eid]
    outcome=next(o for o in m.action_closure.outcomes.values() if o.execution_id==eid)
    advanced=advance_epistemic_program_trial(
        prior,intent=intent,execution=execution,outcome=outcome,
        capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
    assert advanced.status=='COMPLETE',advanced
    return advanced


def _raw_forged_observe(m, execution_id: str, *, state='raw-forged-surprise', evidence_id='E-RAW-1918'):
    forged=Observation(
        'C-RAW-1918','CAPABILITY:FAKE-OBS',f'action-execution:{execution_id}',{'next_state_id':state},
        currentness_basis='QUALIFIED_OBSERVATION_CAPABILITY_AND_BOUNDED_USE_BASIS',
        authority=Authority.OBSERVATION_ONLY,
        lineage=('OBSERVATION_CAPABILITY:FAKE@0','OBSERVATION_USE_BASIS:FAKE@0'))
    return m.record_bounded_action_outcome(
        execution_id,forged,evidence_id=evidence_id,evidence_premise_epochs=(('FAKE',0),))


def test_ranger1_assured_unexpected_observation_closes_trial_and_program_evidence_without_truth_authority():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        _install_observation(m,{'next_state_id':'observed-surprise'},bind_frame=True)
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        out=_assured_observe(m,eid)
        assert out['status']=='ACTION_OUTCOME_OBSERVED',out
        assert out['outcome']['actual_next_state_id']=='observed-surprise'
        assert out['outcome']['prediction_commitment']['commitment']=='UNKNOWN'
        assert out['outcome']['prediction_commitment']['reason']=='EPISTEMIC_STEP_HAS_NO_STEP_LOCAL_PREDICTION_CLAIM'
        receipt=out['observation_admission_receipt']
        assert receipt['truth_authority']==receipt['execution_authority']=='NONE'
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE',admitted
        assert admitted['sample'].start_token=='s1' and admitted['sample'].action_token=='B'
        assert admitted['sample'].end_token=='observed-surprise'
        advanced=_advance(m,prior,n,e)
        assert advanced.step_records[0].actual_next_state_id=='observed-surprise'
        assert advanced.step_records[0].prediction_commitment=='UNKNOWN'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1918-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_RECORDED',result
        assert result['state']=='REVISIT_REQUIRED'
        assert result['truth_authority']==result['answer_authority']==result['execution_authority']=='NONE'
    finally:_close(m,td)


def test_ranger2_raw_forged_observation_cannot_make_probe_program_evidence_admissible():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        raw=_raw_forged_observe(m,eid)
        assert raw['status']=='ACTION_OUTCOME_OBSERVED'
        assert m.derive_admitted_opaque_transition_sample(eid)['reason']=='AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED'
        advanced=_advance(m,prior,n,e)
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-RAW-COMPLETE-1918')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED',result
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
        assert m.epistemic_deficits.records['D-1904'].state.value=='PROBE_AVAILABLE'
    finally:_close(m,td)


def test_ranger3_raw_forged_surprise_cannot_request_revisit_through_step_bearing_route():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        raw=_raw_forged_observe(m,eid,state='outside-both-branches',evidence_id='E-RAW-BEAR-1918')
        assert raw['status']=='ACTION_OUTCOME_OBSERVED'
        advanced=_advance(m,prior,n,e)
        result=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert result['status']=='PROGRAM_STEP_BEARING_UNRESOLVED',result
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
        assert m.epistemic_deficits.records['D-1904'].state.value=='PROBE_AVAILABLE'
    finally:_close(m,td)


def test_ranger4_assured_observation_without_unique_common_frame_records_outcome_but_not_program_evidence():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        _install_observation(m,{'next_state_id':'seen-no-frame'},bind_frame=False)
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        out=_assured_observe(m,eid,evidence_id='E-MS1918-NOFRAME',capture_id='C-MS1918-NOFRAME')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ABSTAIN'
        assert admitted['reason']=='UNIQUE_COMMON_OPERATIONAL_FRAME_REQUIRED'
        advanced=_advance(m,prior,n,e)
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1918-NOFRAME-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED'
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
    finally:_close(m,td)


def test_ranger5_observation_channel_stale_after_outcome_blocks_later_probe_program_evidence():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        _install_observation(m,{'next_state_id':'observed-then-stale'},bind_frame=True)
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        out=_assured_observe(m,eid,evidence_id='E-MS1918-STALE',capture_id='C-MS1918-STALE')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        advanced=_advance(m,prior,n,e)
        m.invalidate_capability('OBS-1918',reason='MS1918_POST_OUTCOME_OBSERVATION_DRIFT')
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ABSTAIN'
        assert admitted['reason']=='LIVE_OBSERVATION_ADMISSION_NOT_CURRENT'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1918-STALE-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED'
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
    finally:_close(m,td)


def test_ranger6_assured_outcome_content_remains_observation_sovereign_even_when_not_predicted():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        _install_observation(m,{'next_state_id':'neither-s2-nor-sx'},bind_frame=True)
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        out=_assured_observe(m,eid,evidence_id='E-MS1918-SOV',capture_id='C-MS1918-SOV')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        assert out['outcome']['actual_next_state_id']=='neither-s2-nor-sx'
        assert m.action_closure.current_state.state_id=='neither-s2-nor-sx'
        ev=m.evidence.get('E-MS1918-SOV')
        assert ev['payload']['next_state_id']=='neither-s2-nor-sx'
        assert ev['payload']['truth_authority']=='NONE'
        assert out['outcome']['prediction_commitment']['commitment']=='UNKNOWN'
    finally:_close(m,td)


def test_ranger7_observation_use_basis_stale_after_outcome_blocks_probe_program_evidence():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        _install_observation(m,{'next_state_id':'observed-basis-then-stale'},bind_frame=True)
        prior,dc,n,e=_execute_probe(m); eid=e['execution']['execution_id']
        out=_assured_observe(m,eid,evidence_id='E-MS1918-BASIS-STALE',capture_id='C-MS1918-BASIS-STALE')
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        advanced=_advance(m,prior,n,e)
        stale=m.invalidate_capability('BASIS-1918',reason='MS1918_POST_OUTCOME_BASIS_DRIFT')
        assert 'BASIS-1918' in stale
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ABSTAIN'
        assert admitted['reason']=='LIVE_OBSERVATION_ADMISSION_NOT_CURRENT'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1918-BASIS-STALE-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED'
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
        assert m.epistemic_deficits.records['D-1904'].state.value=='PROBE_AVAILABLE'
    finally:_close(m,td)
