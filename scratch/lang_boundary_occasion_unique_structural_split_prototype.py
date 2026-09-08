from __future__ import annotations

from microseed import EpistemicStatus
from microseed.runtime.entity import action_result_digest
from scratch.lang_arity_generic_prototype import _current_profile

SCOPE='QUALIFICATION_SCOPE:NATIVE_TOKEN_REFERENT'


def derive_unique_structural_split_candidate(ms,*,max_events=65536,max_window=8,min_segment=2,max_segment=4):
    boot=ms._current_runtime_boot_seq()
    if boot<0:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    win=ms._derive_current_store_aware_bounded_operand_window(max_events=max_events,min_arity=min_segment,max_arity=max_window)
    if win.get('status')!='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW':return win
    selected=tuple(win['selected']);rows=ms.evidence.list();sigs=[];tokens=[];components=[]
    for _pos,row,_seq in selected:
        admitted,reason=ms._current_opaque_token_evidence_admissibility(row,boot)
        if not admitted:return {'status':'DEFER_UNKNOWN','reason':reason}
        token=str((row.get('payload') or {}).get('opaque_token',''))
        recs=[]
        for rec in ms.opaque_evidence_associations.records.values():
            if rec.left_opaque_id!=token or SCOPE not in rec.assistance_ancestry:continue
            if ms.opaque_evidence_association_status(rec.record_id).get('status')!='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION':continue
            recs.append(rec)
        if len(recs)!=1:return {'status':'DEFER_UNKNOWN','reason':'UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED','opaque_token':token,'current_candidate_count':len(recs)}
        sig=str(recs[0].right_digest_sha256)
        if _current_profile(ms,rows,boot,sig) is None:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED','opaque_token':token,'referent_signature':sig}
        tokens.append(token);sigs.append(sig)
        components.append({'opaque_token':token,'operational_referent_signature_sha256':sig,'association_record_id':recs[0].record_id,'token_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],'profile_evidence_ref':[str(_current_profile(ms,rows,boot,sig)['evidence_id']),str(_current_profile(ms,rows,boot,sig)['sha256'])],'token_store_event_seq':int(_seq)})
    n=len(sigs)
    full_structurally_admissible=(min_segment<=n<=max_segment and len(set(sigs))==n)
    base={'token_count':n,'opaque_tokens':tuple(tokens),'referent_signatures':tuple(sigs),'components':tuple(components),'selection_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','boundary_creation_effect_authority':'NONE','caller_supplied_split':'NO'}
    if full_structurally_admissible:
        return {**base,'status':'NO_STRUCTURAL_BOUNDARY_OCCASION_REQUIRED','reason':'FULL_CURRENT_WINDOW_STRUCTURALLY_ADMISSIBLE'}
    candidates=[]
    for split in range(min_segment,n-min_segment+1):
        left=sigs[:split];right=sigs[split:]
        if not (min_segment<=len(left)<=max_segment and min_segment<=len(right)<=max_segment):continue
        if len(set(left))!=len(left) or len(set(right))!=len(right):continue
        candidates.append({'split_index':split,'left_referent_signatures':tuple(left),'right_referent_signatures':tuple(right),'left_components':tuple(components[:split]),'right_components':tuple(components[split:]),'left_last_token_store_seq':int(selected[split-1][2]),'right_first_token_store_seq':int(selected[split][2])})
    if len(candidates)==1:
        return {**base,'status':'CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE','reason':'EXACT_ONE_TWO_WINDOW_SPLIT_RESTORES_EARNED_DISTINCT_OPERAND_ADMISSIBILITY','candidate':candidates[0],'candidate_count':1,'selection_authority':'CONTENT_UNIQUENESS_ONLY'}
    if not candidates:
        return {**base,'status':'NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION','reason':'NO_TWO_WINDOW_SPLIT_SATISFIES_EARNED_SEGMENT_ADMISSIBILITY','candidate_count':0}
    return {**base,'status':'AMBIGUOUS_STRUCTURAL_BOUNDARY_OCCASION','reason':'MULTIPLE_TWO_WINDOW_SPLITS_SATISFY_EARNED_SEGMENT_ADMISSIBILITY','candidate_count':len(candidates),'candidates':tuple(candidates)}

def _current_persisted_structural_boundary_witness(ms,row):
    if row is None or row.get('negative'):
        return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_WITNESS_REQUIRED'}
    payload=row.get('payload') or {};boot=ms._current_runtime_boot_seq()
    if payload.get('kind')!='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS':
        return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_WITNESS_KIND_REQUIRED'}
    if int(payload.get('runtime_boot_seq',-1))!=boot:
        return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_WITNESS_CURRENT_BOOT_REQUIRED'}
    comps=payload.get('components') or [];sigs=[];rows=ms.evidence.list()
    for comp in comps:
        tref=comp.get('token_evidence_ref') or [];pref=comp.get('profile_evidence_ref') or []
        if len(tref)!=2 or len(pref)!=2:return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_SOURCE_REF_REQUIRED'}
        token_row=ms.evidence.get(str(tref[0]));profile_row=ms.evidence.get(str(pref[0]))
        if token_row is None or str(token_row.get('sha256',''))!=str(tref[1]):return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_TOKEN_SOURCE_NOT_EXACT'}
        if profile_row is None or str(profile_row.get('sha256',''))!=str(pref[1]):return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_PROFILE_SOURCE_NOT_EXACT'}
        admitted,reason=ms._current_opaque_token_evidence_admissibility(token_row,boot)
        if not admitted:return {'status':'DEFER_UNKNOWN','reason':reason}
        rid=str(comp.get('association_record_id',''));rec=ms.opaque_evidence_associations.records.get(rid)
        if rec is None or ms.opaque_evidence_association_status(rid).get('status')!='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION':return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'}
        sig=str(comp.get('operational_referent_signature_sha256',''))
        if rec.left_opaque_id!=str(comp.get('opaque_token','')) or rec.right_digest_sha256!=sig:return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_ASSOCIATION_CONTENT_MISMATCH'}
        current_profile=_current_profile(ms,rows,boot,sig)
        if current_profile is None or str(current_profile.get('evidence_id',''))!=str(pref[0]) or str(current_profile.get('sha256',''))!=str(pref[1]):return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE'}
        sigs.append(sig)
    n=len(sigs);split=int(payload.get('split_index',-1));min_segment=int(payload.get('bounded_min_segment_arity',2));max_segment=int(payload.get('bounded_max_segment_arity',4))
    candidates=[]
    for k in range(min_segment,n-min_segment+1):
        left=sigs[:k];right=sigs[k:]
        if min_segment<=len(left)<=max_segment and min_segment<=len(right)<=max_segment and len(set(left))==len(left) and len(set(right))==len(right):candidates.append(k)
    if candidates!=[split]:return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_UNIQUE_SPLIT_NO_LONGER_HOLDS','candidate_splits':tuple(candidates)}
    content={'operator':'UNIQUE_TWO_WINDOW_STRUCTURAL_SPLIT','ordered_operational_referent_signatures':sigs,'split_index':split,'bounded_min_segment_arity':min_segment,'bounded_max_segment_arity':max_segment,'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    digest=action_result_digest(content)
    if digest!=str(payload.get('boundary_content_digest_sha256','')):return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_CONTENT_DIGEST_MISMATCH'}
    return {'status':'CURRENT_STRUCTURAL_BOUNDARY_WITNESS','boundary_content_digest_sha256':digest,'split_index':split,'components':tuple(comps),'evidence_id':str(row['evidence_id']),'evidence_sha256':str(row['sha256'])}


def record_unique_structural_boundary_witness_prototype(ms,*,max_events=65536,max_window=8,min_segment=2,max_segment=4):
    boot=ms._current_runtime_boot_seq()
    if boot<0:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    rows=ms.evidence.list()
    # If the latest current-runtime boundary witness has itself closed the token suffix, validate/read it back idempotently.
    for pos in range(len(rows)-1,-1,-1):
        row=rows[pos];payload=row.get('payload') or {}
        if int(payload.get('runtime_boot_seq',-1))!=boot:continue
        if payload.get('kind')=='OPAQUE_EXTERNAL_TOKEN_OBSERVATION':break
        if payload.get('kind')=='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS':
            current=_current_persisted_structural_boundary_witness(ms,row)
            if current.get('status')=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS':
                return {**current,'status':'CURRENT_STRUCTURAL_BOUNDARY_WITNESS_ALREADY_PRESENT','record_status':'BOUNDARY_WITNESS_ALREADY_PRESENT','retroactive_composition_rewrite_authority':'NONE','effect_authority':'NONE','semantic_grouping_authority':'NONE'}
            return current
    candidate=derive_unique_structural_split_candidate(ms,max_events=max_events,max_window=max_window,min_segment=min_segment,max_segment=max_segment)
    if candidate.get('status')!='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE':return candidate
    split=int(candidate['candidate']['split_index']);components=list(candidate['components']);sigs=list(candidate['referent_signatures'])
    content={'operator':'UNIQUE_TWO_WINDOW_STRUCTURAL_SPLIT','ordered_operational_referent_signatures':sigs,'split_index':split,'bounded_min_segment_arity':int(min_segment),'bounded_max_segment_arity':int(max_segment),'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    content_digest=action_result_digest(content)
    payload={'kind':'OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS','runtime_boot_seq':boot,'operator_owner':'MICROSEED_NATIVE_STRUCTURAL_BOUNDARY_OCCASION','boundary_content_digest_sha256':content_digest,'components':components,'ordered_operational_referent_signatures':sigs,'split_index':split,'left_last_token_store_seq':int(candidate['candidate']['left_last_token_store_seq']),'right_first_token_store_seq':int(candidate['candidate']['right_first_token_store_seq']),'bounded_min_segment_arity':int(min_segment),'bounded_max_segment_arity':int(max_segment),'boundary_basis':'EXACT_ONE_TWO_WINDOW_SPLIT_RESTORES_EARNED_DISTINCT_OPERAND_ADMISSIBILITY','boundary_temporality':'RETROSPECTIVE_RECOGNITION_AFTER_EXTENSION_CONFLICT','retroactive_composition_rewrite_authority':'NONE','caller_supplied_split':'NO','caller_supplied_grouping':'NO','caller_supplied_output_evidence_id':'NO','selection_authority':'CONTENT_UNIQUENESS_ONLY','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','authority_gain':'NONE'}
    evidence_id='E-NATIVE-STRUCTURAL-BOUNDARY-'+action_result_digest(payload)[:24]
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-NATIVE-STRUCTURAL-BOUNDARY-OCCASION')
        evidence_sha=ref.sha256;record_status='BOUNDARY_WITNESS_RECORDED'
    else:
        if existing.get('negative') or existing.get('payload')!=payload:return {'status':'DEFER_UNKNOWN','reason':'STRUCTURAL_BOUNDARY_WITNESS_ID_COLLISION','boundary_evidence_id':evidence_id}
        evidence_sha=str(existing.get('sha256',''));record_status='BOUNDARY_WITNESS_ALREADY_PRESENT'
    return {'status':'CURRENT_STRUCTURAL_BOUNDARY_WITNESS_RECORDED','boundary_evidence_id':evidence_id,'boundary_evidence_sha256':evidence_sha,'record_status':record_status,'boundary_content_digest_sha256':content_digest,'split_index':split,'components':tuple(components),'left_last_token_store_seq':payload['left_last_token_store_seq'],'right_first_token_store_seq':payload['right_first_token_store_seq'],'boundary_temporality':payload['boundary_temporality'],'retroactive_composition_rewrite_authority':'NONE','selection_authority':'CONTENT_UNIQUENESS_ONLY','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','caller_supplied_split':'NO','caller_supplied_output_evidence_id':'NO'}
