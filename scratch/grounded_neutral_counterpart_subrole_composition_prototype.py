from __future__ import annotations
import hashlib,json
from typing import Any
from microseed import EpistemicStatus
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model

SOURCE='VEYA-CLEAN-NEUTRAL-COUNTERPART-SUBROLE-COMPOSITION'
SUBROLE_KIND='OWNED_VEYA_NEUTRAL_COUNTERPART_SUBROLE_SCHEMA'
COMPOSED_KIND='OWNED_VEYA_COMPOSED_NEUTRAL_COUNTERPART_ROLE_SCHEMA'
NAMED='CURRENT_NAMED_COUNTERPART_SUBROLE'
RECURRENT='RECURRENT_COUNTERPART_SUBROLE'
COMPOSED='COMPOSED_NAMED_RECURRENT_COUNTERPART_ROLE'

def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def _model_signature(model:dict[str,Any])->dict[str,bool]|None:
    if model.get('status')!='OWNED_NEUTRAL_COUNTERPART_MODEL_RECORDED_RESEARCH_ONLY': return None
    f=model.get('facets',{})
    return {
      'named':f.get('call_name_preference') is not None,
      'recurrent':f.get('recurrent_interaction') is not None,
      'episode':f.get('latest_observed_episode') is not None,
      'unknowns_preserved':all(v=='UNKNOWN_NOT_EARNED' for v in model.get('explicit_unknowns',{}).values()),
    }

def derive_neutral_subrole_schema(ms,training_models:list[dict[str,Any]],*,subrole:str,evidence_id:str)->dict[str,Any]:
    if subrole not in {NAMED,RECURRENT}:
        return {'status':'DEFER_UNKNOWN','reason':'UNSUPPORTED_NEUTRAL_SUBROLE','role_authority':'NONE'}
    if len(training_models)<2:
        return {'status':'DEFER_UNKNOWN','reason':'AT_LEAST_TWO_DISTINCT_COUNTERPART_MODELS_REQUIRED','role_authority':'NONE'}
    ids=[(str(m.get('counterpart_id')),int(m.get('counterpart_epoch',-1))) for m in training_models]
    if len(set(ids))!=len(ids):
        return {'status':'DEFER_UNKNOWN','reason':'DISTINCT_COUNTERPART_CONTEXTS_REQUIRED','role_authority':'NONE'}
    sigs=[_model_signature(m) for m in training_models]
    if any(s is None for s in sigs):
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_NEUTRAL_COUNTERPART_MODELS_REQUIRED','role_authority':'NONE'}
    if subrole==NAMED:
        # Sharp isolation: named cohort must not contain recurrence.
        if not all(s['named'] and s['episode'] and not s['recurrent'] and s['unknowns_preserved'] for s in sigs):
            return {'status':'DEFER_UNKNOWN','reason':'NAMED_SUBROLE_COHORT_NOT_ISOLATED','role_authority':'NONE'}
        required={'named':True,'recurrent':False,'episode':True}
    else:
        # Sharp isolation: recurrent cohort must not contain call-name preference.
        if not all(s['recurrent'] and s['episode'] and not s['named'] and s['unknowns_preserved'] for s in sigs):
            return {'status':'DEFER_UNKNOWN','reason':'RECURRENT_SUBROLE_COHORT_NOT_ISOLATED','role_authority':'NONE'}
        required={'named':False,'recurrent':True,'episode':True}
    abstract={'subrole':subrole,'required_signature':required,'training_counterpart_ids_excluded':True,'requires_unknowns_preserved':True}
    payload={'kind':SUBROLE_KIND,'schema_id':'VEYA-M06-SUBROLE-'+_sha(abstract)[:24],'abstract_subrole':abstract,'training_counterpart_keys':ids,'training_model_evidence_refs':[[m['evidence_id'],m['evidence_sha256']] for m in training_models],'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE','authority_gain':'NONE'}
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE);sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'SUBROLE_SCHEMA_EVIDENCE_ID_COLLISION','role_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_NEUTRAL_COUNTERPART_SUBROLE_SCHEMA_RESEARCH_ONLY','subrole':subrole,'schema_id':payload['schema_id'],'schema_evidence_id':evidence_id,'schema_evidence_sha256':sha,'training_counterpart_keys':ids,'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE'}

def compose_neutral_subrole_schemas(ms,named_schema:dict[str,Any],recurrent_schema:dict[str,Any],*,evidence_id:str='E-VEYA-M06-COMPOSED-ROLE')->dict[str,Any]:
    if named_schema.get('status')!='OWNED_NEUTRAL_COUNTERPART_SUBROLE_SCHEMA_RESEARCH_ONLY' or named_schema.get('subrole')!=NAMED:
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_NAMED_SUBROLE_SCHEMA_REQUIRED','role_authority':'NONE'}
    if recurrent_schema.get('status')!='OWNED_NEUTRAL_COUNTERPART_SUBROLE_SCHEMA_RESEARCH_ONLY' or recurrent_schema.get('subrole')!=RECURRENT:
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_RECURRENT_SUBROLE_SCHEMA_REQUIRED','role_authority':'NONE'}
    nr=ms.evidence.get(str(named_schema.get('schema_evidence_id',''))); rr=ms.evidence.get(str(recurrent_schema.get('schema_evidence_id','')))
    if nr is None or nr.get('sha256')!=named_schema.get('schema_evidence_sha256') or rr is None or rr.get('sha256')!=recurrent_schema.get('schema_evidence_sha256'):
        return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_SUBROLE_SCHEMA_EVIDENCE_REQUIRED','role_authority':'NONE'}
    named_keys=set(tuple(x) for x in named_schema['training_counterpart_keys']); recur_keys=set(tuple(x) for x in recurrent_schema['training_counterpart_keys'])
    if named_keys & recur_keys:
        return {'status':'DEFER_UNKNOWN','reason':'SUBROLE_TRAINING_COHORTS_MUST_BE_DISJOINT','role_authority':'NONE'}
    abstract={'role':COMPOSED,'required_subroles':[NAMED,RECURRENT],'required_heldout_signature':{'named':True,'recurrent':True,'episode':True},'joint_training_exemplars_allowed':False,'training_cohorts_disjoint':True,'requires_unknowns_preserved':True,'concrete_counterpart_ids_excluded':True}
    payload={'kind':COMPOSED_KIND,'schema_id':'VEYA-M06-COMPOSED-'+_sha(abstract)[:24],'abstract_role':abstract,'named_schema_ref':[named_schema['schema_evidence_id'],named_schema['schema_evidence_sha256']],'recurrent_schema_ref':[recurrent_schema['schema_evidence_id'],recurrent_schema['schema_evidence_sha256']],'training_counterpart_keys':sorted(named_keys|recur_keys),'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE','authority_gain':'NONE'}
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE);sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'COMPOSED_ROLE_SCHEMA_EVIDENCE_ID_COLLISION','role_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_COMPOSED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY','role':COMPOSED,'schema_id':payload['schema_id'],'schema_evidence_id':evidence_id,'schema_evidence_sha256':sha,'training_counterpart_keys':payload['training_counterpart_keys'],'joint_training_exemplars_allowed':False,'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE'}

def transfer_composed_neutral_role(ms,schema:dict[str,Any],*,counterpart_id:str,counterpart_epoch:int)->dict[str,Any]:
    if schema.get('status')!='OWNED_COMPOSED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY':
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_COMPOSED_NEUTRAL_ROLE_SCHEMA_REQUIRED','role_authority':'NONE'}
    row=ms.evidence.get(str(schema.get('schema_evidence_id','')))
    if row is None or row.get('sha256')!=schema.get('schema_evidence_sha256') or row.get('source')!=SOURCE:
        return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_COMPOSED_ROLE_SCHEMA_EVIDENCE_REQUIRED','role_authority':'NONE'}
    model=derive_neutral_counterpart_model(ms,counterpart_id=counterpart_id,counterpart_epoch=counterpart_epoch)
    sig=_model_signature(model)
    if sig is None or not (sig['named'] and sig['recurrent'] and sig['episode'] and sig['unknowns_preserved']):
        return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_COUNTERPART_MISSING_COMPOSED_SUBROLE_REQUIREMENT','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'friendship_authority':'NONE'}
    key=(str(counterpart_id),int(counterpart_epoch))
    if key in set(tuple(x) for x in schema.get('training_counterpart_keys',[])):
        return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_COUNTERPART_MUST_BE_NOVEL','friendship_authority':'NONE'}
    return {'status':'CURRENT_COMPOSED_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY','role':COMPOSED,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'model_evidence_id':model['evidence_id'],'preferred_call_name':model['facets']['call_name_preference']['preferred_call_name'],'distinct_session_count':model['facets']['recurrent_interaction']['distinct_session_count'],'acquisition_basis':'COMPOSITION_OF_INDEPENDENT_DISJOINTLY_TRAINED_SUBROLE_SCHEMAS_WITHOUT_JOINT_EXEMPLAR','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE'}
