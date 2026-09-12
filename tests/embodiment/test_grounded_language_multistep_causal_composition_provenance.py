from pathlib import Path
import tempfile

from microseed import RecruitmentOption,FeasibilityState,RehearsalTransitionObservation,Observation,Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build
from tests.embodiment.test_ms1427_reconstructed_integration import setup,cap,obl,holdout_refs,ExternalActionOutcomeRelationQualifier
from tests.embodiment.test_grounded_language_concept_formation_provenance import _dataset
from scratch.grounded_language_concept_formation_prototype import derive_owned_language_mediated_concepts,grounded_relation_sequence_episode
from scratch.grounded_language_causal_composition_prototype import grounded_action_concept_observation,derive_owned_action_concept_couplings
from scratch.grounded_language_multistep_causal_composition_prototype import (
    derive_owned_two_step_language_causal_chain,
    compose_owned_chain_with_language,
    evaluate_counterfactual_language_sequence,
    validate_two_step_chain_against_actual_holdout,
    inspect_owned_chain_without_language,
    attempt_text_only_multistep_causal_chain,
)


def _close(td,ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def _proposal(ms,cid,start,pred,prefix):
    rows=tuple(RehearsalTransitionObservation(f'{prefix}{i}',start,cid,pred,9.0,0,'F',0,'E',0) for i in range(10))
    p=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id=start,value_id='V')
    assert p is not None
    return p


def _set_state(ms,state,value,index):
    ms.observe_value_state('V',float(value))
    ms.observe_opaque_control_state(Observation(f'P05-STATE-{index}','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-P05-STATE-{index}')


def _execute(ms,p,index,next_state,observed):
    intent=ms.nominate_bounded_action_intent(p.proposal_id,obl());assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl());assert ex['status']=='ACTION_EXECUTED',ex
    eid=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(eid,Observation(f'P05-OUT-{index}','EXT',f'action-execution:{eid}',{'next_state_id':next_state,'value_id':'V','observed_value':float(observed)},authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-P05-OUT-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def _token_for_pattern(cset,pattern):
    return next(c['surface_token'] for c in cset['concepts'] if tuple(c['grounded_concept_content']['relation_transform_permutation'])==tuple(pattern))


def _chain_env(prefix='veya-p05-',tokens=('steady','switch'),start=30000):
    td=tempfile.TemporaryDirectory(prefix=prefix);ms,world=_build(Path(td.name));setup(ms);ms.register_capability(cap('B'))
    tc,hc=_dataset(ms,world,tokens,start);cset=derive_owned_language_mediated_concepts(ms,tc,hc,evidence_id='E-P05-CONCEPT-SET')
    assert cset['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY'
    stable=_token_for_pattern(cset,(0,1));switch=_token_for_pattern(cset,(1,0))
    outs_a=[];outs_b=[]
    # Learn A and B separately: no executed A->B chain appears in training.
    for k in range(10):
        _set_state(ms,'S0',0.0,start+k);pa=_proposal(ms,'A','S0','SX',f'P05-A{k}-');outs_a.append(_execute(ms,pa,start+k,'S1',1.0))
    for k in range(10):
        _set_state(ms,'S1',1.0,start+100+k);pb=_proposal(ms,'B','S1','SY',f'P05-B{k}-');outs_b.append(_execute(ms,pb,start+100+k,'S2',2.0))
    cs=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78);rels=[]
    for j,c in enumerate(cs):
        refs=holdout_refs(ms,c,12,next_state=c.next_state_id,effect=c.value_effect,prefix=f'P05-RQ{j}-')
        q=ms.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs));assert q['status']=='CURRENT_PREDICTIVE_RELATION'
        rels.append(q['relation'])
    ra=next(r for r in rels if r['capability_id']=='A');rb=next(r for r in rels if r['capability_id']=='B')
    train=[];hold=[]
    for i,o in enumerate(outs_a[:6]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=stable,first_mode='PQ' if i%2==0 else 'QP',second_mode='PQ' if i%2==0 else 'QP',index=start+200+i)
        train.append(grounded_action_concept_observation(ms,relation_id=ra['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=stable,grounded_sequence_episode=seq))
    for i,o in enumerate(outs_b[:6]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=switch,first_mode='PQ' if i%2==0 else 'QP',second_mode='QP' if i%2==0 else 'PQ',index=start+300+i)
        train.append(grounded_action_concept_observation(ms,relation_id=rb['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=switch,grounded_sequence_episode=seq))
    for i,o in enumerate(outs_a[6:9]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=stable,first_mode='QP' if i%2==0 else 'PQ',second_mode='QP' if i%2==0 else 'PQ',index=start+400+i)
        hold.append(grounded_action_concept_observation(ms,relation_id=ra['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=stable,grounded_sequence_episode=seq))
    for i,o in enumerate(outs_b[6:9]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=switch,first_mode='QP' if i%2==0 else 'PQ',second_mode='PQ' if i%2==0 else 'QP',index=start+500+i)
        hold.append(grounded_action_concept_observation(ms,relation_id=rb['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=switch,grounded_sequence_episode=seq))
    coupling=derive_owned_action_concept_couplings(ms,train,hold,evidence_id='E-P05-COUPLING-SET')
    assert coupling['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY',coupling
    chain=derive_owned_two_step_language_causal_chain(ms,coupling,first_relation_id=ra['relation_id'],second_relation_id=rb['relation_id'])
    return td,ms,world,cset,coupling,chain,ra,rb,stable,switch


def _actual_chain_holdout(ms,start_index=90000,wrong_second=False):
    _set_state(ms,'S0',0.0,start_index);pa=_proposal(ms,'A','S0','SX',f'P05-HA{start_index}-');oa=_execute(ms,pa,start_index,'S1',1.0)
    pb=_proposal(ms,'B','S1','SY',f'P05-HB{start_index}-');ob=_execute(ms,pb,start_index+1,'S3' if wrong_second else 'S2',2.0)
    return oa,ob


def test_p05_independently_learned_edges_compose_into_owned_two_step_chain_and_match_actual_heldout_execution():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env()
    try:
        assert chain['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN_RESEARCH_ONLY',chain
        assert chain['state_path']==['S0','S1','S2'] and chain['capability_sequence']==['A','B']
        assert chain['cumulative_value_effect']==2.0
        comp=compose_owned_chain_with_language(ms,chain,(stable,switch))
        assert comp['status']=='CURRENT_OWNED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_COMPOSITION_RESEARCH_ONLY',comp
        oa,ob=_actual_chain_holdout(ms)
        val=validate_two_step_chain_against_actual_holdout(ms,comp,oa['outcome']['evidence_id'],ob['outcome']['evidence_id'])
        assert val['status']=='TWO_STEP_CHAIN_HOLDOUT_MATCH' and val['matched'] is True,val
        assert comp['causal_theorem_authority']==comp['planner_authority']==comp['execution_authority']=='NONE'
    finally:_close(td,ms)


def test_p05_counterfactual_language_order_can_be_infeasible_without_text_repairing_state_join():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-cf-',start=32000)
    try:
        valid=evaluate_counterfactual_language_sequence(ms,coupling,(stable,switch))
        assert valid['status']=='BOUNDED_COUNTERFACTUAL_LANGUAGE_CAUSAL_CHAIN_RESEARCH_ONLY',valid
        assert valid['state_path']==['S0','S1','S2']
        reversed_cf=evaluate_counterfactual_language_sequence(ms,coupling,(switch,stable))
        assert reversed_cf['status']=='COUNTERFACTUAL_CHAIN_INFEASIBLE_RESEARCH_ONLY',reversed_cf
        assert reversed_cf['reason']=='EMPIRICAL_STATE_JOIN_MISMATCH'
        assert reversed_cf['causal_theorem_authority']==reversed_cf['planner_authority']=='NONE'
    finally:_close(td,ms)


def test_p05_wrong_language_sequence_and_text_only_story_cannot_override_owned_chain():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-word-',start=34000)
    try:
        wrong=compose_owned_chain_with_language(ms,chain,(switch,stable))
        assert wrong['status']=='DEFER_UNKNOWN' and wrong['reason']=='LANGUAGE_CONCEPT_SEQUENCE_DISAGREES_WITH_OWNED_CAUSAL_CHAIN'
        for text in ('A then B because Veya says so','the operator commands S0 to cause S2','a good agent should infer the missing middle state'):
            out=attempt_text_only_multistep_causal_chain(text)
            assert out['status']=='DEFER_UNKNOWN' and out['reason']=='OWNED_CURRENT_EMPIRICAL_RELATIONS_AND_OWNED_CAUSAL_CHAIN_REQUIRED'
    finally:_close(td,ms)


def test_p05_broken_empirical_state_join_is_refused_at_chain_derivation():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-join-',start=36000)
    try:
        reversed_chain=derive_owned_two_step_language_causal_chain(ms,coupling,first_relation_id=rb['relation_id'],second_relation_id=ra['relation_id'],evidence_id='E-P05-BAD-JOIN')
        assert reversed_chain['status']=='DEFER_UNKNOWN' and reversed_chain['reason']=='EMPIRICAL_RELATION_STATE_JOIN_REQUIRED',reversed_chain
    finally:_close(td,ms)


def test_p05_relation_drift_on_either_edge_blocks_chain_use_without_erasing_owned_chain():
    for cid,token_index,start in [('A',0,38000),('B',1,40000)]:
        td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env(f'p05-drift-{cid}-',start=start)
        try:
            before=inspect_owned_chain_without_language(ms,chain);assert before['status']=='OWNED_TWO_STEP_CAUSAL_CHAIN_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX'
            ms.change_capability_dependency(cid,reason=f'P05-{cid}-DRIFT')
            stale=compose_owned_chain_with_language(ms,chain,(stable,switch))
            assert stale['status']=='DEFER_UNKNOWN' and stale['reason']=='CURRENT_ACTION_OUTCOME_PREDICTIVE_RELATION_REQUIRED',stale
            after=inspect_owned_chain_without_language(ms,chain);assert after['status']==before['status']
        finally:_close(td,ms)


def test_p05_concept_grounding_drift_blocks_chain_language_use_without_erasing_chain_content():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-concept-drift-',start=42000)
    try:
        ms.change_capability_dependency('SIG-X',reason='P05-CONCEPT-DRIFT')
        stale=compose_owned_chain_with_language(ms,chain,(stable,switch))
        assert stale['status']=='DEFER_UNKNOWN' and stale['reason']=='CONCEPT_GROUNDING_DEPENDENCY_DRIFT_REVALIDATION_REQUIRED',stale
        no_language=inspect_owned_chain_without_language(ms,chain)
        assert no_language['status']=='OWNED_TWO_STEP_CAUSAL_CHAIN_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX'
    finally:_close(td,ms)


def test_p05_forged_chain_evidence_is_refused_and_actual_holdout_violation_is_not_narratively_repaired():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-forge-',start=44000)
    try:
        forged=dict(chain);forged['chain_evidence_sha256']='0'*64
        out=compose_owned_chain_with_language(ms,forged,(stable,switch))
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='EXACT_OWNED_TWO_STEP_CHAIN_EVIDENCE_REQUIRED'
        comp=compose_owned_chain_with_language(ms,chain,(stable,switch))
        oa,ob=_actual_chain_holdout(ms,start_index=99000,wrong_second=True)
        val=validate_two_step_chain_against_actual_holdout(ms,comp,oa['outcome']['evidence_id'],ob['outcome']['evidence_id'])
        assert val['status']=='TWO_STEP_CHAIN_HOLDOUT_VIOLATION' and val['matched'] is False,val
    finally:_close(td,ms)


def test_p05_language_disabled_ablation_removes_lexical_use_not_owned_chain_content():
    td,ms,w,cset,coupling,chain,ra,rb,stable,switch=_chain_env('p05-ablate-',start=46000)
    try:
        lexical=compose_owned_chain_with_language(ms,chain,(stable,switch));assert lexical['status']=='CURRENT_OWNED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_COMPOSITION_RESEARCH_ONLY'
        no_language=inspect_owned_chain_without_language(ms,chain)
        assert no_language['status']=='OWNED_TWO_STEP_CAUSAL_CHAIN_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX'
        assert no_language['lexical_retrieval_available'] is False
        assert no_language['state_path']==['S0','S1','S2'] and no_language['cumulative_value_effect']==2.0
    finally:_close(td,ms)
