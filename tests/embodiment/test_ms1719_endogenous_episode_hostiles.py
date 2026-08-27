from __future__ import annotations
from microseed import Observation, Authority
from microseed.development.epistemic_action import EpistemicStepExecutionContext, EpistemicDecisionBearingContext
from microseed.development.rehearsal import RehearsalTransitionRelation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, fob, act_ob

def r(state,cap,next_state,effect): return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))
def informative():
    h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0))
    h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s3',0))
    return EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
def nondiscriminating():
    h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0))
    h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s2',0))
    return EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
def execute_first(m,t,dc):
    n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob()); assert n['status']=='ACTION_INTENT_NOMINATED'
    ec=EpistemicStepExecutionContext(t,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc)
    ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ec); assert ex['status']=='ACTION_EXECUTED'
    return n,ex

def test_model_output_cannot_masquerade_as_epistemic_step_actual_outcome():
    td,m,c,w,t,_=fixture()
    try:
        dc=informative();n,ex=execute_first(m,t,dc);x=ex['execution']['execution_id']
        obs=Observation('O','MODEL',f'action-execution:{x}',{'next_state_id':'s1'},authority=Authority.MODEL_OUTPUT_ONLY)
        assert m.record_bounded_action_outcome(x,obs,evidence_id='E')['reason']=='CONTENT_BOUND_EXTERNAL_OBSERVATION_REQUIRED'
    finally:td.cleanup()
def test_wrong_execution_referent_cannot_close_epistemic_step():
    td,m,c,w,t,_=fixture()
    try:
        dc=informative();n,ex=execute_first(m,t,dc);x=ex['execution']['execution_id']
        obs=Observation('O','EXT','action-execution:WRONG',{'next_state_id':'s1'},authority=Authority.OBSERVATION_ONLY)
        assert m.record_bounded_action_outcome(x,obs,evidence_id='E')['reason']=='CONTENT_BOUND_EXTERNAL_OBSERVATION_REQUIRED'
    finally:td.cleanup()
def test_missing_actual_state_cannot_be_filled_from_relational_prediction():
    td,m,c,w,t,_=fixture()
    try:
        dc=informative();n,ex=execute_first(m,t,dc);x=ex['execution']['execution_id']
        obs=Observation('O','EXT',f'action-execution:{x}',{},authority=Authority.OBSERVATION_ONLY)
        assert m.record_bounded_action_outcome(x,obs,evidence_id='E')['reason']=='EPISTEMIC_STEP_OUTCOME_FIELDS_MISSING'
    finally:td.cleanup()
def test_value_claim_cannot_be_smuggled_into_state_only_program_observation():
    td,m,c,w,t,_=fixture()
    try:
        dc=informative();n,ex=execute_first(m,t,dc);x=ex['execution']['execution_id']
        obs=Observation('O','EXT',f'action-execution:{x}',{'next_state_id':'s1','value_id':'V','observed_value':1.0},authority=Authority.OBSERVATION_ONLY)
        assert m.record_bounded_action_outcome(x,obs,evidence_id='E')['reason']=='EPISTEMIC_STEP_VALUE_CLAIM_NOT_ALLOWED'
    finally:td.cleanup()
def test_information_value_collapse_between_nomination_and_effect_blocks_execution():
    td,m,c,w,t,_=fixture()
    try:
        dc=informative();n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob()); assert n['status']=='ACTION_INTENT_NOMINATED'
        ec=EpistemicStepExecutionContext(t,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=nondiscriminating())
        out=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ec)
        assert out['status']=='NO_EXECUTION' and c==[]
    finally:td.cleanup()
def test_decision_bearing_without_information_value_never_calls_effect():
    td,m,c,w,t,_=fixture()
    try:
        n=m.nominate_endogenous_epistemic_program_step_intent(t,nondiscriminating(),'FEAS-A',fob('A'),act_ob())
        assert n['status']=='ABSTAIN' and n['priority']['commitment']=='YES' and n['information']['commitment']=='NO' and c==[]
    finally:td.cleanup()
