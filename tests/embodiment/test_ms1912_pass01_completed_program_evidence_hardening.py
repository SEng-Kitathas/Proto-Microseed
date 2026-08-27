from dataclasses import replace

from microseed import Authority
from microseed.development.action_closure import BoundedActionIntent, ActionExecutionRecord, ActionOutcomeRecord
from microseed.development.epistemic_action import derive_epistemic_program_step_local_precheck
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound, _close


def _current_direct_probe_trial(m):
    formed = m.instantiate_current_revised_surface_direct_probe_trial(
        old_deficit_id='D', successor_deficit_id='D-1904', obligation=act_ob()
    )
    assert formed['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', formed
    trial = formed['trial']
    assert trial.steps == ('B',) and trial.status == 'OPEN'
    satisfaction = m.derive_current_program_discriminator_satisfaction(trial)
    assert satisfaction.licenses_yes(), satisfaction.serializable()
    return trial, satisfaction


def _scaffold_complete_current_direct_probe(m):
    """Build action-closure-owned records for downstream owner pressure only.

    This is deliberately NOT a lawful organism execution proof. MS1915 established
    that the direct-probe fixture does not currently carry a decision context that
    earns priority+information; the public adapter must therefore abstain. These
    records exist only so the completed-evidence owner can still be attacked for
    binding/content laundering without reopening the unsafe omission path.
    """
    trial, satisfaction = _current_direct_probe_trial(m)
    feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
    local = derive_epistemic_program_step_local_precheck(
        trial=trial,
        deficit=m.epistemic_deficits.records['D-1904'],
        feasibility=feasibility,
        capabilities=m.capabilities,
        obligation=act_ob(),
        current_frame_epochs=dict(m.frames.epochs),
        current_state=m.action_closure.current_state,
        program_discriminator_satisfaction=satisfaction,
    )
    assert local.licenses_yes(), local.serializable()
    assert local.qualifier('decision_premises') == 'LOCAL_PRECHECK_ONLY__NOT_EXECUTABLE'

    epoch = dict(trial.capability_epochs)['B']
    intent = BoundedActionIntent(
        intent_id='MS1912-SCAFFOLD-INTENT', proposal_id=trial.trial_id,
        proposal_digest=trial.digest(), action_commitment=local,
        capability_id='B', capability_epoch=epoch,
        start_state_id=trial.start_state_id,
        control_state_evidence_id=trial.start_state_evidence_id,
        expected_next_state_id=None, expected_value_effect=None, value_epoch=None,
        obligation_id=trial.obligation_id, operational_scope_id=trial.operational_scope_id,
        basis_kind='EPISTEMIC_PROGRAM_STEP',
        execution_authority='NONE', truth_authority='NONE', semantic_intention_authority='NONE',
    )
    m.action_closure.add_intent(intent)

    execution = ActionExecutionRecord(
        execution_id='MS1912-SCAFFOLD-EXECUTION', intent_id=intent.intent_id,
        capability_id='B', capability_epoch=epoch, start_state_id=trial.start_state_id,
        handler_result_sha256='0'*64,
        execution_commitment_id='MS1912-SCAFFOLD-NOT-AUTHORIZATION',
        execution_premise_ids=(local.commitment_id,), authority='NONE',
        observation_authority='NONE', truth_authority='NONE',
    )
    m.action_closure.add_execution(execution)

    prediction = RelationalCommitment(
        'MS1912-SCAFFOLD-PREDICTION', 'ms1912-scaffold-prediction',
        TernaryCommitment.UNKNOWN, reason='TEST_SCAFFOLD_NO_PREDICTION_AUTHORITY',
        qualifiers=(('authority_gain','NONE'),),
    )
    outcome = ActionOutcomeRecord(
        outcome_id='MS1912-SCAFFOLD-OUTCOME', execution_id=execution.execution_id,
        evidence_id='MS1912-SCAFFOLD-EVIDENCE-NOT-PHYSICAL-PROOF', actual_next_state_id='s2',
        observed_value=None, value_id=None, prediction_commitment=prediction,
        state_only=True, execution_authority_gain='NONE', qualification_authority='NONE', truth_authority='NONE',
    )
    m.action_closure.add_outcome(outcome)

    done = advance_epistemic_program_trial(
        trial, intent=intent, execution=execution, outcome=outcome,
        capabilities=m.capabilities, current_frame_epochs=dict(m.frames.epochs),
    )
    assert done.status == 'COMPLETE'
    assert done.discrimination_signature_sha256 == trial.discrimination_signature_sha256
    assert done.source_relation_digests == trial.source_relation_digests
    return done


def test_current_direct_probe_cannot_claim_lawful_execution_without_decision_context():
    td, m, calls, binding, successor = _bound()
    try:
        trial, _ = _current_direct_probe_trial(m)
        feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        nominated = m.nominate_epistemic_program_step_intent(trial, feasibility, act_ob())
        assert nominated['status'] == 'ABSTAIN', nominated
        assert nominated['reason'] == 'EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        assert nominated['local_precheck']['commitment'] == 'YES'
        assert len(m.action_closure.intents)==before_intents
        assert len(m.action_closure.executions)==before_exec
        assert calls == ['A','B']
    finally:
        _close(m, td)


def test_scaffolded_completed_direct_probe_records_only_bounded_relevance():
    td, m, calls, binding, successor = _bound()
    try:
        done = _scaffold_complete_current_direct_probe(m)
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


def test_scaffolded_completed_trial_cannot_launder_replaced_source_ancestry():
    td, m, calls, binding, successor = _bound()
    try:
        done = _scaffold_complete_current_direct_probe(m)
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


def test_scaffolded_completed_trial_cannot_launder_source_superset():
    td, m, calls, binding, successor = _bound()
    try:
        done = _scaffold_complete_current_direct_probe(m)
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


def test_scaffolded_valid_source_ancestry_cannot_launder_forged_step_content():
    td, m, calls, binding, successor = _bound()
    try:
        done = _scaffold_complete_current_direct_probe(m)
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
