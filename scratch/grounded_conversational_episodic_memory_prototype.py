from __future__ import annotations

import hashlib
import json
from typing import Any

from microseed import EpistemicStatus

KIND='OWNED_VEYA_CONVERSATIONAL_EPISODE'
SOURCE='VEYA-CLEAN-CONVERSATIONAL-EPISODIC-MEMORY'


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def record_conversational_episode(ms,*,session_id:str,counterpart_id:str,counterpart_epoch:int,turn_id:str,utterance:str,evidence_id:str|None=None)->dict[str,Any]:
    if not session_id or not counterpart_id or int(counterpart_epoch)<0 or not turn_id:
        return {'status':'DEFER_UNKNOWN','reason':'EXPLICIT_SESSION_COUNTERPART_EPOCH_AND_TURN_REQUIRED','truth_authority':'NONE','identity_authority':'NONE'}
    text=str(utterance)
    payload={
        'kind':KIND,
        'session_id':str(session_id),
        'counterpart_id':str(counterpart_id),
        'counterpart_epoch':int(counterpart_epoch),
        'turn_id':str(turn_id),
        'utterance':text,
        'utterance_sha256':hashlib.sha256(text.encode()).hexdigest(),
        'episode_identity_sha256':_sha({'session_id':str(session_id),'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'turn_id':str(turn_id),'utterance':text}),
        'memory_semantics':'OBSERVED_HISTORICAL_UTTERANCE_EVENT_ONLY',
        'truth_authority':'NONE',
        'counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY',
        'selfhood_authority':'NONE',
        'semantic_commitment_authority':'NONE',
    }
    eid=evidence_id or 'E-VEYA-CONV-EPI-'+payload['episode_identity_sha256'][:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE)
        sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'CONVERSATIONAL_EPISODE_EVIDENCE_ID_COLLISION','evidence_id':eid,'truth_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_CONVERSATIONAL_EPISODE_RECORDED_RESEARCH_ONLY','evidence_id':eid,'evidence_sha256':sha,'session_id':str(session_id),'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'turn_id':str(turn_id),'utterance_sha256':payload['utterance_sha256'],'memory_semantics':payload['memory_semantics'],'truth_authority':'NONE','identity_authority':'NONE'}


def recall_recent_conversational_episode(ms,*,counterpart_id:str,counterpart_epoch:int,current_session_id:str,limit:int=64,allow_same_session:bool=False)->dict[str,Any]:
    bound=max(1,min(int(limit),256))
    rows=ms.evidence.recent(bound)
    stale_seen=False
    for row in rows:
        if row is None or row.get('negative') or row.get('source')!=SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=KIND: continue
        if str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch):
            stale_seen=True; continue
        if not allow_same_session and str(p.get('session_id'))==str(current_session_id): continue
        text=str(p.get('utterance',''))
        if hashlib.sha256(text.encode()).hexdigest()!=str(p.get('utterance_sha256','')):
            return {'status':'DEFER_UNKNOWN','reason':'CONVERSATIONAL_EPISODE_UTTERANCE_HASH_MISMATCH','evidence_id':row.get('evidence_id'),'truth_authority':'NONE'}
        expected_identity=_sha({'session_id':str(p.get('session_id')),'counterpart_id':str(p.get('counterpart_id')),'counterpart_epoch':int(p.get('counterpart_epoch')),'turn_id':str(p.get('turn_id')),'utterance':text})
        if expected_identity!=str(p.get('episode_identity_sha256','')):
            return {'status':'DEFER_UNKNOWN','reason':'CONVERSATIONAL_EPISODE_IDENTITY_HASH_MISMATCH','evidence_id':row.get('evidence_id'),'truth_authority':'NONE'}
        return {
            'status':'CURRENT_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY',
            'evidence_id':row['evidence_id'],'evidence_sha256':row['sha256'],
            'source_session_id':str(p['session_id']),'current_session_id':str(current_session_id),
            'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),
            'source_turn_id':str(p['turn_id']),'recalled_utterance':text,'recalled_utterance_sha256':str(p['utterance_sha256']),
            'memory_semantics':'HISTORICAL_UTTERANCE_RECALL_ONLY','truth_authority':'NONE','semantic_truth_inference':'NONE',
            'counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY','selfhood_authority':'NONE','authority_gain':'NONE',
            'retrieval_scope':f'BOUNDED_RECENT_{bound}_EVIDENCE_ROWS'
        }
    if stale_seen:
        return {'status':'STALE_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY','reason':'COUNTERPART_EPOCH_MISMATCH','counterpart_id':str(counterpart_id),'requested_epoch':int(counterpart_epoch),'truth_authority':'NONE','authority_gain':'NONE'}
    return {'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_MATCHING_CONVERSATIONAL_EPISODE','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'current_session_id':str(current_session_id),'truth_authority':'NONE','authority_gain':'NONE'}
