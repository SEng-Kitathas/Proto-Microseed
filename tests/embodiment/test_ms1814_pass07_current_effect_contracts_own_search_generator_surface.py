from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, derive_current_epistemic_effect_action_tokens,
    search_current_represented_discriminating_programs,
)
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation


def cap(cid, *, scope='S', q='Q', current='CURRENT', authority=Authority.EFFECT):
    return CapabilityContract(cid,'opaque',{}, {},(),(),authority,('MS1814',),current,{},
        query_obligation_id=q,qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:None,operational_scope_id=scope)


def rel(s,a,n):
    return RehearsalTransitionRelation(state_id=s,capability_id=a,next_state_id=n,value_effect=0.0,
        support=2,consistency=1.0,source_evidence_ids=(f'E-{s}-{a}-{n}',),capability_epoch=0,
        frame_epoch=('F',0),episode_schema_epoch=('EP',0),value_epoch=('V',0))


def test_current_effect_contracts_supply_complete_search_alphabet_without_caller_token_list():
    reg=CapabilityRegistry()
    for cid in ('A','B','C'): reg.register(cap(cid))
    reg.register(cap('WRONG_SCOPE',scope='OTHER'))
    reg.register(cap('WRONG_QUERY',q='OTHERQ'))
    reg.register(cap('READ',authority=Authority.DERIVED_READ_ONLY))
    ob=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')
    assert derive_current_epistemic_effect_action_tokens(capabilities=reg,obligation=ob)==('A','B','C')
    common=(rel('S0','A','S1'),rel('S1','B','S2'))
    dc=EpistemicDecisionBearingContext((common+(rel('S2','C','P'),),common+(rel('S2','C','Q'),)),())
    out=search_current_represented_discriminating_programs(decision_context=dc,start_state_id='S0',capabilities=reg,obligation=ob)
    assert out['status']=='REPRESENTED_INFORMATIVE_PROGRAMS_FOUND'
    assert ('A','B','C') in out['programs']
    assert out['generator_tokens']==('A','B','C')
    assert out['generator_surface_authority']=='CURRENT_CAPABILITY_CONTRACTS_ONLY'
    assert out['truth_authority']==out['execution_authority']=='NONE'
