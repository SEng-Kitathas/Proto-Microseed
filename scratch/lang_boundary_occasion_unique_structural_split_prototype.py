from __future__ import annotations

from scratch.lang_arity_generic_prototype import _current_profile

SCOPE='QUALIFICATION_SCOPE:NATIVE_TOKEN_REFERENT'


def derive_unique_structural_split_candidate(ms,*,max_events=65536,max_window=8,min_segment=2,max_segment=4):
    boot=ms._current_runtime_boot_seq()
    if boot<0:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    win=ms._derive_current_store_aware_bounded_operand_window(max_events=max_events,min_arity=min_segment,max_arity=max_window)
    if win.get('status')!='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW':return win
    selected=tuple(win['selected']);rows=ms.evidence.list();sigs=[];tokens=[]
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
    n=len(sigs)
    full_structurally_admissible=(min_segment<=n<=max_segment and len(set(sigs))==n)
    base={'token_count':n,'opaque_tokens':tuple(tokens),'referent_signatures':tuple(sigs),'selection_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','boundary_creation_effect_authority':'NONE','caller_supplied_split':'NO'}
    if full_structurally_admissible:
        return {**base,'status':'NO_STRUCTURAL_BOUNDARY_OCCASION_REQUIRED','reason':'FULL_CURRENT_WINDOW_STRUCTURALLY_ADMISSIBLE'}
    candidates=[]
    for split in range(min_segment,n-min_segment+1):
        left=sigs[:split];right=sigs[split:]
        if not (min_segment<=len(left)<=max_segment and min_segment<=len(right)<=max_segment):continue
        if len(set(left))!=len(left) or len(set(right))!=len(right):continue
        candidates.append({'split_index':split,'left_referent_signatures':tuple(left),'right_referent_signatures':tuple(right),'left_last_token_store_seq':int(selected[split-1][2]),'right_first_token_store_seq':int(selected[split][2])})
    if len(candidates)==1:
        return {**base,'status':'CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE','reason':'EXACT_ONE_TWO_WINDOW_SPLIT_RESTORES_EARNED_DISTINCT_OPERAND_ADMISSIBILITY','candidate':candidates[0],'candidate_count':1,'selection_authority':'CONTENT_UNIQUENESS_ONLY'}
    if not candidates:
        return {**base,'status':'NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION','reason':'NO_TWO_WINDOW_SPLIT_SATISFIES_EARNED_SEGMENT_ADMISSIBILITY','candidate_count':0}
    return {**base,'status':'AMBIGUOUS_STRUCTURAL_BOUNDARY_OCCASION','reason':'MULTIPLE_TWO_WINDOW_SPLITS_SATISFY_EARNED_SEGMENT_ADMISSIBILITY','candidate_count':len(candidates),'candidates':tuple(candidates)}
