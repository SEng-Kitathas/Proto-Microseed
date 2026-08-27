from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, nominate, ctx, act_ob
from microseed import Observation, Authority

td,m,calls,world,trial,dc=fixture()
try:
    n=nominate(m,trial,dc)
    ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ctx(trial,dc))
    assert ex['status']=='ACTION_EXECUTED'
    execution_id=ex['execution']['execution_id']
    obs=Observation('OUT-A','EXT',f'action-execution:{execution_id}',{'next_state_id':'s1','value_id':'V','observed_value':-1.0},authority=Authority.OBSERVATION_ONLY)
    out=m.record_bounded_action_outcome(execution_id,obs,evidence_id='E-OUT-A')
    assert out=={'status':'OUTCOME_REJECTED','reason':'UNKNOWN_ACTION_INTENT_BASIS'},out
    print({'pass':'MS1711','execution':ex['status'],'outcome':out,'calls':calls})
finally:
    td.cleanup()
