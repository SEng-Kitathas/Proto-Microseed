from __future__ import annotations
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, derive_current_decision_bearing_commitment, derive_current_program_discrimination_commitment
from microseed.development.rehearsal import RehearsalTransitionRelation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, fob, act_ob

def r(state,cap,next_state,effect):
    return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))

def context(h1,h2): return EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))

def test_nondiscriminating_program_does_not_initiate_even_when_unknown_is_decision_bearing():
    td,m,calls,world,t,_=fixture()
    try:
        h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0))
        h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s2',0))
        dc=context(h1,h2)
        n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob())
        assert n['status']=='ABSTAIN' and n['reason']=='PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE'
        assert n['priority']['commitment']=='YES' and n['information']['commitment']=='NO'
        assert calls==[]
    finally: td.cleanup()

def test_informative_program_nominates_when_predicted_observable_traces_differ():
    td,m,calls,world,t,_=fixture()
    try:
        h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0))
        h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s3',0))
        dc=context(h1,h2)
        n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob())
        assert n['status']=='ACTION_INTENT_NOMINATED'
        assert n['priority']['commitment']=='YES' and n['information']['commitment']=='YES'
    finally: td.cleanup()

def test_missing_program_relation_returns_unknown_not_informative():
    td,m,calls,world,t,_=fixture()
    try:
        h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0))
        h2=(r('s0','A','s1',0),r('s0','B','bx',2))
        dc=context(h1,h2)
        n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob())
        assert n['status']=='ABSTAIN' and n['information']['commitment']=='UNKNOWN'
    finally: td.cleanup()

def test_information_commitment_has_zero_authority_surface():
    td,m,calls,world,t,dc=fixture()
    try:
        deficit=m.epistemic_deficits.records[t.deficit_id]
        p=derive_current_decision_bearing_commitment(trial=t,deficit=deficit,decision_context=dc,capabilities=m.capabilities,values=m.values,current_frame_epochs=dict(m.frames.epochs),current_episode_epochs=dict(m.episodes.epochs),current_topology_epochs=dict(m.topologies.epochs),current_coordination_epochs=dict(m.coordinations.epochs))
        info=derive_current_program_discrimination_commitment(trial=t,decision_context=dc,decision_bearing_commitment=p)
        q=dict(info.qualifiers)
        assert q['authority_gain']==q['execution_authority']==q['truth_authority']==q['selection_authority']=='NONE'
    finally: td.cleanup()

def test_actual_intermediate_outcome_reprojects_information_value_before_next_tick():
    from microseed import Observation, Authority
    from microseed.development.epistemic_action import EpistemicStepExecutionContext
    from microseed.development.epistemic_program import advance_epistemic_program_trial
    td,m,calls,world,t,_=fixture()
    try:
        # Informative as modelled from s0: A->s1 then B diverges s2/s3.
        # But the actual first step lands at sx.  From sx the UNKNOWN remains
        # decision-bearing while B has the same observable consequence in both.
        h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0),r('sx','A','ax',2),r('sx','B','same',0))
        h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s3',0),r('sx','A','ax',0),r('sx','B','same',2))
        dc=context(h1,h2)
        n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob()); assert n['status']=='ACTION_INTENT_NOMINATED'
        ec=EpistemicStepExecutionContext(t,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc)
        ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ec); assert ex['status']=='ACTION_EXECUTED'
        xid=ex['execution']['execution_id']
        obs=Observation('OUT-X','EXT',f'action-execution:{xid}',{'next_state_id':'sx'},authority=Authority.OBSERVATION_ONLY)
        out=m.record_bounded_action_outcome(xid,obs,evidence_id='E-OUT-X'); assert out['status']=='ACTION_OUTCOME_OBSERVED'
        t2=advance_epistemic_program_trial(t,intent=m.action_closure.intents[n['intent']['intent_id']],execution=m.action_closure.executions[xid],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs))
        n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob())
        assert n2['status']=='ABSTAIN'
        assert n2['priority']['commitment']=='YES'
        assert n2['information']['commitment']=='NO'
        assert n2['reason']=='PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE'
        assert calls==['A']
    finally: td.cleanup()
