from microseed.development.epistemic_action import EpistemicDecisionBearingContext, search_current_represented_discriminating_programs
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation


def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1815',),'CURRENT',{},
        query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:None,operational_scope_id='S')


def rel(s,a,n):
    return RehearsalTransitionRelation(state_id=s,capability_id=a,next_state_id=n,value_effect=0.0,
        support=2,consistency=1.0,source_evidence_ids=(f'E-{s}-{a}-{n}',),capability_epoch=0,
        frame_epoch=('F',0),episode_schema_epoch=('EP',0),value_epoch=('V',0))


def test_missing_relation_for_current_effect_generator_blocks_represented_fixpoint_claim():
    reg=CapabilityRegistry(); reg.register(cap('A')); reg.register(cap('B'))
    ob=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')
    rows=(rel('S0','A','S0'),)  # B is a current EFFECT generator but is unrepresented here.
    out=search_current_represented_discriminating_programs(
        decision_context=EpistemicDecisionBearingContext((rows,rows),()), start_state_id='S0',
        capabilities=reg, obligation=ob,
    )
    assert out['unresolved_edges']>0
    assert out['status']=='REPRESENTED_REACHABILITY_INCOMPLETE'
    assert out['closure_authority']=='NONE'
