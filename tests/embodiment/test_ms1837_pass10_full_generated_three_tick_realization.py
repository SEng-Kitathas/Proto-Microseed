from microseed import Authority, CapabilityContract, Observation, QualificationState
from microseed.development.epistemic import EpistemicDeficitState
from microseed.development.epistemic_action import EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture


def _add_feas_c(m):
    m.register_capability(CapabilityContract(
        'FEAS-C','feas',{'target_capability_id':'C'},{},(),(),Authority.DERIVED_READ_ONLY,('T',),'CURRENT',{},
        dependencies=('C',),query_obligation_id='QF-C',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'feasibility':'FEASIBLE','reason':'FRESH_WORLD'},operational_scope_id='S',
    ))


def _run_one(m, trial, dc, expected_cap, next_state, evidence_id):
    nomination=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(trial,dc,act_ob())
    assert nomination['status']=='ACTION_INTENT_NOMINATED', nomination
    assert nomination['intent']['capability_id']==expected_cap
    ctx=EpistemicStepExecutionContext(trial,decision_context=dc)
    execution=m.execute_bounded_action(nomination['intent']['intent_id'],act_ob(),epistemic_step_context=ctx)
    assert execution['status']=='ACTION_EXECUTED', execution
    xid=execution['execution']['execution_id']
    obs=Observation('OBS-'+evidence_id,'EXT',f'action-execution:{xid}',{'next_state_id':next_state},authority=Authority.OBSERVATION_ONLY)
    outcome=m.record_bounded_action_outcome(xid,obs,evidence_id=evidence_id)
    assert outcome['status']=='ACTION_OUTCOME_OBSERVED', outcome
    advanced=advance_epistemic_program_trial(
        trial,intent=m.action_closure.intents[nomination['intent']['intent_id']],execution=m.action_closure.executions[xid],
        outcome=m.action_closure.outcomes[outcome['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs),
    )
    bearing=m.assess_epistemic_program_step_outcome_bearing(trial,advanced,dc)
    return advanced,bearing


def test_generated_program_runs_three_separate_ticks_and_final_actual_observation_requests_revisit():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        _add_feas_c(m)
        t1,b1=_run_one(m,trial,dc,'A','s1','E-1837-A')
        assert b1['status']=='CONSENSUS_NONDISCRIMINATING'
        assert t1.status=='OPEN' and calls==['A']
        t2,b2=_run_one(m,t1,dc,'B','s2','E-1837-B')
        assert b2['status']=='CONSENSUS_NONDISCRIMINATING'
        assert t2.status=='OPEN' and calls==['A','B']
        t3,b3=_run_one(m,t2,dc,'C','u','E-1837-C')
        assert t3.status=='COMPLETE' and calls==['A','B','C']
        assert b3['status']=='DISCRIMINATES_LIVE_SET', b3
        assert b3['revisit_status']=='REVISIT_REQUIRED'
        assert m.epistemic_deficits.records[trial.deficit_id].state==EpistemicDeficitState.REVISIT_REQUIRED
        assert b3['truth_authority']==b3['answer_authority']==b3['model_replacement_authority']=='NONE'
    finally:
        td.cleanup()
