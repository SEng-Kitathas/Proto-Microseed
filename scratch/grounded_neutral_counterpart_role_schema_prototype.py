from __future__ import annotations
import hashlib,json
from typing import Any
from microseed import EpistemicStatus
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model

SOURCE='VEYA-CLEAN-NEUTRAL-COUNTERPART-ROLE-SCHEMA'
KIND='OWNED_VEYA_NEUTRAL_COUNTERPART_ROLE_SCHEMA'
ROLE='RECURRENT_NAMED_CONVERSATIONAL_COUNTERPART_ROLE'

def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def _role_signature(model:dict[str,Any])->dict[str,Any]|None:
    if model.get('status')!='OWNED_NEUTRAL_COUNTERPART_MODEL_RECORDED_RESEARCH_ONLY': return None
    f=model.get('facets',{})
    name=f.get('call_name_preference'); recur=f.get('recurrent_interaction'); latest=f.get('latest_observed_episode')
    if not name or not recur or not latest: return None
    return {
      'has_current_call_name_preference':True,
      'has_recurrent_interaction':True,
      'has_latest_owned_episode':True,
      'minimum_distinct_session_count_satisfied':int(recur.get('distinct_session_count',0))>=2,
      'all_unearned_social_fields_unknown':all(v=='UNKNOWN_NOT_EARNED' for v in model.get('explicit_unknowns',{}).values()),
    }

def derive_neutral_counterpart_role_schema(ms,training_models:list[dict[str,Any]],*,evidence_id:str='E-VEYA-M05-ROLE-SCHEMA')->dict[str,Any]:
    if len(training_models)<2:
        return {'status':'DEFER_UNKNOWN','reason':'AT_LEAST_TWO_DISTINCT_COUNTERPART_MODELS_REQUIRED','role_authority':'NONE'}
    ids=[(str(m.get('counterpart_id')),int(m.get('counterpart_epoch',-1))) for m in training_models]
    if len(set(ids))!=len(ids):
        return {'status':'DEFER_UNKNOWN','reason':'DISTINCT_COUNTERPART_CONTEXTS_REQUIRED','role_authority':'NONE'}
    sigs=[_role_signature(m) for m in training_models]
    if any(s is None for s in sigs):
        return {'status':'DEFER_UNKNOWN','reason':'FULL_NEUTRAL_COUNTERPART_MODEL_REQUIRED','role_authority':'NONE'}
    if len({_sha(s) for s in sigs})!=1:
        return {'status':'DEFER_UNKNOWN','reason':'NO_SHARED_NEUTRAL_COUNTERPART_ROLE_STRUCTURE','role_authority':'NONE'}
    abstract={
      'role':ROLE,
      'required_facets':['call_name_preference','recurrent_interaction','latest_observed_episode'],
      'required_min_distinct_sessions':2,
      'requires_all_unearned_social_fields_unknown':True,
      'concrete_counterpart_ids_excluded':True,
    }
    payload={
      'kind':KIND,'schema_id':'VEYA-M05-ROLE-'+_sha(abstract)[:24],'abstract_role':abstract,
      'training_counterpart_count':len(training_models),
      'training_model_evidence_refs':[[m['evidence_id'],m['evidence_sha256']] for m in training_models],
      'human_identity_truth_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','authority_gain':'NONE'}
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE);sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'ROLE_SCHEMA_EVIDENCE_ID_COLLISION','role_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY','schema_id':payload['schema_id'],'schema_evidence_id':evidence_id,'schema_evidence_sha256':sha,'abstract_role':abstract,'training_counterpart_count':len(training_models),'human_identity_truth_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE'}

def transfer_neutral_counterpart_role_schema(ms,schema:dict[str,Any],*,counterpart_id:str,counterpart_epoch:int)->dict[str,Any]:
    if schema.get('status')!='OWNED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY':
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_REQUIRED','role_authority':'NONE'}
    row=ms.evidence.get(str(schema.get('schema_evidence_id','')))
    if row is None or row.get('sha256')!=schema.get('schema_evidence_sha256') or row.get('source')!=SOURCE:
        return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_ROLE_SCHEMA_EVIDENCE_REQUIRED','role_authority':'NONE'}
    model=derive_neutral_counterpart_model(ms,counterpart_id=counterpart_id,counterpart_epoch=counterpart_epoch)
    sig=_role_signature(model)
    if sig is None:
        return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_COUNTERPART_DOES_NOT_SATISFY_NEUTRAL_ROLE','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'friendship_authority':'NONE'}
    if not sig.get('all_unearned_social_fields_unknown'):
        return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_MODEL_CONTAINS_UNEARNED_SOCIAL_PRELOAD','friendship_authority':'NONE'}
    return {'status':'CURRENT_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY','role':ROLE,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'model_evidence_id':model['evidence_id'],'model_evidence_sha256':model['evidence_sha256'],'preferred_call_name':model['facets']['call_name_preference']['preferred_call_name'],'distinct_session_count':model['facets']['recurrent_interaction']['distinct_session_count'],'human_identity_truth_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE'}
