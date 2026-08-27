from microseed.development.epistemic_action import EpistemicDecisionBearingContext, search_represented_discriminating_programs
from microseed.development.rehearsal import RehearsalTransitionRelation


def rel(s,a,n):
    return RehearsalTransitionRelation(state_id=s, capability_id=a, next_state_id=n, value_effect=0.0,
        support=2, consistency=1.0, source_evidence_ids=(f'E-{s}-{a}-{n}',), capability_epoch=0,
        frame_epoch=('F',0), episode_schema_epoch=('EP',0), value_epoch=('V',0))


def test_fixpoint_search_finds_three_step_discriminator_without_depth_parameter():
    common=(rel('S0','A','S1'),rel('S1','B','S2'))
    dc=EpistemicDecisionBearingContext((common+(rel('S2','C','P'),), common+(rel('S2','C','Q'),)),())
    out=search_represented_discriminating_programs(decision_context=dc,start_state_id='S0',action_tokens=('A','B','C'))
    assert out['status']=='REPRESENTED_INFORMATIVE_PROGRAMS_FOUND'
    assert ('A','B','C') in out['programs']
    # Sparse rows can still supply a discriminating witness, but cannot prove
    # that every current action is represented/applicable at every reached state.
    assert out['search_complete'] is False
    assert out['closure_authority']=='NONE'
    assert out['truth_authority']==out['execution_authority']=='NONE'


def test_revisited_common_state_is_alias_not_longer_word_pressure():
    a0=(rel('S0','A','S0'),rel('S0','B','P'))
    a1=(rel('S0','A','S0'),rel('S0','B','Q'))
    out=search_represented_discriminating_programs(decision_context=EpistemicDecisionBearingContext((a0,a1),()),start_state_id='S0',action_tokens=('A','B'))
    assert out['programs']==(('B',),)
    assert ('A','B') not in out['programs']


def test_represented_fixpoint_is_not_physical_generated_affordance_saturation():
    rows=(rel('S0','A','S1'),rel('S1','A','S0'))
    out=search_represented_discriminating_programs(decision_context=EpistemicDecisionBearingContext((rows,rows),()),start_state_id='S0',action_tokens=('A',))
    assert out['status']=='REPRESENTED_REACHABILITY_FIXPOINT_NO_DISCRIMINATOR'
    assert out['closure_authority']=='REPRESENTED_QUERY_LOCAL_ONLY'
    assert 'AFFORDANCE' not in out['status'] and 'SATURATED' not in out['status']


def test_budget_exhaustion_cannot_launder_into_saturation():
    rows=(rel('S0','A','S1'),rel('S1','A','S2'),rel('S2','A','S3'))
    out=search_represented_discriminating_programs(decision_context=EpistemicDecisionBearingContext((rows,rows),()),start_state_id='S0',action_tokens=('A',),max_nodes=1)
    assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED'
    assert out['closure_authority']=='NONE'
