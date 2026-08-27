from microseed import Authority, QueryObligation
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1850_pass03_admitted_probe_surprise_projects_opaque_transition import _install_observation_ingress


def test_admitted_first_step_model_challenge_has_no_predecessor_context_and_does_not_auto_refine_state():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        _install_observation_ingress(m,'sx')
        nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob())
        assert nomination['status']=='ACTION_INTENT_NOMINATED',nomination
        ctx=EpistemicStepExecutionContext(trial,decision_context=dc)
        execution=m.execute_bounded_action(nomination['intent']['intent_id'],act_ob(),epistemic_step_context=ctx)
        assert execution['status']=='ACTION_EXECUTED',execution
        xid=execution['execution']['execution_id']
        out=m.record_bounded_action_outcome_via_observation_basis(
            xid,observation_capability_id='OBS-1850',observation_obligation=QueryObligation('OBS-Q-1850','observe',Authority.OBSERVATION_ONLY,operational_scope_id='S'),
            basis_capability_id='BASIS-1850',basis_obligation=QueryObligation('BASIS-Q-1850','basis',Authority.DERIVED_READ_ONLY,operational_scope_id='S'),
            evidence_id='E-1857-CHALLENGE',capture_id='C-1857-CHALLENGE',
        )
        assert out['status']=='ACTION_OUTCOME_OBSERVED',out
        advanced=advance_epistemic_program_trial(trial,intent=m.action_closure.intents[nomination['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
        bearing=m.assess_epistemic_program_step_outcome_bearing(trial,advanced,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE' and bearing['revisit_status']=='REVISIT_REQUIRED'
        sample=m.derive_admitted_opaque_transition_sample(xid)
        assert sample['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        refinement=m.derive_admitted_one_step_visible_history_refinements()
        assert refinement['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT',refinement
        assert refinement['successor_pair_count']==0
        assert refinement['refinements']==()
        assert calls==['A']
    finally:td.cleanup()
