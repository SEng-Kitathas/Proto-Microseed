from __future__ import annotations
from microseed import Observation, Authority
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.development.rehearsal import RehearsalTransitionRelation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob, fob


def rr(state,cap,next_state,effect):
    return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))

def two_tick_fixture():
    td,m,calls,world,trial,_=fixture()
    h1=(rr('s0','A','s1',2.0),rr('s0','B','bx',0.0),rr('s1','A','ax1',0.0),rr('s1','B','s2',2.0))
    h2=(rr('s0','A','s1',0.0),rr('s0','B','bx',2.0),rr('s1','A','ax1',2.0),rr('s1','B','s3',0.0))
    dc=EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
    return td,m,calls,world,trial,dc

def do_first(td,m,calls,world,trial,dc):
    n=m.nominate_endogenous_epistemic_program_step_intent(trial,dc,'FEAS-A',fob('A'),act_ob())
    assert n['status']=='ACTION_INTENT_NOMINATED' and n['intent']['capability_id']=='A'
    c=EpistemicStepExecutionContext(trial,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc)
    ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=c); assert ex['status']=='ACTION_EXECUTED'
    xid=ex['execution']['execution_id']
    obs=Observation('OUT-A','EXT',f'action-execution:{xid}',{'next_state_id':'s1'},authority=Authority.OBSERVATION_ONLY)
    out=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-A'); assert out['status']=='ACTION_OUTCOME_OBSERVED'
    t2=advance_epistemic_program_trial(trial,intent=m.action_closure.intents[n['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
    assert t2.status=='OPEN' and len(t2.step_records)==1 and m.action_closure.current_state.state_id=='s1'
    return n,ex,out,t2

def test_second_tick_is_freshly_nominated_from_advanced_trial_and_actual_state():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,calls,world,trial,dc)
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        assert n2['status']=='ACTION_INTENT_NOMINATED' and n2['intent']['capability_id']=='B'
        assert n2['intent']['start_state_id']=='s1' and n2['intent']['control_state_evidence_id']=='E-OUT-A'
        assert n2['intent']['proposal_digest']==t2.digest()
        c2=EpistemicStepExecutionContext(t2,feasibility_capability_id='FEAS-B',feasibility_obligation=fob('B'),decision_context=dc)
        ex2=m.execute_bounded_action(n2['intent']['intent_id'],act_ob(),epistemic_step_context=c2)
        assert ex2['status']=='ACTION_EXECUTED' and calls==['A','B']
    finally: td.cleanup()

def test_tick0_trial_cannot_nominate_tick1_from_later_control_state():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        do_first(td,m,calls,world,trial,dc)
        old=m.nominate_endogenous_epistemic_program_step_intent(trial,dc,'FEAS-A',fob('A'),act_ob())
        assert old['status']=='ABSTAIN'
    finally: td.cleanup()

def test_priority_must_be_reearned_after_first_actual_outcome():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,calls,world,trial,dc)
        m.observe_value_state('V',5.0)
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        assert n2['status']=='ABSTAIN' and n2['priority']['commitment']=='NO'
    finally: td.cleanup()

def test_second_step_feasibility_must_be_reearned_after_first_actual_outcome():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,calls,world,trial,dc)
        world['B']='REFUSED'
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        assert n2['status']=='ABSTAIN'
    finally: td.cleanup()

def test_frame_drift_after_first_outcome_blocks_second_tick():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,calls,world,trial,dc)
        m.change_operational_frame('F',reason='AFTER_STEP_ONE')
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        assert n2['status']=='ABSTAIN'
    finally: td.cleanup()

def test_two_fresh_ticks_bind_into_complete_trial_only_after_second_actual_outcome():
    td,m,calls,world,trial,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,calls,world,trial,dc)
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        c2=EpistemicStepExecutionContext(t2,feasibility_capability_id='FEAS-B',feasibility_obligation=fob('B'),decision_context=dc)
        ex2=m.execute_bounded_action(n2['intent']['intent_id'],act_ob(),epistemic_step_context=c2); assert ex2['status']=='ACTION_EXECUTED'
        xid=ex2['execution']['execution_id']
        obs=Observation('OUT-B','EXT',f'action-execution:{xid}',{'next_state_id':'s2'},authority=Authority.OBSERVATION_ONLY)
        out=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-B'); assert out['status']=='ACTION_OUTCOME_OBSERVED'
        t3=advance_epistemic_program_trial(t2,intent=m.action_closure.intents[n2['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
        assert t3.status=='COMPLETE' and len(t3.step_records)==2 and calls==['A','B']
    finally: td.cleanup()
