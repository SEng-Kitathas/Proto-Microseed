from __future__ import annotations

from microseed.runtime.entity import action_result_digest
from scratch.lang_arity_generic_prototype import _current_profile

TOKEN_KIND='OPAQUE_EXTERNAL_TOKEN_OBSERVATION'
SCOPE='QUALIFICATION_SCOPE:NATIVE_TOKEN_REFERENT'


def derive_store_aware_operand_window(ms,*,max_events=65536,min_arity=2,max_arity=4):
    boot=ms._current_runtime_boot_seq()
    if boot<0:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    events=ms.store.events();bound=int(max_events)
    if bound<=0:return {'status':'DEFER_UNKNOWN','reason':'OPERAND_WINDOW_EVENT_SCAN_BUDGET_REQUIRED'}
    current=[row for row in events if int(row.get('seq',-1))>boot]
    if len(current)>bound:
        return {'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'OPERAND_WINDOW_EVENT_HISTORY_EXCEEDS_SCAN_BUDGET','current_event_count':len(current),'max_events':bound}
    window=[];last_boundary=None;seen_evidence_events=set();seen_execution_events=set()
    for event in current:
        kind=str(event.get('kind',''));payload=event.get('payload') or {}
        if kind=='EVIDENCE':
            eid=str(payload.get('evidence_id',''))
            if eid in seen_evidence_events:
                return {'status':'DEFER_UNKNOWN','reason':'OPERAND_WINDOW_EVIDENCE_EVENT_REPLAY_DETECTED','evidence_id':eid,'store_seq':int(event.get('seq',-1))}
            seen_evidence_events.add(eid)
            erow=ms.evidence.get(eid)
            if erow is None or str(erow.get('sha256',''))!=str(payload.get('sha256','')):
                return {'status':'DEFER_UNKNOWN','reason':'OPERAND_WINDOW_EVIDENCE_EVENT_NOT_EXACT','evidence_id':eid}
            ep=erow.get('payload') or {}
            if ep.get('kind')==TOKEN_KIND and int(ep.get('runtime_boot_seq',-1))==boot:
                window.append((int(event['seq']),erow))
            else:
                window=[];last_boundary={'kind':'REPRESENTED_NON_TOKEN_EVIDENCE','store_seq':int(event['seq']),'evidence_id':eid}
        elif kind=='BOUNDED_ACTION_EXECUTED':
            execution_id=str(payload.get('execution_id',''))
            if execution_id in seen_execution_events:
                return {'status':'DEFER_UNKNOWN','reason':'ACTION_EXECUTION_BOUNDARY_REPLAY_DETECTED','execution_id':execution_id,'store_seq':int(event.get('seq',-1))}
            seen_execution_events.add(execution_id)
            rec=ms.action_closure.executions.get(execution_id)
            if rec is None or rec.serializable()!=payload:
                return {'status':'DEFER_UNKNOWN','reason':'ACTION_EXECUTION_BOUNDARY_NOT_AUTHENTICATED','execution_id':execution_id,'store_seq':int(event.get('seq',-1))}
            window=[];last_boundary={'kind':'BOUNDED_ACTION_EXECUTED','store_seq':int(event['seq']),'execution_id':execution_id}
        else:
            # Other store traffic has no grouping authority.
            continue
    arity=len(window)
    if arity<min_arity:return {'status':'DEFER_UNKNOWN','reason':'BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM','derived_arity':arity,'last_boundary':last_boundary}
    if arity>max_arity:return {'status':'DEFER_UNKNOWN','reason':'BOUNDED_OPERAND_WINDOW_EXCEEDS_MAXIMUM','derived_arity':arity,'last_boundary':last_boundary}
    return {'status':'CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW','derived_arity':arity,'selected':tuple(window),'last_boundary':last_boundary,'boundary_basis':'AUTHENTICATED_DURABLE_STORE_EVENT_CHRONOLOGY','caller_supplied_boundary':'NO'}


def derive_store_aware_bounded_composition_prototype(ms,*,max_events=65536,max_records=65536,min_arity=2,max_arity=4):
    win=derive_store_aware_operand_window(ms,max_events=max_events,min_arity=min_arity,max_arity=max_arity)
    if win.get('status')!='CURRENT_STORE_AWARE_BOUNDED_OPERAND_WINDOW':return win
    if ms.evidence.count()>int(max_records):
        return {'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'BOUNDED_COMPOSITION_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':ms.evidence.count(),'max_records':int(max_records)}
    boot=ms._current_runtime_boot_seq();rows=ms.evidence.list();selected=win['selected'];arity=int(win['derived_arity'])
    for _seq,row in selected:
        admitted,reason=ms._current_opaque_token_evidence_admissibility(row,boot)
        if not admitted:return {'status':'DEFER_UNKNOWN','reason':reason,'derived_arity':arity,'last_boundary':win.get('last_boundary')}
    components=[];sigs=[]
    for ordinal,(event_seq,row) in enumerate(selected):
        token=str((row.get('payload') or {}).get('opaque_token',''))
        recs=[]
        for rec in ms.opaque_evidence_associations.records.values():
            if rec.left_opaque_id!=token or SCOPE not in rec.assistance_ancestry:continue
            if ms.opaque_evidence_association_status(rec.record_id).get('status')!='CURRENT_OPAQUE_EVIDENCE_ASSOCIATION':continue
            recs.append(rec)
        if len(recs)!=1:return {'status':'DEFER_UNKNOWN','reason':'UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED','derived_arity':arity,'opaque_token':token}
        rec=recs[0];sig=str(rec.right_digest_sha256);profile=_current_profile(ms,rows,boot,sig)
        if profile is None:return {'status':'DEFER_UNKNOWN','reason':'CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED','derived_arity':arity,'opaque_token':token,'referent_signature':sig}
        sigs.append(sig);components.append({'ordinal':ordinal,'opaque_token':token,'operational_referent_signature_sha256':sig,'association_record_id':rec.record_id,'token_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],'profile_evidence_ref':[str(profile['evidence_id']),str(profile['sha256'])],'token_store_event_seq':event_seq})
    if len(set(sigs))!=arity:return {'status':'DEFER_UNKNOWN','reason':'ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT','derived_arity':arity}
    content={'operator':'ORDERED_EVIDENCE_TUPLE','ordered_operational_referent_signatures':list(sigs),'arity':arity,'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    return {'status':'CURRENT_STORE_AWARE_BOUNDED_COMPOSITION_PROTOTYPE','derived_arity':arity,'ordered_operational_referent_signatures':tuple(sigs),'components':tuple(components),'composition_content_digest_sha256':action_result_digest(content),'content':content,'last_boundary':win.get('last_boundary'),'boundary_basis':win['boundary_basis'],'caller_supplied_boundary':'NO','caller_supplied_arity':'NO','execution_authority_gain':'NONE','semantic_grouping_authority':'NONE'}
