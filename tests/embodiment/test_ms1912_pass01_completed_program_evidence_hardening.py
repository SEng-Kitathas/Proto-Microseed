from dataclasses import replace

from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound, _close


def _complete_current_direct_probe(m):
    formed = m.instantiate_current_revised_surface_direct_probe_trial(
        old_deficit_id='D', successor_deficit_id='D-1904', obligation=act_ob()
    )
    assert formed['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', formed
    trial = formed['trial']
    assert trial.steps == ('B',) and trial.status == 'OPEN'
    satisfaction = m.derive_current_program_discriminator_satisfaction(trial)
    assert satisfaction.licenses_yes(), satisfaction.serializable()

    feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
    nominated = m.nominate_epistemic_program_step_intent(trial, feasibility, act_ob())
    assert nominated['status'] == 'ACTION_INTENT_NOMINATED', nominated
    intent = m.action_closure.intents[nominated['intent']['intent_id']]

    context = EpistemicStepExecutionContext(trial, feasibility=feasibility)
    executed = m.execute_bounded_action(
        intent.intent_id, act_ob(), epistemic_step_context=context
    )
    assert executed['status'] == 'ACTION_EXECUTED', executed
    execution = m.action_closure.executions[executed['execution']['execution_id']]

    observed = Observation(
        'OUT-MS1912-B', 'EXT', f'action-execution:{execution.execution_id}',
        {'next_state_id': 's2'}, authority=Authority.OBSERVATION_ONLY,
    )
    outcome_result = m.record_bounded_action_outcome(
        execution.execution_id, observed, evidence_id='E-MS1912-B'
    )
    assert outcome_result['status'] == 'ACTION_OUTCOME_OBSERVED', outcome_result
    outcome = m.action_closure.outcomes[outcome_result['outcome']['outcome_id']]

    done = advance_epistemic_program_trial(
        trial, intent=intent, execution=execution, outcome=outcome,
        capabilities=m.capabilities, current_frame_epochs=dict(m.frames.epochs),
    )
    assert done.status == 'COMPLETE'
    assert done.discrimination_signature_sha256 == trial.discrimination_signature_sha256
    assert done.source_relation_digests == trial.source_relation_digests
    return done


def test_ranger1_genuine_completed_direct_probe_records_only_bounded_relevance():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_current_direct_probe(m)
        before_events = len(m.store.events())
        result = m.record_completed_epistemic_program_evidence(done, evidence_id='E-MS1912-COMPLETE')
        assert result['status'] == 'PROGRAM_EVIDENCE_RECORDED', result
        assert result['state'] == 'REVISIT_REQUIRED'
        assert result['truth_authority'] == result['answer_authority'] == result['execution_authority'] == 'NONE'
        evidence = m.evidence.get('E-MS1912-COMPLETE')
        assert evidence is not None
        assert evidence['source'] == 'EPISTEMIC_PROGRAM_TRIAL'
        assert evidence['payload']['relevance_authority'] == 'BOUNDED_PROGRAM_DISCRIMINATION_BINDING_ONLY'
        assert evidence['payload']['answer_authority'] == 'NONE'
        assert evidence['payload']['truth_authority'] == 'NONE'
        assert evidence['payload']['execution_authority_gain'] == 'NONE'
        assert len(m.store.events()) > before_events
    finally:
        _close(m, td)


def test_ranger2_matching_copied_discriminator_cannot_launder_replaced_source_ancestry():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_current_direct_probe(m)
        forged = replace(done, source_relation_digests=('f' * 64,))
        assert forged.discrimination_signature_sha256 == done.discrimination_signature_sha256
        assert forged.status == 'COMPLETE' and forged.step_records == done.step_records
        before_events = len(m.store.events())
        result = m.record_completed_epistemic_program_evidence(forged, evidence_id='E-MS1912-FORGED-SOURCE')
        assert result['status'] == 'PROGRAM_EVIDENCE_REJECTED', result
        assert result['reason'] in {
            'PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST',
            'PROGRAM_SOURCE_RELATION_ANCESTRY_NOT_EXACT',
        }
        assert m.evidence.get('E-MS1912-FORGED-SOURCE') is None
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)


def test_ranger3_matching_copied_discriminator_cannot_launder_source_superset():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_current_direct_probe(m)
        forged = replace(
            done,
            source_relation_digests=tuple(sorted(done.source_relation_digests + ('f' * 64,))),
        )
        before_events = len(m.store.events())
        result = m.record_completed_epistemic_program_evidence(forged, evidence_id='E-MS1912-FORGED-SUPERSET')
        assert result['status'] == 'PROGRAM_EVIDENCE_REJECTED', result
        assert result['reason'] == 'PROGRAM_SOURCE_RELATION_ANCESTRY_NOT_EXACT'
        assert m.evidence.get('E-MS1912-FORGED-SUPERSET') is None
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)


def test_ranger4_actual_step_content_cannot_be_laundered_by_valid_source_ancestry():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_current_direct_probe(m)
        bad_record = replace(done.step_records[0], actual_next_state_id='FORGED-MS1912')
        forged = replace(done, step_records=(bad_record,))
        before_events = len(m.store.events())
        result = m.record_completed_epistemic_program_evidence(forged, evidence_id='E-MS1912-FORGED-STEP')
        assert result['status'] == 'PROGRAM_EVIDENCE_REJECTED', result
        assert result['reason'] == 'PROGRAM_STEP_RECORD_CONTENT_MISMATCH'
        assert m.evidence.get('E-MS1912-FORGED-STEP') is None
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)
