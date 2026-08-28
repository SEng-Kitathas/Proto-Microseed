from __future__ import annotations

from dataclasses import replace

from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus, _close


def _nominate_current_probe(m):
    surface=m.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
    assert surface['status']=='CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE',surface
    trial_out=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
    assert trial_out['status']=='EPISTEMIC_TRIAL_INSTANTIATED',trial_out
    trial=trial_out['trial']
    dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
    nominated=m.nominate_grounded_epistemic_program_step_intent(trial,'FEAS-B',fob('B'),act_ob(),decision_context=dc)
    assert nominated['status']=='ACTION_INTENT_NOMINATED',nominated
    assert nominated['priority']['commitment']=='YES'
    assert nominated['information']['commitment']=='YES'
    return trial,dc,nominated


def _execute(m,trial,dc,intent_id):
    return m.execute_bounded_action(
        intent_id,act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(
            trial,
            feasibility_capability_id='FEAS-B',
            feasibility_obligation=fob('B'),
            decision_context=dc,
        ),
    )


def test_ranger1_unchanged_current_probe_reauthorizes_and_executes_once():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='ACTION_EXECUTED',out
        assert len(m.action_closure.executions)==before+1
        assert out['execution']['execution_premise_ids']
        assert out['observation_recorded'] is False
        assert calls[-1]=='B'
    finally:_close(m,td)


def test_ranger2_background_ambiguity_added_after_nomination_must_block_execution():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        original=next(
            r for r in m.action_outcome_learning.relations.values()
            if r.start_state_id=='s1' and r.capability_id=='D' and m._action_outcome_relation_current(r)
        )
        duplicate=replace(
            original,
            relation_id='MS1917-AMBIGUOUS-BACKGROUND-D',
            next_state_id='ms1917-other-d',
            value_effect=float(original.value_effect)+0.5,
        )
        m.action_outcome_learning.add_relation(duplicate)
        fresh=m.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
        assert fresh['status']=='ABSTAIN'
        assert fresh['reason']=='DIRECT_PROBE_BACKGROUND_RELATION_AMBIGUOUS'

        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='NO_EXECUTION',out
        assert out['reason']=='CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE_REQUIRED_AT_EXECUTION'
        assert len(m.action_closure.executions)==before
        assert calls[-1]!='B' or calls.count('B')==1
    finally:_close(m,td)


def test_ranger3_control_state_drift_after_nomination_blocks_before_effect():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        m.observe_opaque_control_state(
            Observation('MS1917-DRIFT-S2','EXT','opaque-control','s2',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-MS1917-DRIFT-S2',
        )
        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='NO_EXECUTION'
        assert out['reason']=='CONTROL_STATE_DRIFT'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_ranger4_probe_capability_epoch_drift_after_nomination_blocks_before_effect():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        m.invalidate_capability('B',reason='MS1917_PROBE_EPOCH_DRIFT')
        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='NO_EXECUTION'
        assert out['reason']=='EFFECT_CAPABILITY_NOT_CURRENT'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_ranger5_execution_can_rederive_revised_probe_context_without_caller_reusing_nomination_context():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        before=len(m.action_closure.executions)
        out=m.execute_bounded_action(
            n['intent']['intent_id'],act_ob(),
            epistemic_step_context=EpistemicStepExecutionContext(
                trial,
                feasibility_capability_id='FEAS-B',
                feasibility_obligation=fob('B'),
            ),
        )
        assert out['status']=='ACTION_EXECUTED',out
        assert len(m.action_closure.executions)==before+1
        assert out['execution']['execution_premise_ids']
        assert calls[-1]=='B'
    finally:_close(m,td)


def test_ranger6_ambiguous_successor_lineage_cannot_choose_a_predecessor_at_execution():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        deficit=m.epistemic_deficits.records['D-1904']
        deficit.assistance_ancestry=tuple(deficit.assistance_ancestry)+('SUCCESSOR_OF:OTHER-DEFICIT',)
        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='NO_EXECUTION',out
        assert out['reason']=='CURRENT_REVISED_DIRECT_PROBE_PREDECESSOR_REQUIRED'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)


def test_ranger7_current_source_relation_content_drift_cannot_reuse_old_trial_ancestry():
    td,m,calls,b,s=_bound_at_probe_locus()
    try:
        trial,dc,n=_nominate_current_probe(m)
        rid='R-B-S2-1868'
        original=m.action_outcome_learning.relations[rid]
        m.action_outcome_learning.relations[rid]=replace(
            original,
            value_effect=float(original.value_effect)-0.25,
        )
        fresh=m.derive_current_revised_surface_direct_probe_decision_surface(
            old_deficit_id='D',successor_deficit_id='D-1904',
        )
        assert fresh['status']=='CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE'
        assert tuple(sorted(fresh['source_relation_digests']))!=tuple(sorted(trial.source_relation_digests))
        before=len(m.action_closure.executions)
        out=_execute(m,trial,dc,n['intent']['intent_id'])
        assert out['status']=='NO_EXECUTION',out
        assert out['reason']=='CURRENT_REVISED_DIRECT_PROBE_SOURCE_ANCESTRY_DRIFT'
        assert len(m.action_closure.executions)==before
    finally:_close(m,td)
