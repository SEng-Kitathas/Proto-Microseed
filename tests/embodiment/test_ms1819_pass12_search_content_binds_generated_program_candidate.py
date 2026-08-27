from dataclasses import replace
from microseed.development.epistemic_action import EpistemicDecisionBearingContext, derive_current_generated_epistemic_program_candidates
from microseed.development.rehearsal import RehearsalTransitionRelation
from microseed.runtime.capabilities import CapabilityRegistry
from microseed.runtime.types import Authority, CapabilityContract, QualificationState, QueryObligation


def cap(cid):
    return CapabilityContract(cid,'opaque',{}, {},(),(),Authority.EFFECT,('MS1819',),'CURRENT',{},
        query_obligation_id='Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:None,operational_scope_id='S')


def rel(s,a,n,e):
    return RehearsalTransitionRelation(state_id=s,capability_id=a,next_state_id=n,value_effect=0.0,support=2,consistency=1.0,
        source_evidence_ids=(e,),capability_epoch=0,frame_epoch=('F',0),episode_schema_epoch=('EP',0),value_epoch=('V',0))


def fixture(last_evidence='E-C0'):
    reg=CapabilityRegistry()
    for cid in ('A','B','C'): reg.register(cap(cid))
    common=(rel('S0','A','S1','E-A'),rel('S1','B','S2','E-B'))
    dc=EpistemicDecisionBearingContext((common+(rel('S2','C','P',last_evidence),),common+(rel('S2','C','Q','E-C1'),)),())
    ob=QueryObligation('Q','probe',required_authority=Authority.EFFECT,operational_scope_id='S')
    return reg,dc,ob


def test_search_itself_generates_content_bound_zero_authority_candidate():
    reg,dc,ob=fixture()
    out=derive_current_generated_epistemic_program_candidates(decision_context=dc,start_state_id='S0',capabilities=reg,obligation=ob)
    c=[x for x in out['candidates'] if x.steps==('A','B','C')][0]
    expected={r.digest() for rows in dc.relation_sets for r in rows}
    assert set(c.source_relation_digests)==expected
    assert c.candidate_id=='generated-epistemic-program-'+c.digest()[:20]
    assert c.proposal_authority==c.truth_authority==c.execution_authority==c.closure_authority=='NONE'


def test_relation_content_change_changes_generated_candidate_identity_without_changing_program_word():
    reg,dc,ob=fixture('E-C0')
    a=derive_current_generated_epistemic_program_candidates(decision_context=dc,start_state_id='S0',capabilities=reg,obligation=ob)['candidates'][0]
    reg2,dc2,ob2=fixture('E-C0-CHANGED')
    b=derive_current_generated_epistemic_program_candidates(decision_context=dc2,start_state_id='S0',capabilities=reg2,obligation=ob2)['candidates'][0]
    assert a.steps==b.steps==('A','B','C')
    assert a.digest()!=b.digest() and a.candidate_id!=b.candidate_id
