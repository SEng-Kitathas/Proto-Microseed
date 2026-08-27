from __future__ import annotations
import json
from pathlib import Path
from dataclasses import replace
from microseed import Observation, Authority
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, EpistemicStepExecutionContext
from microseed.development.epistemic_program import advance_epistemic_program_trial
from microseed.development.rehearsal import RehearsalTransitionRelation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, fob, act_ob
from tests.embodiment.test_ms1713_tick_reauthorization import two_tick_fixture, do_first
from tests.embodiment.test_ms1717_program_evidence_revisit import complete_trial

def r(state,cap,next_state,effect): return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))
def nondisc_context():
    h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0));h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s2',0))
    return EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))

def family_lawful():
    td,m,c,w,t,dc=two_tick_fixture()
    try:
        done=complete_trial(m,t,dc); return done.status=='COMPLETE' and c==['A','B']
    finally:td.cleanup()
def family_nondisc():
    td,m,c,w,t,_=fixture()
    try:
        n=m.nominate_endogenous_epistemic_program_step_intent(t,nondisc_context(),'FEAS-A',fob('A'),act_ob());return n['status']=='ABSTAIN' and n['information']['commitment']=='NO' and c==[]
    finally:td.cleanup()
def family_feas_loss():
    td,m,c,w,t,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,c,w,t,dc);w['B']='REFUSED';n=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob());return n['status']=='ABSTAIN' and c==['A']
    finally:td.cleanup()
def family_priority_loss():
    td,m,c,w,t,dc=two_tick_fixture()
    try:
        _,_,_,t2=do_first(td,m,c,w,t,dc);m.observe_value_state('V',5.0);n=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob());return n['status']=='ABSTAIN' and c==['A']
    finally:td.cleanup()
def family_voi_after_actual():
    td,m,c,w,t,_=fixture()
    try:
        h1=(r('s0','A','s1',2),r('s0','B','bx',0),r('s1','B','s2',0),r('sx','A','ax',2),r('sx','B','same',0));h2=(r('s0','A','s1',0),r('s0','B','bx',2),r('s1','B','s3',0),r('sx','A','ax',0),r('sx','B','same',2));dc=EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
        n=m.nominate_endogenous_epistemic_program_step_intent(t,dc,'FEAS-A',fob('A'),act_ob());ec=EpistemicStepExecutionContext(t,feasibility_capability_id='FEAS-A',feasibility_obligation=fob('A'),decision_context=dc);ex=m.execute_bounded_action(n['intent']['intent_id'],act_ob(),epistemic_step_context=ec);x=ex['execution']['execution_id'];obs=Observation('OX','EXT',f'action-execution:{x}',{'next_state_id':'sx'},authority=Authority.OBSERVATION_ONLY);out=m.record_bounded_action_outcome(x,obs,evidence_id='EX');t2=advance_epistemic_program_trial(t,intent=m.action_closure.intents[n['intent']['intent_id']],execution=m.action_closure.executions[x],outcome=m.action_closure.outcomes[out['outcome']['outcome_id']],capabilities=m.capabilities,current_frame_epochs=dict(m.frames.epochs));n2=m.nominate_endogenous_epistemic_program_step_intent(t2,dc,'FEAS-B',fob('B'),act_ob());return n2['status']=='ABSTAIN' and n2['information']['commitment']=='NO' and c==['A']
    finally:td.cleanup()
def family_forged_complete():
    td,m,c,w,t,dc=two_tick_fixture()
    try:
        done=complete_trial(m,t,dc);bad=replace(done,step_records=(replace(done.step_records[0],actual_next_state_id='FORGED'),)+done.step_records[1:]);q=m.record_completed_epistemic_program_evidence(bad,evidence_id='EF');return q['status']=='PROGRAM_EVIDENCE_REJECTED' and m.epistemic_deficits.records['D'].state.value=='ACTION_LIMITED'
    finally:td.cleanup()

families={'lawful_two_tick':family_lawful,'nondiscriminating_abstain':family_nondisc,'second_step_feasibility_loss':family_feas_loss,'second_step_priority_loss':family_priority_loss,'actual_outcome_voi_collapse':family_voi_after_actual,'forged_complete_evidence':family_forged_complete}
N=16;results={}
for name,fn in families.items():
    ok=sum(1 for _ in range(N) if fn());results[name]={'pass':ok,'total':N};assert ok==N,(name,ok)
out={'pass':'MS1720','families':results,'worlds':N*len(families),'disposition':'6_FAMILIES_ALL_EXPECTED'}
Path('research/MS1720_PASS18_ENDOGENOUS_EPISODE_BREADTH.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(out)
