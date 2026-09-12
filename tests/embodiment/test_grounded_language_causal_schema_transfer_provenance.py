from pathlib import Path
import json
import tempfile

from microseed import RecruitmentOption,FeasibilityState,RehearsalTransitionObservation,Observation,Authority
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import _build
from tests.embodiment.test_ms1427_reconstructed_integration import setup,cap,obl,holdout_refs,ExternalActionOutcomeRelationQualifier
from tests.embodiment.test_grounded_language_concept_formation_provenance import _dataset
from scratch.grounded_language_concept_formation_prototype import derive_owned_language_mediated_concepts,grounded_relation_sequence_episode
from scratch.grounded_language_causal_composition_prototype import grounded_action_concept_observation,derive_owned_action_concept_couplings
from scratch.grounded_language_multistep_causal_composition_prototype import derive_owned_two_step_language_causal_chain
from scratch.grounded_language_causal_schema_transfer_prototype import (
    derive_owned_causal_schema,
    transfer_owned_schema_to_context,
    validate_schema_transfer_against_actual_holdout,
    inspect_owned_schema_without_language,
    attempt_text_only_schema,
)


def _close(td,ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close();td.cleanup()


def _proposal(ms,cid,start,prefix):
    rows=tuple(RehearsalTransitionObservation(f'{prefix}{i}',start,cid,'SX',9.0,0,'F',0,'E',0) for i in range(10))
    p=ms.nominate_counterfactual_rehearsal(rows,(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id=start,value_id='V')
    assert p is not None
    return p


def _set_state(ms,state,value,eid):
    ms.observe_value_state('V',float(value))
    ms.observe_opaque_control_state(Observation(f'{eid}-STATE','EXT','opaque-control',state,authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-{eid}-STATE')


def _execute(ms,p,eid,next_state,observed):
    intent=ms.nominate_bounded_action_intent(p.proposal_id,obl());assert intent['status']=='ACTION_INTENT_NOMINATED',intent
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],obl());assert ex['status']=='ACTION_EXECUTED',ex
    execution_id=ex['execution']['execution_id']
    out=ms.record_bounded_action_outcome(execution_id,Observation(f'{eid}-OUT','EXT',f'action-execution:{execution_id}',{'next_state_id':next_state,'value_id':'V','observed_value':float(observed)},authority=Authority.OBSERVATION_ONLY),evidence_id=f'E-{eid}-OUT')
    assert out['status']=='ACTION_OUTCOME_OBSERVED',out
    return out


def _token_for_pattern(cset,pattern):
    return next(c['surface_token'] for c in cset['concepts'] if tuple(c['grounded_concept_content']['relation_transform_permutation'])==tuple(pattern))


def _make_concept_set(ms,world,tokens,start,evidence_id):
    train,hold=_dataset(ms,world,tokens,start)
    c=derive_owned_language_mediated_concepts(ms,train,hold,evidence_id=evidence_id)
    assert c['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY',c
    return c,_token_for_pattern(c,(0,1)),_token_for_pattern(c,(1,0))


def _context(ms,world,*,name,cap1,cap2,s0,s1,s2,cset,stable,switch,start,first_effect=1.0,second_effect=1.0,second_start=None,make_chain=True):
    for cid in (cap1,cap2):
        if cid not in ms.capabilities.contracts: ms.register_capability(cap(cid))
    second_start=s1 if second_start is None else second_start
    outs1=[];outs2=[]
    for k in range(10):
        _set_state(ms,s0,0.0,f'{name}-A{k}');p1=_proposal(ms,cap1,s0,f'{name}-AP{k}-');outs1.append(_execute(ms,p1,f'{name}-A{k}',s1,first_effect))
    for k in range(10):
        _set_state(ms,second_start,0.0,f'{name}-B{k}');p2=_proposal(ms,cap2,second_start,f'{name}-BP{k}-');outs2.append(_execute(ms,p2,f'{name}-B{k}',s2,second_effect))
    candidates=ms.nominate_action_outcome_predictive_candidates(min_support=8,min_consistency=.78)
    selected=[c for c in candidates if c.capability_id in {cap1,cap2} and c.start_state_id in {s0,second_start}]
    assert len(selected)==2,[(c.capability_id,c.start_state_id,c.next_state_id,c.value_effect) for c in selected]
    rels=[]
    for j,c in enumerate(selected):
        refs=holdout_refs(ms,c,12,next_state=c.next_state_id,effect=c.value_effect,prefix=f'{name}-RQ{j}-')
        q=ms.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs));assert q['status']=='CURRENT_PREDICTIVE_RELATION'
        rels.append(q['relation'])
    r1=next(r for r in rels if r['capability_id']==cap1);r2=next(r for r in rels if r['capability_id']==cap2)
    train=[];hold=[]
    for i,o in enumerate(outs1[:6]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=stable,first_mode='PQ' if i%2==0 else 'QP',second_mode='PQ' if i%2==0 else 'QP',index=start+200+i)
        train.append(grounded_action_concept_observation(ms,relation_id=r1['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=stable,grounded_sequence_episode=seq))
    for i,o in enumerate(outs2[:6]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=switch,first_mode='PQ' if i%2==0 else 'QP',second_mode='QP' if i%2==0 else 'PQ',index=start+300+i)
        train.append(grounded_action_concept_observation(ms,relation_id=r2['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=switch,grounded_sequence_episode=seq))
    for i,o in enumerate(outs1[6:9]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=stable,first_mode='QP' if i%2==0 else 'PQ',second_mode='QP' if i%2==0 else 'PQ',index=start+400+i)
        hold.append(grounded_action_concept_observation(ms,relation_id=r1['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=stable,grounded_sequence_episode=seq))
    for i,o in enumerate(outs2[6:9]):
        seq=grounded_relation_sequence_episode(ms,world,surface_token=switch,first_mode='QP' if i%2==0 else 'PQ',second_mode='PQ' if i%2==0 else 'QP',index=start+500+i)
        hold.append(grounded_action_concept_observation(ms,relation_id=r2['relation_id'],action_outcome_evidence_id=o['outcome']['evidence_id'],concept_set=cset,surface_token=switch,grounded_sequence_episode=seq))
    coupling=derive_owned_action_concept_couplings(ms,train,hold,evidence_id=f'E-P06-{name}-COUPLING')
    assert coupling['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY',coupling
    chain=None
    if make_chain:
        chain=derive_owned_two_step_language_causal_chain(ms,coupling,first_relation_id=r1['relation_id'],second_relation_id=r2['relation_id'],evidence_id=f'E-P06-{name}-CHAIN')
        assert chain['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN_RESEARCH_ONLY',chain
    return {'coupling':coupling,'chain':chain,'r1':r1,'r2':r2,'stable':stable,'switch':switch,'cap1':cap1,'cap2':cap2,'s0':s0,'s1':s1,'s2':s2,'second_start':second_start,'first_effect':first_effect,'second_effect':second_effect}


def _actual_holdout(ms,ctx,index):
    _set_state(ms,ctx['s0'],0.0,f'H{index}-A');p1=_proposal(ms,ctx['cap1'],ctx['s0'],f'H{index}-AP-');o1=_execute(ms,p1,f'H{index}-A',ctx['s1'],ctx['first_effect'])
    _set_state(ms,ctx['second_start'],0.0,f'H{index}-B');p2=_proposal(ms,ctx['cap2'],ctx['second_start'],f'H{index}-BP-');o2=_execute(ms,p2,f'H{index}-B',ctx['s2'],ctx['second_effect'])
    return o1,o2


def _base_env(prefix='veya-p06-'):
    td=tempfile.TemporaryDirectory(prefix=prefix);ms,world=_build(Path(td.name));setup(ms)
    c1,stable1,switch1=_make_concept_set(ms,world,('steady','switch'),50000,'E-P06-CONCEPT-TRAIN')
    a=_context(ms,world,name='CTX-A',cap1='A',cap2='B',s0='S0',s1='S1',s2='S2',cset=c1,stable=stable1,switch=switch1,start=51000)
    b=_context(ms,world,name='CTX-B',cap1='C',cap2='D',s0='T0',s1='T1',s2='T2',cset=c1,stable=stable1,switch=switch1,start=53000)
    schema=derive_owned_causal_schema(ms,[a['chain'],b['chain']])
    return td,ms,world,c1,stable1,switch1,a,b,schema


def test_p06_schema_abstracts_two_disjoint_training_contexts_without_concrete_ids():
    td,ms,w,c,stable,switch,a,b,schema=_base_env()
    try:
        assert schema['status']=='OWNED_GROUNDED_LANGUAGE_MEDIATED_CAUSAL_SCHEMA_RESEARCH_ONLY',schema
        assert schema['training_context_count']==2 and schema['concrete_identifiers_excluded_from_schema_content'] is True
        abstract=schema['abstract_schema']
        assert abstract['edge_count']==2 and abstract['state_role_count']==3 and abstract['join_roles']==[[0,1],[1,2]]
        assert abstract['step_value_effect_signs']==[1,1]
        dumped=json.dumps(abstract,sort_keys=True)
        for concrete in ('S0','S1','S2','T0','T1','T2','"A"','"B"','"C"','"D"'):
            assert concrete not in dumped
        assert schema['ontology_authority']==schema['causal_theorem_authority']=='NONE'
    finally:_close(td,ms)


def test_p06_transfers_schema_to_heldout_context_with_surface_words_remapped_and_matches_actual_execution():
    td,ms,w,c,stable,switch,a,b,schema=_base_env('p06-transfer-')
    try:
        # New concept set has the same grounded concept contents but swapped word assignment.
        c2,stable2,switch2=_make_concept_set(ms,w,('switch','steady'),55000,'E-P06-CONCEPT-HOLDOUT')
        held=_context(ms,w,name='CTX-H',cap1='P6E',cap2='P6F',s0='U0',s1='U1',s2='U2',cset=c2,stable=stable2,switch=switch2,start=57000,make_chain=False)
        assert stable2=='switch' and switch2=='steady'
        transfer=transfer_owned_schema_to_context(ms,schema,held['coupling'],(stable2,switch2))
        assert transfer['status']=='CURRENT_GROUNDED_LANGUAGE_MEDIATED_SCHEMA_TRANSFER_RESEARCH_ONLY',transfer
        assert transfer['state_path']==['U0','U1','U2'] and transfer['capability_sequence']==['P6E','P6F']
        assert transfer['concrete_training_identifiers_used_for_matching'] is False
        o1,o2=_actual_holdout(ms,held,98000)
        val=validate_schema_transfer_against_actual_holdout(ms,transfer,o1['outcome']['evidence_id'],o2['outcome']['evidence_id'])
        assert val['status']=='SCHEMA_TRANSFER_HOLDOUT_MATCH' and val['matched'] is True,val
    finally:_close(td,ms)


def test_p06_structurally_incompatible_heldout_context_is_refused_not_forced_to_fit():
    td,ms,w,c,stable,switch,a,b,schema=_base_env('p06-badjoin-')
    try:
        held=_context(ms,w,name='CTX-X',cap1='G',cap2='H',s0='V0',s1='V1',s2='V2',second_start='V9',cset=c,stable=stable,switch=switch,start=59000,make_chain=False)
        out=transfer_owned_schema_to_context(ms,schema,held['coupling'],(stable,switch))
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_CONTEXT_STATE_JOIN_MISMATCH',out
    finally:_close(td,ms)


def test_p06_effect_role_mismatch_is_refused():
    td,ms,w,c,stable,switch,a,b,schema=_base_env('p06-effect-')
    try:
        held=_context(ms,w,name='CTX-N',cap1='I',cap2='J',s0='W0',s1='W1',s2='W2',cset=c,stable=stable,switch=switch,start=61000,first_effect=1.0,second_effect=-1.0,make_chain=False)
        out=transfer_owned_schema_to_context(ms,schema,held['coupling'],(stable,switch))
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_CONTEXT_EFFECT_ROLE_MISMATCH',out
    finally:_close(td,ms)


def test_p06_one_context_or_overlapping_contexts_cannot_claim_abstraction():
    td,ms,w,c,stable,switch,a,b,schema=_base_env('p06-one-')
    try:
        one=derive_owned_causal_schema(ms,[a['chain']],evidence_id='E-P06-ONE')
        assert one['status']=='DEFER_UNKNOWN' and one['reason']=='AT_LEAST_TWO_OWNED_CHAIN_CONTEXTS_REQUIRED'
        overlap=derive_owned_causal_schema(ms,[a['chain'],a['chain']],evidence_id='E-P06-OVERLAP')
        assert overlap['status']=='DEFER_UNKNOWN' and overlap['reason']=='TRAINING_CONTEXTS_MUST_BE_CONCRETELY_DISJOINT'
    finally:_close(td,ms)


def test_p06_text_only_schema_and_forged_schema_evidence_are_refused():
    assert attempt_text_only_schema('all steady then switch chains have a universal causal law')['status']=='DEFER_UNKNOWN'
    td,ms,w,c,stable,switch,a,b,schema=_base_env('p06-forge-')
    try:
        held=_context(ms,w,name='CTX-F',cap1='K',cap2='L',s0='X0',s1='X1',s2='X2',cset=c,stable=stable,switch=switch,start=63000,make_chain=False)
        forged=dict(schema);forged['schema_evidence_sha256']='0'*64
        out=transfer_owned_schema_to_context(ms,forged,held['coupling'],(stable,switch))
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='EXACT_OWNED_CAUSAL_SCHEMA_EVIDENCE_REQUIRED'
    finally:_close(td,ms)


def test_p06_heldout_relation_or_concept_drift_blocks_transfer_while_schema_content_remains_inspectable():
    for drift_kind,start in [('relation',65000),('concept',68000)]:
        td,ms,w,c,stable,switch,a,b,schema=_base_env(f'p06-drift-{drift_kind}-')
        try:
            held=_context(ms,w,name='CTX-D',cap1='M',cap2='N',s0='Y0',s1='Y1',s2='Y2',cset=c,stable=stable,switch=switch,start=start,make_chain=False)
            before=inspect_owned_schema_without_language(ms,schema);assert before['status']=='OWNED_CAUSAL_SCHEMA_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX'
            if drift_kind=='relation': ms.change_capability_dependency('M',reason='P06-RELATION-DRIFT')
            else: ms.change_capability_dependency('SIG-X',reason='P06-CONCEPT-DRIFT')
            out=transfer_owned_schema_to_context(ms,schema,held['coupling'],(stable,switch))
            assert out['status']=='DEFER_UNKNOWN',out
            after=inspect_owned_schema_without_language(ms,schema);assert after['status']==before['status']
        finally:_close(td,ms)
