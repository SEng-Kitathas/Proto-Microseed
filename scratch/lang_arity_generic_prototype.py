from __future__ import annotations

from microseed.runtime.entity import action_result_digest

TOKEN_KIND='OPAQUE_EXTERNAL_TOKEN_OBSERVATION'
SCOPE='QUALIFICATION_SCOPE:NATIVE_TOKEN_REFERENT'

def _current_profile(ms,rows,boot,referent_sig):
    candidates=[]
    for row in rows:
        pp=row.get('payload') or {}
        if (pp.get('kind')!='OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS'
                or int(pp.get('runtime_boot_seq',-1))!=boot
                or str(pp.get('operational_referent_signature_sha256',''))!=referent_sig
                or row.get('negative')):
            continue
        action=str(pp.get('exclusive_action_id','')); cap=ms.capabilities.contracts.get(action)
        if cap is None or not ms.capabilities.is_current(action): continue
        if (ms.capabilities.epochs.get(action,-1)!=int(pp.get('exclusive_action_epoch',-1))
                or cap.computed_signature_sha256()!=str(pp.get('exclusive_action_signature_sha256',''))): continue
        frame_id=str(pp.get('frame_id','')); frame=ms.frames.frames.get(frame_id)
        if (frame is None or not ms.frames.is_current(frame_id,int(pp.get('frame_epoch',-1)))
                or frame.signature_sha256!=str(pp.get('frame_signature_sha256',''))): continue
        exact=True
        for eid,sig in pp.get('source_raw_evidence_refs',()):
            erow=ms.evidence.get(str(eid))
            if erow is None or str(erow.get('sha256',''))!=str(sig): exact=False;break
        if exact: candidates.append(row)
    return candidates[-1] if candidates else None


def derive_current_bounded_ordered_composition_prototype(ms,*,min_arity=2,max_arity=4):
    rows=ms.evidence.list();boot=ms._current_runtime_boot_seq()
    if boot<0:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    suffix=[]
    for pos in range(len(rows)-1,-1,-1):
        row=rows[pos];payload=row.get('payload') or {}
        if payload.get('kind')!=TOKEN_KIND or int(payload.get('runtime_boot_seq',-1))!=boot: break
        suffix.append((pos,row))
    suffix=tuple(reversed(suffix));arity=len(suffix)
    if arity<min_arity:
        return {'status':'DEFER_UNKNOWN','reason':'BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM','derived_arity':arity}
    if arity>max_arity:
        return {'status':'DEFER_UNKNOWN','reason':'BOUNDED_OPERAND_WINDOW_EXCEEDS_MAXIMUM','derived_arity':arity,'max_arity':max_arity}
    components=[];sigs=[]
    for ordinal,(pos,row) in enumerate(suffix):
        payload=row.get('payload') or {};token=str(payload.get('opaque_token',''))
        if not token:return {'status':'DEFER_UNKNOWN','reason':'OPAQUE_TOKEN_CONTENT_REQUIRED','derived_arity':arity}
        recs=[]
        for rec in ms.opaque_evidence_associations.records.values():
            if rec.left_opaque_id!=token or SCOPE not in rec.assistance_ancestry: continue
            if ms.opaque_evidence_association_status(rec.record_id).get('status')!='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION': continue
            recs.append(rec)
        if len(recs)!=1:
            return {'status':'DEFER_UNKNOWN','reason':'UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED','opaque_token':token,'derived_arity':arity,'current_candidate_count':len(recs)}
        rec=recs[0];sig=str(rec.right_digest_sha256);profile=_current_profile(ms,rows,boot,sig)
        if profile is None:
            return {'status':'DEFER_UNKNOWN','reason':'CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED','opaque_token':token,'referent_signature':sig,'derived_arity':arity}
        sigs.append(sig)
        components.append({'ordinal':ordinal,'opaque_token':token,'operational_referent_signature_sha256':sig,'association_record_id':rec.record_id,'token_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],'profile_evidence_ref':[str(profile['evidence_id']),str(profile['sha256'])],'evidence_list_position':pos,'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'})
    if len(set(sigs))!=arity:
        return {'status':'DEFER_UNKNOWN','reason':'ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT','derived_arity':arity}
    content={'operator':'ORDERED_EVIDENCE_TUPLE','ordered_operational_referent_signatures':list(sigs),'arity':arity,'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    return {'status':'CURRENT_BOUNDED_ORDERED_COMPOSITION_PROTOTYPE','derived_arity':arity,'ordered_operational_referent_signatures':tuple(sigs),'components':tuple(components),'composition_content_digest_sha256':action_result_digest(content),'content':content,'arity_basis':'EXACT_CONTIGUOUS_CURRENT_RUNTIME_TOKEN_SUFFIX_LENGTH','caller_supplied_arity':'NO','caller_supplied_operands':'NO','semantic_authority':'NONE'}
