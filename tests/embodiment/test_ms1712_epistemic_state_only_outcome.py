from __future__ import annotations
from microseed import Observation, Authority
from microseed.development.epistemic_program import advance_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob


def execute_first():
    td,m,calls,world,trial,dc=fixture()
    n=nominate(m,trial,dc)
    ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(trial,dc))
    assert ex['status']=='ACTION_EXECUTED'
    return td,m,calls,world,trial,dc,n,ex

def test_epistemic_step_accepts_external_state_only_outcome_and_updates_control_state():
    td,m,*rest=execute_first(); ex=rest[-1]
    try:
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-A','EXT',f'action-execution:{xid}',{'next_state_id':'s1'},authority=Authority.OBSERVATION_ONLY)
        r=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-A')
        assert r['status']=='ACTION_OUTCOME_OBSERVED'
        assert r['outcome']['state_only'] is True
        assert r['outcome']['value_id'] is None and r['outcome']['observed_value'] is None
        assert r['outcome']['prediction_commitment']['commitment']=='UNKNOWN'
        assert m.action_closure.current_state.state_id=='s1'
        assert m.action_closure.current_state.evidence_id=='E-OUT-A'
    finally: td.cleanup()

def test_epistemic_step_state_only_outcome_refuses_value_claim_smuggling():
    td,m,*rest=execute_first(); ex=rest[-1]
    try:
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-A','EXT',f'action-execution:{xid}',{'next_state_id':'s1','value_id':'V','observed_value':0.0},authority=Authority.OBSERVATION_ONLY)
        r=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-A')
        assert r=={'status':'OUTCOME_REJECTED','reason':'EPISTEMIC_STEP_VALUE_CLAIM_NOT_ALLOWED'}
    finally: td.cleanup()

def test_state_only_outcome_advances_program_trial_from_actual_records():
    td,m,calls,world,trial,dc,n,ex=execute_first()
    try:
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-A','EXT',f'action-execution:{xid}',{'next_state_id':'s1'},authority=Authority.OBSERVATION_ONLY)
        r=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-A'); assert r['status']=='ACTION_OUTCOME_OBSERVED'
        intent=m.action_closure.intents[n['intent']['intent_id']]
        execution=m.action_closure.executions[xid]
        outcome=m.action_closure.outcomes[r['outcome']['outcome_id']]
        t2=advance_epistemic_program_trial(trial,intent=intent,execution=execution,outcome=outcome,capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
        assert t2.status=='OPEN' and len(t2.step_records)==1
        assert t2.step_records[0].actual_next_state_id=='s1'
        assert t2.step_records[0].outcome_evidence_id=='E-OUT-A'
    finally: td.cleanup()

def test_state_only_outcome_does_not_enter_value_effect_learning():
    td,m,*rest=execute_first(); ex=rest[-1]
    try:
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-A','EXT',f'action-execution:{xid}',{'next_state_id':'s1'},authority=Authority.OBSERVATION_ONLY)
        r=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-A'); assert r['status']=='ACTION_OUTCOME_OBSERVED'
        assert m._action_outcome_experiences()==()
    finally: td.cleanup()
