from dataclasses import replace

from microseed import EpistemicStatus
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    EpistemicStepExecutionContext,
)
from microseed.development.epistemic_program import EpistemicProgramStepRecord
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound, _close


def _current_trial(m):
    formed = m.instantiate_current_revised_surface_direct_probe_trial(
        old_deficit_id='D', successor_deficit_id='D-1904', obligation=act_ob()
    )
    assert formed['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', formed
    return formed['trial']


def test_ranger1_program_intent_cannot_execute_without_epistemic_context():
    td, m, calls, binding, successor = _bound()
    try:
        trial = _current_trial(m)
        feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        nominated = m.nominate_epistemic_program_step_intent(trial, feasibility, act_ob())
        assert nominated['status'] == 'ABSTAIN', nominated
        assert nominated['reason'] == 'EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        assert nominated['local_precheck']['commitment'] == 'YES'
        assert len(m.action_closure.intents)==before_intents
        assert len(m.action_closure.executions)==before_exec
    finally:
        _close(m, td)


def test_ranger2_program_intent_cannot_execute_with_forged_trial_context():
    td, m, calls, binding, successor = _bound()
    try:
        trial = _current_trial(m)
        feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        nominated = m.nominate_epistemic_program_step_intent(trial, feasibility, act_ob())
        assert nominated['status'] == 'ABSTAIN', nominated
        assert nominated['reason'] == 'EPISTEMIC_DECISION_CONTEXT_REQUIRED'
        # A forged trial context cannot be supplied to execution because no intent exists
        # until a current decision-bearing context has already licensed nomination.
        forged = replace(trial, source_relation_digests=('f' * 64,))
        assert forged.digest() != trial.digest()
        assert len(m.action_closure.intents)==before_intents
        assert len(m.action_closure.executions)==before_exec
    finally:
        _close(m, td)


def _synthetic_irrelevant_context(trial):
    # Two fully represented alternatives for the same physical primitive B, deliberately
    # unrelated to the registered revised-surface discriminator. Their digests become the
    # forged trial's source ancestry so the older relation-ancestry check itself passes.
    r1 = RehearsalTransitionRelation(
        state_id=trial.start_state_id, capability_id='B', next_state_id='synthetic-a',
        value_effect=0.0, support=10, consistency=1.0, source_evidence_ids=('SYN-E-1913-A',),
        capability_epoch=dict(trial.capability_epochs)['B'], frame_epoch=('F', 0),
        episode_schema_epoch=('EP', 0),
    )
    r2 = RehearsalTransitionRelation(
        state_id=trial.start_state_id, capability_id='B', next_state_id='synthetic-b',
        value_effect=0.0, support=10, consistency=1.0, source_evidence_ids=('SYN-E-1913-B',),
        capability_epoch=dict(trial.capability_epochs)['B'], frame_epoch=('F', 0),
        episode_schema_epoch=('EP', 0),
    )
    dc = EpistemicDecisionBearingContext(((r1,), (r2,)), ())
    return dc, tuple(sorted((r1.digest(), r2.digest())))


def test_ranger3_irrelevant_but_self_consistent_program_surface_must_not_request_revisit():
    td, m, calls, binding, successor = _bound()
    try:
        trial = _current_trial(m)
        dc, forged_sources = _synthetic_irrelevant_context(trial)
        forged_prior = replace(trial, source_relation_digests=forged_sources)
        fake_record = EpistemicProgramStepRecord(
            step_index=0, capability_id='B', capability_epoch=dict(trial.capability_epochs)['B'],
            intent_id='FAKE-INTENT-1913', execution_id='FAKE-EXEC-1913', outcome_id='FAKE-OUT-1913',
            outcome_evidence_id='FAKE-EVIDENCE-1913', actual_next_state_id='outside-both-models',
            prediction_commitment='FAKE-COMMITMENT-1913',
        )
        forged_advanced = replace(forged_prior, step_records=(fake_record,), status='COMPLETE')
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        before_events = len(m.store.events())
        result = m.assess_epistemic_program_step_outcome_bearing(forged_prior, forged_advanced, dc)
        assert result.get('revisit_status') != 'REVISIT_REQUIRED', result
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert m.evidence.get('FAKE-EVIDENCE-1913') is None
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)


def test_ranger4_genuine_program_step_bearing_requires_action_closure_owned_step_record():
    td, m, calls, binding, successor = _bound()
    try:
        trial = _current_trial(m)
        # Keep the genuine exact source ancestry and build a decision context from the exact
        # current routing relations, but forge only the new physical step record.
        rows = []
        for bucket_id in binding.qualified_bucket_ids:
            rid = binding.relation_id_for(bucket_id, 'B')
            rel = m.action_outcome_learning.relations[rid].as_epistemic_alternative_relation()
            assert rel is not None
            rows.append((rel,))
        dc = EpistemicDecisionBearingContext(tuple(rows), ())
        fake_record = EpistemicProgramStepRecord(
            step_index=0, capability_id='B', capability_epoch=dict(trial.capability_epochs)['B'],
            intent_id='FAKE-INTENT-1913-B', execution_id='FAKE-EXEC-1913-B', outcome_id='FAKE-OUT-1913-B',
            outcome_evidence_id='FAKE-EVIDENCE-1913-B', actual_next_state_id='outside-both-models',
            prediction_commitment='FAKE-COMMITMENT-1913-B',
        )
        forged_advanced = replace(trial, step_records=(fake_record,), status='COMPLETE')
        before_events = len(m.store.events())
        result = m.assess_epistemic_program_step_outcome_bearing(trial, forged_advanced, dc)
        assert result.get('revisit_status') != 'REVISIT_REQUIRED', result
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)


def test_ranger5_legacy_probe_evidence_bridge_cannot_launder_unrelated_evidence_into_modern_revisit():
    td, m, calls, binding, successor = _bound()
    try:
        unrelated = m.append_evidence(
            'E-MS1913-UNRELATED', {'kind':'UNRELATED_PRESSURE','opaque':999},
            EpistemicStatus.PRESSURE_SUPPORTED, source='MS1913_UNRELATED',
        )
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        before_events = len(m.store.events())
        result = m.record_epistemic_probe_evidence('D-1904', unrelated.evidence_id)
        assert result['status'] == 'PROBE_EVIDENCE_REJECTED', result
        assert result['reason'] == 'CURRENT_DERIVED_DISCRIMINATOR_REQUIRES_BOUND_EVIDENCE'
        assert m.epistemic_deficits.records['D-1904'].state.value == 'PROBE_AVAILABLE'
        assert len(m.store.events()) == before_events
    finally:
        _close(m, td)


def test_ranger6_legacy_unbound_probe_evidence_bridge_remains_historically_available():
    from tests.embodiment.test_ms1152_integration import new
    from microseed import Authority, CapabilityContract, QualificationState

    td, m = new()
    try:
        m.append_evidence('U-MS1913-LEGACY', {'opaque':1}, EpistemicStatus.UNKNOWN_INCOMPLETE, source='MS1913')
        m.record_action_limited_unknown(
            deficit_id='D-LEGACY-1913', question_key='Q-LEGACY',
            hypothesis_digest_sha256='a'*64, unknown_evidence_id='U-MS1913-LEGACY',
            missing_discriminator_signature_sha256='b'*64,
        )
        cap = CapabilityContract(
            'probe-legacy-1913','opaque',{}, {},(),(),Authority.DERIVED_READ_ONLY,
            ('MS1128-1152','MS1913_BACKCOMPAT'), 'CURRENT', {},
            qualification=QualificationState.SHADOW_QUALIFIED, handler=lambda **_: 1,
        )
        m.register_capability(cap)
        m.bind_probe_capability('D-LEGACY-1913','probe-legacy-1913')
        ev = m.append_evidence('E-MS1913-LEGACY-PROBE', {'outcome':1}, EpistemicStatus.PRESSURE_SUPPORTED, source='MS1913')
        out = m.record_epistemic_probe_evidence('D-LEGACY-1913', ev.evidence_id)
        assert out['state'] == 'REVISIT_REQUIRED', out
    finally:
        try:
            m.biography.close(); m.evidence.conn.close(); m.store.conn.close()
        except Exception:
            pass
        td.cleanup()


def test_ranger7_explicit_external_revisit_is_visibly_assisted_not_program_evidence():
    td, m, calls, binding, successor = _bound()
    try:
        unrelated = m.append_evidence(
            'E-MS1913-EXTERNAL-RELEVANCE', {'kind':'EXTERNALLY_ASSERTED_RELEVANCE','opaque':123},
            EpistemicStatus.PRESSURE_SUPPORTED, source='MS1913_EXTERNAL_ASSISTANCE',
        )
        deficit = m.epistemic_deficits.records['D-1904']
        result = m.request_epistemic_revisit(
            'D-1904', unrelated.evidence_id,
            relevance_basis_sha256=deficit.missing_discriminator_signature_sha256,
        )
        assert result['state'] == 'REVISIT_REQUIRED', result
        events = [e for e in m.store.events() if e.get('kind') == 'EPISTEMIC_DEFICIT_REVISIT_REQUESTED'
                  and e.get('payload',{}).get('evidence_id') == unrelated.evidence_id]
        assert len(events) == 1
        payload = events[0]['payload']
        assert payload['relevance_authority'] == 'EXPLICIT_BOUNDING_ONLY'
        assert payload['truth_authority'] == 'NONE'
        assert payload['semantic_question_authority'] == 'NONE'
        assert 'program_step_bearing_witness_id' not in payload
        assert 'bearing_witness_id' not in payload
    finally:
        _close(m, td)


def test_ranger8_manual_wrong_probe_rebind_cannot_unlock_current_program_execution():
    td, m, calls, binding, successor = _bound()
    try:
        trial = _current_trial(m)
        # Deliberately overwrite the current probe binding with A, which does not realize the
        # registered B discriminator. The genuine B trial must no longer nominate.
        rebound = m.bind_probe_capability('D-1904', 'A')
        assert rebound['probe_capability_id'] == 'A'
        before = len(m.action_closure.executions)
        feasibility = RecruitmentOption('B', FeasibilityState.FEASIBLE)
        nominated = m.nominate_epistemic_program_step_intent(trial, feasibility, act_ob())
        assert nominated['status'] == 'ABSTAIN', nominated
        assert nominated['reason'] in {
            'EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED',
            'PROBE_AVAILABLE_BOUND_TO_DIFFERENT_PRIMITIVE',
        }
        assert len(m.action_closure.executions) == before
    finally:
        _close(m, td)
