from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, fob, act_ob
from microseed.development.epistemic_action import EpistemicDecisionBearingContext
from microseed.development.rehearsal import RehearsalTransitionRelation

def r(state,cap,next_state,effect):
    return RehearsalTransitionRelation(state,cap,next_state,effect,8,1.0,(f'E-{state}-{cap}-{effect}',),0,('F',0),('EP',0))

td,m,calls,world,trial,_=fixture()
try:
    # Decision-bearing: h1 would regulate with A, h2 with B at s0.
    # But the candidate program A->B predicts the same observable state trace in both.
    h1=(r('s0','A','s1',2.0),r('s0','B','bx',0.0),r('s1','B','s2',0.0))
    h2=(r('s0','A','s1',0.0),r('s0','B','bx',2.0),r('s1','B','s2',0.0))
    dc=EpistemicDecisionBearingContext((h1,h2),(('A','FEAS-A',fob('A')),('B','FEAS-B',fob('B'))))
    traces=[]
    for rows in dc.relation_sets:
        rels={(x.state_id,x.capability_id):x for x in rows}; state='s0'; trace=[]
        for action in trial.steps:
            x=rels[(state,action)]; state=x.next_state_id; trace.append(state)
        traces.append(tuple(trace))
    assert traces[0]==traces[1]==('s1','s2'),traces
    n=m.nominate_endogenous_epistemic_program_step_intent(trial,dc,'FEAS-A',fob('A'),act_ob())
    assert n['status']=='ACTION_INTENT_NOMINATED',n
    print({'pass':'MS1714','predicted_program_traces':traces,'false_initiation':n['status'],'scar':'DECISION_BEARING_UNKNOWN_PLUS_FEASIBLE_PROGRAM != INFORMATIVE_PROGRAM'})
finally: td.cleanup()
