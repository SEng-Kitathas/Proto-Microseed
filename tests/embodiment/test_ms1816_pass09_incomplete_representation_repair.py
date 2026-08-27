from microseed.development.epistemic_action import EpistemicDecisionBearingContext, search_current_represented_discriminating_programs
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation


def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1816',),'CURRENT',{},
        query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:None,operational_scope_id='S')


def rel(s,a,n):
    return RehearsalTransitionRelation(state_id=s,capability_id=a,next_state_id=n,value_effect=0.0,
        support=2,consistency=1.0,source_evidence_ids=(f'E-{s}-{a}-{n}',),capability_epoch=0,
        frame_epoch=('F',0),episode_schema_epoch=('EP',0),value_epoch=('V',0))


def fixture(actions=('A','B')):
    reg=CapabilityRegistry()
    for a in actions: reg.register(cap(a))
    return reg,QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')


def test_missing_current_generator_edge_is_incomplete_not_fixpoint():
    reg,ob=fixture(); rows=(rel('S0','A','S0'),)
    out=search_current_represented_discriminating_programs(decision_context=EpistemicDecisionBearingContext((rows,rows),()),start_state_id='S0',capabilities=reg,obligation=ob)
    assert out['status']=='REPRESENTED_REACHABILITY_INCOMPLETE'
    assert out['search_complete'] is False and out['closure_authority']=='NONE'


def test_found_witness_can_survive_other_unrepresented_edges_without_completeness_claim():
    reg,ob=fixture(('A','B','C'))
    a0=(rel('S0','A','P'),); a1=(rel('S0','A','Q'),)  # B/C unrepresented but A already discriminates.
    out=search_current_represented_discriminating_programs(decision_context=EpistemicDecisionBearingContext((a0,a1),()),start_state_id='S0',capabilities=reg,obligation=ob)
    assert ('A',) in out['programs']
    assert out['status']=='REPRESENTED_INFORMATIVE_PROGRAMS_FOUND'
    assert out['search_complete'] is False and out['closure_authority']=='NONE'
