from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext,EpistemicStepExecutionContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture,act_ob,fob
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_effect_c,_add_recurrent_chain
from tests.embodiment.test_ms1822_pass15_three_locus_shared_background_priority import _add_shared_fallback


def test_generated_three_step_trial_executes_only_first_primitive_through_existing_effect_lane():
    td,m,calls,_,_,_=fixture()
    try:
        _add_effect_c(m,calls); _add_shared_fallback(m,calls)
        for prefix,effect,end in (('P1',1.0,'u'),('P2',1.0,'u'),('N1',-1.0,'v'),('N2',-1.0,'v')):
            _add_recurrent_chain(m,prefix,effect,end)
        m.observe_opaque_control_state(Observation('CS-1825','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1825')
        admitted=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
        assert admitted['status']=='EPISTEMIC_TRIAL_INSTANTIATED', admitted
        trial=admitted['trial']
        assert trial.steps==('A','B','C') and calls==[]
        surface=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
        nomination=m.nominate_endogenous_epistemic_program_step_intent(trial,dc,'FEAS-A',fob('A'),act_ob())
        assert nomination['status']=='ACTION_INTENT_NOMINATED', nomination
        assert nomination['intent']['capability_id']=='A'
        assert calls==[]
        ctx=EpistemicStepExecutionContext(trial,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc)
        result=m.execute_bounded_action(nomination['intent']['intent_id'],act_ob(),epistemic_step_context=ctx)
        assert result['status']=='ACTION_EXECUTED', result
        assert calls==['A']
        assert 'B' not in calls and 'C' not in calls
        # Selection/instantiation never becomes macro execution authority.
        assert trial.execution_authority=='NONE'
    finally:
        td.cleanup()
