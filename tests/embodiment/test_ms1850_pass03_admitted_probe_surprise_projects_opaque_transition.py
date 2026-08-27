from microseed import Authority, CapabilityContract, QualificationState, QueryObligation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture


def _install_observation_ingress(m, next_state):
    m.register_capability(CapabilityContract(
        'OBS-1850','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1850',),'CURRENT',{},
        query_obligation_id='OBS-Q-1850',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'next_state_id':next_state},operational_scope_id='S',
    ))
    m.register_capability(CapabilityContract(
        'BASIS-1850','basis',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1850',),'CURRENT',{},
        dependencies=('OBS-1850',),query_obligation_id='BASIS-Q-1850',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'claim':'BOUNDED_USE_ONLY'},operational_scope_id='S',
    ))
    m.frames.bind_capability('F','A')
    m.frames.bind_capability('F','OBS-1850')


def test_admitted_state_only_probe_surprise_is_opaque_transition_not_value_experience():
    td, m, calls, trial, dc = _generated_fixture()
    try:
        _install_observation_ingress(m, 'sx')
        nomination = m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial, dc, act_ob())
        assert nomination['status'] == 'ACTION_INTENT_NOMINATED', nomination
        ctx = EpistemicStepExecutionContext(trial, decision_context=dc)
        execution = m.execute_bounded_action(nomination['intent']['intent_id'], act_ob(), epistemic_step_context=ctx)
        assert execution['status'] == 'ACTION_EXECUTED', execution
        xid = execution['execution']['execution_id']
        outcome = m.record_bounded_action_outcome_via_observation_basis(
            xid,
            observation_capability_id='OBS-1850',
            observation_obligation=QueryObligation('OBS-Q-1850','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
            basis_capability_id='BASIS-1850',
            basis_obligation=QueryObligation('BASIS-Q-1850','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
            evidence_id='E-1850-CHALLENGE',capture_id='C-1850-CHALLENGE',
        )
        assert outcome['status'] == 'ACTION_OUTCOME_OBSERVED', outcome
        advanced = advance_epistemic_program_trial(
            trial,
            intent=m.action_closure.intents[nomination['intent']['intent_id']],
            execution=m.action_closure.executions[xid],
            outcome=m.action_closure.outcomes[outcome['outcome']['outcome_id']],
            capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs),
        )
        bearing = m.assess_epistemic_program_step_outcome_bearing(trial, advanced, dc)
        assert bearing['status'] == 'MODEL_SPACE_CHALLENGE', bearing
        projected = m.derive_admitted_opaque_transition_sample(xid)
        assert projected['status'] == 'ADMITTED_OPAQUE_TRANSITION_SAMPLE', projected
        sample = projected['sample']
        assert (sample.start_token, sample.action_token, sample.end_token) == ('s0','A','sx')
        assert (sample.frame_id, sample.frame_epoch) == ('F',0)
        assert projected['truth_authority'] == projected['qualification_authority'] == projected['execution_authority'] == 'NONE'
        assert all(x.evidence_id != 'E-1850-CHALLENGE' for x in m._action_outcome_experiences())
        assert calls == ['A']
    finally:
        td.cleanup()
