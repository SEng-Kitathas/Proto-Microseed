from dataclasses import replace

from microseed import Authority
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus as _bound, _close
from tests.embodiment.test_ms1918_pass07_authenticated_probe_observation_closure import (
    _install_observation, _execute_probe, _assured_observe, _advance,
)


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


def _complete_authenticated_current_direct_probe(m):
    """Close a current direct probe through the earned execution+observation path.

    MS1918 supersedes the old MS1912 manual action-closure scaffold as a positive
    evidence fixture.  Source-ancestry/content hostiles below still test the MS1912
    owners, but their positive control now uses ordinary execution and authenticated
    observation rather than fabricated closure records.
    """
    _install_observation(m, {'next_state_id':'observed-ms1912'}, bind_frame=True)
    prior, dc, nominated, executed = _execute_probe(m)
    eid = executed['execution']['execution_id']
    observed = _assured_observe(
        m, eid, evidence_id='E-MS1912-AUTH-OUT', capture_id='C-MS1912-AUTH-OUT'
    )
    assert observed['status'] == 'ACTION_OUTCOME_OBSERVED', observed
    done = _advance(m, prior, nominated, executed)
    assert done.status == 'COMPLETE'
    assert done.discrimination_signature_sha256 == prior.discrimination_signature_sha256
    assert done.source_relation_digests == prior.source_relation_digests
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


def test_authenticated_completed_direct_probe_records_only_bounded_relevance():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_authenticated_current_direct_probe(m)
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


def test_authenticated_completed_trial_cannot_launder_replaced_source_ancestry():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_authenticated_current_direct_probe(m)
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


def test_authenticated_completed_trial_cannot_launder_source_superset():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_authenticated_current_direct_probe(m)
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


def test_authenticated_valid_source_ancestry_cannot_launder_forged_step_content():
    td, m, calls, binding, successor = _bound()
    try:
        done = _complete_authenticated_current_direct_probe(m)
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
