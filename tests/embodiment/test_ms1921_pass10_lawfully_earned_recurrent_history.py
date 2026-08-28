from __future__ import annotations

from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install, _close


def _close_fixture(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def _run_live_step(m, outcomes, trial, dc, *, end: str, tag: str):
    nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob())
    assert nomination['status']=='ACTION_INTENT_NOMINATED',nomination
    ctx=EpistemicStepExecutionContext(trial,decision_context=dc)
    execution=m.execute_bounded_action(nomination['intent']['intent_id'],act_ob(),epistemic_step_context=ctx)
    assert execution['status']=='ACTION_EXECUTED',execution
    xid=execution['execution']['execution_id']
    outcomes[xid]=end
    observed=_close(m,outcomes,xid,end,tag)
    assert observed['status']=='ACTION_OUTCOME_OBSERVED',observed
    advanced=advance_epistemic_program_trial(
        trial,
        intent=m.action_closure.intents[nomination['intent']['intent_id']],
        execution=m.action_closure.executions[xid],
        outcome=m.action_closure.outcomes[observed['outcome']['outcome_id']],
        capabilities=m.capabilities,
        current_frame_epochs=dict(m.frames.epochs),
    )
    return advanced,xid


def _two_same_context_runs():
    td,m,calls,trial0,dc=_generated_fixture()
    outcomes={}; _install(m,outcomes)
    rows=[]
    for idx in range(2):
        if idx:
            m.observe_opaque_control_state(
                Observation(f'MS1921-RESET-{idx}','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
                evidence_id=f'E-MS1921-RESET-{idx}',
            )
            admitted=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
            assert admitted['status']=='EPISTEMIC_TRIAL_INSTANTIATED',admitted
            trial=admitted['trial']
        else:
            trial=trial0
        t1,x_a=_run_live_step(m,outcomes,trial,dc,end='s1',tag=f'R{idx}-A')
        t2,x_b=_run_live_step(m,outcomes,t1,dc,end='sx',tag=f'R{idx}-B')
        rows.append((x_a,x_b))
    return td,m,calls,dc,rows


def test_ranger1_two_fresh_generated_trials_lawfully_earn_same_context_recurrence():
    td,m,calls,dc,rows=_two_same_context_runs()
    try:
        assert calls==['A','B','A','B']
        assert len({x_b for _,x_b in rows})==2
        surface=m.derive_admitted_one_step_visible_history_refinements()
        assert surface['admitted_sample_count']==4
        assert surface['successor_pair_count']==2
        assert surface['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT'
        assert len(surface['refinements'])==0
        assert m.epistemic_deficits.records['D'].state.value=='ACTION_LIMITED'
    finally:_close_fixture(m,td)


def test_ranger2_each_b_step_is_bound_to_its_own_authenticated_a_outcome():
    td,m,calls,dc,rows=_two_same_context_runs()
    try:
        a_outcome_evidence={
            x_a: next(o.evidence_id for o in m.action_closure.outcomes.values() if o.execution_id==x_a)
            for x_a,_ in rows
        }
        for x_a,x_b in rows:
            b_ex=m.action_closure.executions[x_b]
            b_intent=m.action_closure.intents[b_ex.intent_id]
            assert b_intent.start_state_id=='s1'
            assert b_intent.control_state_evidence_id==a_outcome_evidence[x_a]
            assert m.derive_admitted_opaque_transition_sample(x_a)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
            assert m.derive_admitted_opaque_transition_sample(x_b)['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
    finally:_close_fixture(m,td)


def test_ranger3_unrepresented_second_context_has_no_generated_or_regulatory_escape_route():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        m.observe_opaque_control_state(
            Observation('MS1921-CONTEXT-R','EXT','opaque-control','r',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-MS1921-CONTEXT-R',
        )
        generated=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
        assert generated['status']=='ABSTAIN'
        assert generated['reason']=='CURRENT_GENERATOR_TRANSITION_UNREPRESENTED'

        license_result=m.derive_multi_value_action_licenses(('V',))
        assert license_result['status']=='UNKNOWN_ACTION_SELECTION'
        assert license_result['licensed_action_ids']==[]
        assert license_result['overall_commitment']['reason']=='NO_FULLY_LICENSED_ACTION'
        nomination=m.nominate_multi_value_action_intent(('V',),act_ob())
        assert nomination['status']=='ABSTAIN'
        assert nomination['reason']=='NO_FULLY_LICENSED_ACTION'
        assert calls==[]
    finally:_close_fixture(m,td)


def test_ranger4_same_context_recurrence_is_not_silently_promoted_to_multi_context_refinement():
    td,m,calls,dc,rows=_two_same_context_runs()
    try:
        surface=m.derive_admitted_one_step_visible_history_refinements()
        assert surface['successor_pair_count']==2
        assert surface['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT'
        # Both lawful predecessor samples originate at the same visible context s0.
        contexts=[]
        for x_a,x_b in rows:
            a=m.derive_admitted_opaque_transition_sample(x_a)['sample']
            b=m.derive_admitted_opaque_transition_sample(x_b)['sample']
            assert a.end_token==b.start_token=='s1'
            contexts.append(a.start_token)
        assert contexts==['s0','s0']
        assert len(set(contexts))==1
    finally:_close_fixture(m,td)
