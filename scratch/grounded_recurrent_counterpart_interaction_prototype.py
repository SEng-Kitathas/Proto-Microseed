from __future__ import annotations

import hashlib
import json
from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_conversational_episodic_memory_prototype import SOURCE as M01_SOURCE, KIND as M01_KIND

SOURCE='VEYA-CLEAN-RECURRENT-COUNTERPART-INTERACTION'
KIND='OWNED_VEYA_RECURRENT_COUNTERPART_INTERACTION_RELATION'


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def derive_recurrent_counterpart_interaction(ms,*,counterpart_id:str,counterpart_epoch:int,min_distinct_sessions:int=2,limit:int=256,evidence_id:str|None=None)->dict[str,Any]:
    bound=max(2,min(int(limit),512)); sessions={}; rows=[]; stale=False
    for row in ms.evidence.recent(bound):
        if row is None or row.get('negative') or row.get('source')!=M01_SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=M01_KIND or str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch): stale=True; continue
        sid=str(p.get('session_id'))
        sessions.setdefault(sid,[]).append(str(row['evidence_id']))
        rows.append((int(row.get('seq',0)),row,p))
    if len(sessions)<int(min_distinct_sessions):
        if stale and not sessions:
            return {'status':'STALE_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY','reason':'COUNTERPART_EPOCH_MISMATCH','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'social_relationship_authority':'NONE'}
        return {'status':'DEFER_UNKNOWN','reason':'MULTIPLE_DISTINCT_CONVERSATION_SESSIONS_REQUIRED','distinct_session_count':len(sessions),'required':int(min_distinct_sessions),'social_relationship_authority':'NONE'}
    rows.sort(key=lambda x:x[0])
    payload={
        'kind':KIND,
        'counterpart_id':str(counterpart_id),
        'counterpart_epoch':int(counterpart_epoch),
        'distinct_session_ids':sorted(sessions),
        'distinct_session_count':len(sessions),
        'episode_evidence_ids':[str(r[1]['evidence_id']) for r in rows],
        'episode_count':len(rows),
        'first_episode_seq':rows[0][0],
        'last_episode_seq':rows[-1][0],
        'interaction_semantics':'REPEATED_OBSERVED_CONVERSATIONAL_INTERACTION_ONLY',
        'human_identity_truth_authority':'NONE',
        'friendship_authority':'NONE',
        'trust_authority':'NONE',
        'attachment_authority':'NONE',
        'social_valence_authority':'NONE',
        'importance_authority':'NONE',
        'relationship_type_authority':'NONE',
        'authority_gain':'NONE',
    }
    eid=evidence_id or 'E-VEYA-RECURRENT-INTERACTION-'+_sha(payload)[:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE); sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'RECURRENT_INTERACTION_EVIDENCE_ID_COLLISION','social_relationship_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_RECURRENT_COUNTERPART_INTERACTION_RECORDED_RESEARCH_ONLY','evidence_id':eid,'evidence_sha256':sha,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'distinct_session_count':len(sessions),'episode_count':len(rows),'interaction_semantics':payload['interaction_semantics'],'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE'}


def resolve_current_recurrent_counterpart_interaction(ms,*,counterpart_id:str,counterpart_epoch:int,limit:int=256)->dict[str,Any]:
    for row in ms.evidence.recent(max(2,min(int(limit),512))):
        if row is None or row.get('negative') or row.get('source')!=SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=KIND or str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch): continue
        for eid in p.get('episode_evidence_ids',[]):
            src=ms.evidence.get(str(eid))
            if src is None or src.get('source')!=M01_SOURCE:
                return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_EPISODE_SET_REQUIRED','social_relationship_authority':'NONE'}
        return {'status':'CURRENT_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY','counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'distinct_session_count':int(p['distinct_session_count']),'episode_count':int(p['episode_count']),'distinct_session_ids':list(p['distinct_session_ids']),'interaction_semantics':p['interaction_semantics'],'friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','social_valence_authority':'NONE','importance_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE'}
    # Distinguish stale history when possible.
    for row in ms.evidence.recent(max(2,min(int(limit),512))):
        if row and row.get('source')==SOURCE:
            p=dict(row.get('payload') or {})
            if p.get('kind')==KIND and str(p.get('counterpart_id'))==str(counterpart_id):
                return {'status':'STALE_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY','reason':'COUNTERPART_EPOCH_MISMATCH','social_relationship_authority':'NONE'}
    return {'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_RECURRENT_COUNTERPART_INTERACTION','social_relationship_authority':'NONE'}
