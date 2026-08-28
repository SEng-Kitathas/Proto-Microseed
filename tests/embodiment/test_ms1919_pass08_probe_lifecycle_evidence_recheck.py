from __future__ import annotations

from dataclasses import replace

from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus, _close
from tests.embodiment.test_ms1918_pass07_authenticated_probe_observation_closure import (
    _install_observation, _execute_probe, _assured_observe, _advance, _raw_forged_observe,
)


def _authenticated_complete(next_state: str = 'ms1919-observed'):
    td,m,calls,b,s=_bound_at_probe_locus()
    _install_observation(m,{'next_state_id':next_state},bind_frame=True)
    prior,dc,n,e=_execute_probe(m)
    eid=e['execution']['execution_id']
    out=_assured_observe(m,eid,evidence_id=f'E-MS1919-{next_state}',capture_id=f'C-MS1919-{next_state}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    advanced=_advance(m,prior,n,e)
    return td,m,calls,prior,dc,n,e,advanced,eid


def test_ranger1_basis_drift_after_bearing_cannot_bypass_completed_evidence_authentication():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('basis-drift-after-bearing')
    try:
        bearing=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE' and bearing['revisit_status']=='REVISIT_REQUIRED'
        assert m.epistemic_deficits.records['D-1904'].state.value=='REVISIT_REQUIRED'
        stale=m.invalidate_capability('BASIS-1918',reason='MS1919_POST_BEARING_BASIS_DRIFT')
        assert 'BASIS-1918' in stale
        assert m.derive_admitted_opaque_transition_sample(eid)['reason']=='LIVE_OBSERVATION_ADMISSION_NOT_CURRENT'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1919-AFTER-BASIS-DRIFT')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED',result
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
        assert m.evidence.get('E-MS1919-AFTER-BASIS-DRIFT') is None
    finally:_close(m,td)


def test_ranger2_source_relation_drift_after_bearing_cannot_bypass_discriminator_satisfaction():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('source-drift-after-bearing')
    try:
        bearing=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE' and bearing['revisit_status']=='REVISIT_REQUIRED'
        formed=m.derive_current_revised_surface_direct_probe_program_candidate(old_deficit_id='D',successor_deficit_id='D-1904')
        rid=formed['source_relation_ids'][0]
        relation=m.action_outcome_learning.relations[rid]
        m.action_outcome_learning.relations[rid]=replace(relation,next_state_id='MS1919-SOURCE-CONTENT-DRIFT')
        satisfaction=m.derive_current_program_discriminator_satisfaction(prior)
        assert satisfaction.commitment.value=='UNKNOWN'
        assert satisfaction.reason=='PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1919-AFTER-SOURCE-DRIFT')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED',result
        assert result['reason']=='PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST'
        assert m.evidence.get('E-MS1919-AFTER-SOURCE-DRIFT') is None
    finally:_close(m,td)


def test_ranger3_repeated_step_bearing_after_observation_stales_must_recheck_probe_authentication():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('repeat-bearing-stale')
    try:
        first=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert first['status']=='MODEL_SPACE_CHALLENGE' and first['duplicate'] is False
        m.invalidate_capability('BASIS-1918',reason='MS1919_REPEAT_BEARING_STALE')
        second=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert second['status']=='PROGRAM_STEP_BEARING_UNRESOLVED',second
        assert second['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
    finally:_close(m,td)


def test_ranger4_unrelated_revisit_transition_cannot_turn_raw_outcome_into_probe_program_evidence():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        prior,dc,n,e=_execute_probe(m)
        eid=e['execution']['execution_id']
        raw=_raw_forged_observe(m,eid,evidence_id='E-MS1919-RAW',state='raw-untrusted')
        assert raw['status']=='ACTION_OUTCOME_OBSERVED'
        advanced=_advance(m,prior,n,e)
        m.epistemic_deficits.request_revisit('D-1904','E-MS1919-RAW')
        assert m.epistemic_deficits.records['D-1904'].state.value=='REVISIT_REQUIRED'
        assert m.derive_admitted_opaque_transition_sample(eid)['status']=='ABSTAIN'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1919-RAW-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_REJECTED',result
        assert result['reason']=='AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED'
        assert m.evidence.get('E-MS1919-RAW-COMPLETE') is None
    finally:_close(m,td)


def test_ranger5_current_authenticated_probe_can_record_completed_evidence_after_bearing_revisit():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('positive-after-bearing')
    try:
        bearing=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE' and bearing['revisit_status']=='REVISIT_REQUIRED'
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        result=m.record_completed_epistemic_program_evidence(advanced,evidence_id='E-MS1919-POSITIVE-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_RECORDED',result
        assert result['state']=='REVISIT_REQUIRED'
        assert result['truth_authority']==result['answer_authority']==result['execution_authority']=='NONE'
    finally:_close(m,td)


def test_ranger6_authenticated_challenge_does_not_auto_create_revision_or_successor():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('no-auto-revision')
    try:
        bearing=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE'
        refinement=m.derive_revisit_one_step_visible_history_refinement('D-1904')
        assert refinement['status']=='NO_BOUNDED_REFINEMENT_FOR_REVISIT',refinement
        revision=m.derive_current_revisit_hypothesis_revision_surface('D-1904')
        assert revision['status']=='NO_CURRENT_REVISED_HYPOTHESIS_SURFACE',revision
        binding_id=next(iter(sorted(m.action_outcome_learning.projection_conditioned_bindings)))
        accepted=m.accept_revisit_hypothesis_revision('D-1904',binding_id)
        assert accepted=={'status':'REVISION_NOT_ACCEPTED','reason':'NO_CURRENT_REVISED_HYPOTHESIS_SURFACE','authority':'NONE'}
        try:
            m.record_revised_surface_action_limited_unknown(
                old_deficit_id='D-1904',new_deficit_id='D-1919',unknown_evidence_id='E-U-1904-LOCUS')
        except ValueError as exc:
            assert str(exc)=='REVISED_SURFACE_SUCCESSOR_REQUIRES_STALE_OLD_DEFICIT'
        else:
            raise AssertionError('successor was created without accepted/staled revision')
    finally:_close(m,td)


def test_ranger7_repeated_step_bearing_after_source_drift_must_recheck_discriminator_satisfaction():
    td,m,calls,prior,dc,n,e,advanced,eid=_authenticated_complete('repeat-bearing-source-drift')
    try:
        first=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert first['status']=='MODEL_SPACE_CHALLENGE' and first['duplicate'] is False
        formed=m.derive_current_revised_surface_direct_probe_program_candidate(old_deficit_id='D',successor_deficit_id='D-1904')
        rid=formed['source_relation_ids'][0]
        relation=m.action_outcome_learning.relations[rid]
        m.action_outcome_learning.relations[rid]=replace(relation,next_state_id='MS1919-REPEAT-SOURCE-DRIFT')
        second=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
        assert second['status']=='PROGRAM_STEP_BEARING_UNRESOLVED',second
        assert second['reason']=='PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST'
        assert second['program_discriminator_satisfaction']['commitment']=='UNKNOWN'
    finally:_close(m,td)
