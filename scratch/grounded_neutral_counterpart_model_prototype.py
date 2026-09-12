from __future__ import annotations

import hashlib
import json
from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_conversational_episodic_memory_prototype import SOURCE as M01_SOURCE, KIND as M01_KIND
from scratch.grounded_counterpart_name_preference_prototype import resolve_current_counterpart_name_preference
from scratch.grounded_recurrent_counterpart_interaction_prototype import resolve_current_recurrent_counterpart_interaction

SOURCE='VEYA-CLEAN-NEUTRAL-COUNTERPART-MODEL'
KIND='OWNED_VEYA_NEUTRAL_COUNTERPART_MODEL'


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def _latest_episode(ms,counterpart_id:str,counterpart_epoch:int,limit:int=256):
    stale=False
    for row in ms.evidence.recent(max(1,min(int(limit),512))):
        if row is None or row.get('negative') or row.get('source')!=M01_SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=M01_KIND or str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch): stale=True; continue
        return row,p
    return ('STALE' if stale else None),None


def _compose_current_facets(ms, counterpart_id:str, counterpart_epoch:int):
    pref=resolve_current_counterpart_name_preference(ms,counterpart_id=counterpart_id,counterpart_epoch=counterpart_epoch)
    recur=resolve_current_recurrent_counterpart_interaction(ms,counterpart_id=counterpart_id,counterpart_epoch=counterpart_epoch)
    latest,ep=_latest_episode(ms,str(counterpart_id),int(counterpart_epoch))
    facets={'call_name_preference':None,'recurrent_interaction':None,'latest_observed_episode':None}
    stale_all=(latest=='STALE' and pref.get('status','').startswith('STALE_') and recur.get('status','').startswith('STALE_'))
    if pref.get('status')=='CURRENT_COUNTERPART_CALL_NAME_PREFERENCE_RESEARCH_ONLY':
        facets['call_name_preference']={'preferred_call_name':pref['preferred_call_name'],'preference_evidence_id':pref['preference_evidence_id'],'preference_evidence_sha256':pref['preference_evidence_sha256'],'semantics':'SELF_DECLARED_CONVERSATIONAL_CALL_NAME_PREFERENCE_ONLY'}
    if recur.get('status')=='CURRENT_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY':
        facets['recurrent_interaction']={'distinct_session_count':recur['distinct_session_count'],'episode_count':recur['episode_count'],'semantics':'REPEATED_OBSERVED_CONVERSATIONAL_INTERACTION_ONLY'}
    if isinstance(latest,dict) and ep is not None:
        facets['latest_observed_episode']={'episode_evidence_id':latest['evidence_id'],'episode_evidence_sha256':latest['sha256'],'session_id':ep['session_id'],'turn_id':ep['turn_id'],'utterance_sha256':ep['utterance_sha256'],'semantics':'HISTORICAL_UTTERANCE_EVENT_ONLY'}
    return facets, stale_all

def derive_neutral_counterpart_model(ms,*,counterpart_id:str,counterpart_epoch:int,evidence_id:str|None=None)->dict[str,Any]:
    facets, stale_all = _compose_current_facets(ms, str(counterpart_id), int(counterpart_epoch))
    if stale_all:
        return {'status':'STALE_NEUTRAL_COUNTERPART_MODEL_RESEARCH_ONLY','reason':'COUNTERPART_EPOCH_MISMATCH','model_authority':'NONE'}
    if all(v is None for v in facets.values()):
        return {'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_COUNTERPART_FACETS','model_authority':'NONE'}
    payload={
        'kind':KIND,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'facets':facets,
        'explicit_unknowns':{
            'human_identity_truth':'UNKNOWN_NOT_EARNED','legal_name':'UNKNOWN_NOT_EARNED','personality':'UNKNOWN_NOT_EARNED','friendship':'UNKNOWN_NOT_EARNED','trust':'UNKNOWN_NOT_EARNED','attachment':'UNKNOWN_NOT_EARNED','importance':'UNKNOWN_NOT_EARNED','social_valence':'UNKNOWN_NOT_EARNED','relationship_type':'UNKNOWN_NOT_EARNED','goals':'UNKNOWN_NOT_EARNED','beliefs':'UNKNOWN_NOT_EARNED','preferences_beyond_observed':'UNKNOWN_NOT_EARNED'},
        'model_semantics':'COMPOSITION_OF_EXACT_EARNED_COUNTERPART_FACETS_ONLY',
        'model_authority':'NONE','human_identity_truth_authority':'NONE','personality_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','social_valence_authority':'NONE','relationship_type_authority':'NONE','authority_gain':'NONE'}
    eid=evidence_id or 'E-VEYA-NEUTRAL-COUNTERPART-'+_sha(payload)[:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE); sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'NEUTRAL_COUNTERPART_MODEL_EVIDENCE_ID_COLLISION','model_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_NEUTRAL_COUNTERPART_MODEL_RECORDED_RESEARCH_ONLY','evidence_id':eid,'evidence_sha256':sha,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'facets':facets,'explicit_unknowns':payload['explicit_unknowns'],'model_semantics':payload['model_semantics'],'model_authority':'NONE','human_identity_truth_authority':'NONE','personality_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','social_valence_authority':'NONE','relationship_type_authority':'NONE'}


def resolve_current_neutral_counterpart_model(ms,*,counterpart_id:str,counterpart_epoch:int,limit:int=256)->dict[str,Any]:
    for row in ms.evidence.recent(max(1,min(int(limit),512))):
        if row is None or row.get('negative') or row.get('source')!=SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=KIND or str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch): continue
        current_facets, stale_all = _compose_current_facets(ms, str(counterpart_id), int(counterpart_epoch))
        if stale_all or all(v is None for v in current_facets.values()):
            return {'status':'DEFER_UNKNOWN','reason':'CURRENT_COUNTERPART_FACETS_NO_LONGER_QUALIFY','model_authority':'NONE'}
        if current_facets!=p.get('facets'):
            return {'status':'STALE_NEUTRAL_COUNTERPART_MODEL_RESEARCH_ONLY','reason':'OWNED_COUNTERPART_FACETS_CHANGED','model_authority':'NONE'}
        return {'status':'CURRENT_NEUTRAL_COUNTERPART_MODEL_RESEARCH_ONLY','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'facets':dict(p['facets']),'explicit_unknowns':dict(p['explicit_unknowns']),'model_semantics':p['model_semantics'],'model_authority':'NONE','human_identity_truth_authority':'NONE','personality_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','social_valence_authority':'NONE','relationship_type_authority':'NONE'}
    return {'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_NEUTRAL_COUNTERPART_MODEL','model_authority':'NONE'}
