from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_conversational_episodic_memory_prototype import SOURCE as M01_SOURCE, KIND as M01_KIND

SOURCE='VEYA-CLEAN-COUNTERPART-NAME-PREFERENCE'
KIND='OWNED_VEYA_COUNTERPART_CALL_NAME_PREFERENCE'


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()


def _extract_preferred_name(utterance:str)->str|None:
    text=str(utterance).strip()
    lower=text.lower()
    # Hedged, negated, or explicitly uncertain naming does not create a binding.
    blockers=('maybe call me','might call me','could call me','do not call me',"don't call me",'not call me','something else','whatever you want','if you want')
    if any(b in lower for b in blockers):
        return None
    pats=[
        r'(?i)\byou can call me\s+([A-Za-z][A-Za-z0-9_-]{0,31})\b',
        r'(?i)\bcall me\s+([A-Za-z][A-Za-z0-9_-]{0,31})\b',
        r'(?i)\bi prefer to be called\s+([A-Za-z][A-Za-z0-9_-]{0,31})\b',
    ]
    vals=[]
    for p in pats:
        m=re.search(p,text)
        if m: vals.append(m.group(1))
    vals=list(dict.fromkeys(v.lower() for v in vals))
    if len(vals)!=1:return None
    m=re.search(r'(?i)\b(?:you can call me|call me|i prefer to be called)\s+([A-Za-z][A-Za-z0-9_-]{0,31})\b',text)
    return m.group(1) if m else None


def derive_counterpart_name_preference(ms,*,episode_evidence_id:str,evidence_id:str|None=None)->dict[str,Any]:
    row=ms.evidence.get(str(episode_evidence_id))
    if row is None or row.get('negative') or row.get('source')!=M01_SOURCE:
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_CONVERSATIONAL_EPISODE_REQUIRED','identity_authority':'NONE'}
    ep=dict(row.get('payload') or {})
    if ep.get('kind')!=M01_KIND:
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_CONVERSATIONAL_EPISODE_REQUIRED','identity_authority':'NONE'}
    name=_extract_preferred_name(str(ep.get('utterance','')))
    if not name:
        return {'status':'DEFER_UNKNOWN','reason':'EXPLICIT_UNAMBIGUOUS_CALL_NAME_PREFERENCE_REQUIRED','identity_authority':'NONE'}
    payload={
        'kind':KIND,
        'counterpart_id':str(ep['counterpart_id']),
        'counterpart_epoch':int(ep['counterpart_epoch']),
        'preferred_call_name':name,
        'source_episode_evidence_id':str(row['evidence_id']),
        'source_episode_evidence_sha256':str(row['sha256']),
        'source_session_id':str(ep['session_id']),
        'source_turn_id':str(ep['turn_id']),
        'preference_semantics':'CURRENT_SELF_DECLARED_CONVERSATIONAL_CALL_NAME_PREFERENCE_ONLY',
        'human_identity_truth_authority':'NONE',
        'legal_name_authority':'NONE',
        'counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY',
        'social_relationship_authority':'NONE',
        'authority_gain':'NONE',
    }
    eid=evidence_id or 'E-VEYA-CALL-NAME-'+_sha(payload)[:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE)
        sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'CALL_NAME_PREFERENCE_EVIDENCE_ID_COLLISION','identity_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_COUNTERPART_CALL_NAME_PREFERENCE_RECORDED_RESEARCH_ONLY','evidence_id':eid,'evidence_sha256':sha,'counterpart_id':payload['counterpart_id'],'counterpart_epoch':payload['counterpart_epoch'],'preferred_call_name':name,'preference_semantics':payload['preference_semantics'],'human_identity_truth_authority':'NONE','counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY'}


def resolve_current_counterpart_name_preference(ms,*,counterpart_id:str,counterpart_epoch:int,limit:int=128)->dict[str,Any]:
    bound=max(1,min(int(limit),256)); candidates=[]; stale=False
    for row in ms.evidence.recent(bound):
        if row is None or row.get('negative') or row.get('source')!=SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=KIND or str(p.get('counterpart_id'))!=str(counterpart_id): continue
        if int(p.get('counterpart_epoch',-1))!=int(counterpart_epoch): stale=True; continue
        src=ms.evidence.get(str(p.get('source_episode_evidence_id','')))
        if src is None or str(src.get('sha256',''))!=str(p.get('source_episode_evidence_sha256','')) or src.get('source')!=M01_SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'EXACT_SOURCE_CONVERSATIONAL_EPISODE_REQUIRED','identity_authority':'NONE'}
        candidates.append((int(row.get('seq',0)),row,p))
    if not candidates:
        if stale:return {'status':'STALE_COUNTERPART_CALL_NAME_PREFERENCE_RESEARCH_ONLY','reason':'COUNTERPART_EPOCH_MISMATCH','identity_authority':'NONE'}
        return {'status':'DEFER_UNKNOWN','reason':'NO_CURRENT_CALL_NAME_PREFERENCE','identity_authority':'NONE'}
    candidates.sort(key=lambda x:x[0],reverse=True)
    latest=candidates[0]
    # Same-seq ambiguity should be impossible in ledger order; explicit contradiction is handled by newest observation wins.
    row,p=latest[1],latest[2]
    return {'status':'CURRENT_COUNTERPART_CALL_NAME_PREFERENCE_RESEARCH_ONLY','preferred_call_name':str(p['preferred_call_name']),'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'source_episode_evidence_id':str(p['source_episode_evidence_id']),'preference_evidence_id':str(row['evidence_id']),'preference_evidence_sha256':str(row['sha256']),'preference_semantics':p['preference_semantics'],'human_identity_truth_authority':'NONE','legal_name_authority':'NONE','counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY','social_relationship_authority':'NONE','retrieval_scope':f'BOUNDED_RECENT_{bound}_EVIDENCE_ROWS'}
