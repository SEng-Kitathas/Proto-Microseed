from __future__ import annotations

from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_language_concept_formation_prototype import resolve_owned_concept
from scratch.grounded_language_causal_composition_prototype import NONE,_sha,_current_relation


def _sign(v:float)->int:
    return 1 if float(v)>0 else (-1 if float(v)<0 else 0)


def _owned_chain(ms,chain:dict[str,Any])->tuple[dict[str,Any]|None,dict[str,Any]|None]:
    if chain.get('status')!='OWNED_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN_RESEARCH_ONLY':
        return None,{**NONE,'status':'DEFER_UNKNOWN','reason':'OWNED_TWO_STEP_CAUSAL_CHAIN_REQUIRED'}
    row=ms.evidence.get(str(chain.get('chain_evidence_id','')))
    if row is None or row.get('sha256')!=chain.get('chain_evidence_sha256') or row.get('payload',{}).get('chain_id')!=chain.get('chain_id'):
        return None,{**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_TWO_STEP_CHAIN_EVIDENCE_REQUIRED'}
    return dict(row['payload']),None


def derive_owned_causal_schema(ms,training_chains:list[dict[str,Any]],*,evidence_id:str='E-VEYA-P06-CAUSAL-SCHEMA')->dict[str,Any]:
    if len(training_chains)<2:
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'AT_LEAST_TWO_OWNED_CHAIN_CONTEXTS_REQUIRED'}
    payloads=[]
    for chain in training_chains:
        p,err=_owned_chain(ms,chain)
        if err:return err
        payloads.append(p)
    # Require genuinely distinct concrete contexts so a single memorized path cannot masquerade as abstraction.
    cap_sets=[set(p['capability_sequence']) for p in payloads]
    state_sets=[set(p['state_path']) for p in payloads]
    for i in range(len(payloads)):
        for j in range(i+1,len(payloads)):
            if cap_sets[i]&cap_sets[j] or state_sets[i]&state_sets[j]:
                return {**NONE,'status':'DEFER_UNKNOWN','reason':'TRAINING_CONTEXTS_MUST_BE_CONCRETELY_DISJOINT'}
    concept_sequences={tuple(p['concept_content_digest_sequence']) for p in payloads}
    effect_signs={tuple(_sign(x) for x in p['step_value_effects']) for p in payloads}
    if len(concept_sequences)!=1:
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'NO_SHARED_CONCEPT_ROLE_SEQUENCE_ACROSS_CONTEXTS'}
    if len(effect_signs)!=1:
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'NO_SHARED_EFFECT_SIGN_SCHEMA_ACROSS_CONTEXTS'}
    # Structural topology is checked from evidence, then concrete names are deliberately omitted from schema content.
    for p in payloads:
        if len(p['relation_ids'])!=2 or len(p['state_path'])!=3 or len(p['capability_sequence'])!=2:
            return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_TWO_EDGE_CHAIN_TOPOLOGY_REQUIRED'}
        if p.get('causal_theorem_authority')!='NONE' or p.get('planner_authority')!='NONE' or p.get('execution_authority')!='NONE':
            return {**NONE,'status':'DEFER_UNKNOWN','reason':'TRAINING_CHAIN_AUTHORITY_OVERCLAIM'}
    abstract={
        'schema_kind':'TWO_EDGE_JOINED_EMPIRICAL_CAUSAL_ROLE_SCHEMA',
        'edge_count':2,
        'state_role_count':3,
        'join_roles':[[0,1],[1,2]],
        'concept_content_digest_sequence':list(next(iter(concept_sequences))),
        'step_value_effect_signs':list(next(iter(effect_signs))),
        'transfer_scope':'CURRENT_OWNED_ACTION_CONCEPT_COUPLINGS_WITH_EXACT_ROLE_MATCH_ONLY',
    }
    durable={
        'kind':'OWNED_VEYA_GROUNDED_LANGUAGE_MEDIATED_CAUSAL_SCHEMA',
        'schema_id':'VEYA-P06-SCHEMA-'+_sha(abstract)[:24],
        'abstract_schema':abstract,
        'training_chain_evidence_refs':[[p['chain_id'],training_chains[i]['chain_evidence_id'],training_chains[i]['chain_evidence_sha256']] for i,p in enumerate(payloads)],
        'training_context_count':len(payloads),
        'concrete_identifiers_excluded_from_schema_content':True,
        'ontology_authority':'NONE',
        'causal_theorem_authority':'NONE',
        'general_causal_learner_authority':'NONE',
        'planner_authority':'NONE',
        'execution_authority':'NONE',
        'truth_authority':'NONE',
        'external_oracle_authority':'NONE',
        'authority_gain':'NONE',
    }
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,durable,EpistemicStatus.PRESSURE_SUPPORTED,source='VEYA-P06-GROUNDED-LANGUAGE-CAUSAL-SCHEMA')
        sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=durable:
            return {**NONE,'status':'DEFER_UNKNOWN','reason':'CAUSAL_SCHEMA_EVIDENCE_ID_COLLISION'}
        sha=str(existing.get('sha256',''))
    return {**NONE,'status':'OWNED_GROUNDED_LANGUAGE_MEDIATED_CAUSAL_SCHEMA_RESEARCH_ONLY','schema_id':durable['schema_id'],'schema_evidence_id':evidence_id,'schema_evidence_sha256':sha,'abstract_schema':abstract,'training_context_count':len(payloads),'concrete_identifiers_excluded_from_schema_content':True,'ontology_authority':'NONE'}


def transfer_owned_schema_to_context(ms,schema:dict[str,Any],coupling_set:dict[str,Any],surface_tokens:tuple[str,str])->dict[str,Any]:
    if schema.get('status')!='OWNED_GROUNDED_LANGUAGE_MEDIATED_CAUSAL_SCHEMA_RESEARCH_ONLY':
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'OWNED_CAUSAL_SCHEMA_REQUIRED'}
    srow=ms.evidence.get(str(schema.get('schema_evidence_id','')))
    if srow is None or srow.get('sha256')!=schema.get('schema_evidence_sha256') or srow.get('payload',{}).get('schema_id')!=schema.get('schema_id'):
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_CAUSAL_SCHEMA_EVIDENCE_REQUIRED'}
    if coupling_set.get('status')!='OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY':
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'OWNED_ACTION_CONCEPT_COUPLING_SET_REQUIRED'}
    crow=ms.evidence.get(str(coupling_set.get('coupling_evidence_id','')))
    if crow is None or crow.get('sha256')!=coupling_set.get('coupling_evidence_sha256') or crow.get('payload',{}).get('coupling_set_id')!=coupling_set.get('coupling_set_id'):
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_ACTION_CONCEPT_COUPLING_EVIDENCE_REQUIRED'}
    cp=dict(crow['payload']);ap=dict(srow['payload']['abstract_schema'])
    if len(surface_tokens)!=2:return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_TWO_LANGUAGE_CONCEPT_INDICES_REQUIRED'}
    cset={'status':'OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY','concept_set_id':cp['concept_set_id'],'concept_evidence_id':cp['concept_evidence_id'],'concept_evidence_sha256':cp['concept_evidence_sha256']}
    resolved=[]
    for token in surface_tokens:
        c=resolve_owned_concept(ms,cset,str(token))
        if c.get('status')!='OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY':return {**NONE,**c,'status':'DEFER_UNKNOWN'}
        resolved.append(c)
    digests=[c['concept_content_digest_sha256'] for c in resolved]
    if digests!=list(ap['concept_content_digest_sequence']):
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'HELDOUT_LANGUAGE_CONCEPT_SEQUENCE_DISAGREES_WITH_SCHEMA'}
    selected=[]
    for digest in digests:
        m=[x for x in cp['couplings'] if x['concept_content_digest_sha256']==digest]
        if len(m)!=1:return {**NONE,'status':'DEFER_UNKNOWN','reason':'SCHEMA_ROLE_DOES_NOT_UNIQUELY_MAP_TO_HELDOUT_COUPLING'}
        selected.append(m[0])
    relations=[]
    for c in selected:
        r,status=_current_relation(ms,c['relation_id'])
        if r is None:return status
        if _sha(r)!=c['relation_snapshot_sha256']:
            return {**NONE,'status':'DEFER_UNKNOWN','reason':'CURRENT_RELATION_SNAPSHOT_DISAGREES_WITH_HELDOUT_COUPLING'}
        relations.append(r)
    if relations[0]['next_state_id']!=relations[1]['start_state_id']:
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'HELDOUT_CONTEXT_STATE_JOIN_MISMATCH'}
    signs=[_sign(r['value_effect']) for r in relations]
    if signs!=list(ap['step_value_effect_signs']):
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'HELDOUT_CONTEXT_EFFECT_ROLE_MISMATCH','observed_effect_signs':signs,'schema_effect_signs':list(ap['step_value_effect_signs'])}
    return {**NONE,'status':'CURRENT_GROUNDED_LANGUAGE_MEDIATED_SCHEMA_TRANSFER_RESEARCH_ONLY','schema_id':schema['schema_id'],'coupling_set_id':coupling_set['coupling_set_id'],'surface_tokens':list(surface_tokens),'relation_ids':[r['relation_id'] for r in relations],'capability_sequence':[r['capability_id'] for r in relations],'state_path':[relations[0]['start_state_id'],relations[0]['next_state_id'],relations[1]['next_state_id']],'step_value_effects':[float(r['value_effect']) for r in relations],'cumulative_value_effect':round(float(relations[0]['value_effect'])+float(relations[1]['value_effect']),6),'concept_content_digest_sequence':digests,'transfer_basis':'OWNED_ABSTRACT_SCHEMA_PLUS_CURRENT_HELDOUT_ACTION_CONCEPT_COUPLINGS','transfer_scope':ap['transfer_scope'],'concrete_training_identifiers_used_for_matching':False,'ontology_authority':'NONE'}


def validate_schema_transfer_against_actual_holdout(ms,transfer:dict[str,Any],first_outcome_evidence_id:str,second_outcome_evidence_id:str)->dict[str,Any]:
    if transfer.get('status')!='CURRENT_GROUNDED_LANGUAGE_MEDIATED_SCHEMA_TRANSFER_RESEARCH_ONLY':return {**NONE,'status':'DEFER_UNKNOWN','reason':'CURRENT_SCHEMA_TRANSFER_REQUIRED'}
    rows=[]
    for eid in (first_outcome_evidence_id,second_outcome_evidence_id):
        r=ms.evidence.get(str(eid))
        if r is None or r.get('negative'):return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_POSITIVE_TRANSFER_HOLDOUT_EVIDENCE_REQUIRED'}
        rows.append(r)
    p1,p2=(dict(r.get('payload') or {}) for r in rows)
    path=[str(p1.get('start_state_id')),str(p1.get('next_state_id')),str(p2.get('next_state_id'))]
    caps=[str(p1.get('capability_id')),str(p2.get('capability_id'))]
    effect=round(float(p1.get('actual_value_effect'))+float(p2.get('actual_value_effect')),6)
    joined=str(p1.get('next_state_id'))==str(p2.get('start_state_id'))
    matched=joined and path==list(transfer['state_path']) and caps==list(transfer['capability_sequence']) and effect==round(float(transfer['cumulative_value_effect']),6)
    return {**NONE,'status':'SCHEMA_TRANSFER_HOLDOUT_MATCH' if matched else 'SCHEMA_TRANSFER_HOLDOUT_VIOLATION','matched':matched,'predicted_state_path':list(transfer['state_path']),'observed_state_path':path,'predicted_capability_sequence':list(transfer['capability_sequence']),'observed_capability_sequence':caps,'predicted_cumulative_value_effect':transfer['cumulative_value_effect'],'observed_cumulative_value_effect':effect,'joined':joined}


def inspect_owned_schema_without_language(ms,schema:dict[str,Any])->dict[str,Any]:
    row=ms.evidence.get(str(schema.get('schema_evidence_id','')))
    if row is None or row.get('sha256')!=schema.get('schema_evidence_sha256'):
        return {**NONE,'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_CAUSAL_SCHEMA_EVIDENCE_REQUIRED'}
    return {**NONE,'status':'OWNED_CAUSAL_SCHEMA_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX','abstract_schema':dict(row['payload']['abstract_schema']),'lexical_retrieval_available':False}


def attempt_text_only_schema(text:str)->dict[str,Any]:
    return {**NONE,'status':'DEFER_UNKNOWN','reason':'MULTIPLE_OWNED_GROUNDED_CHAIN_CONTEXTS_REQUIRED','surface_text':str(text)}
