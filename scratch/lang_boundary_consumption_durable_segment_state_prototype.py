from __future__ import annotations
from microseed import EpistemicStatus
from microseed.runtime.entity import action_result_digest

KIND='OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE'
OWNER='MICROSEED_NATIVE_STRUCTURAL_BOUNDARY_CONSUMPTION'


def _state_content_from_boundary(v):
    split=int(v['split_index']);sigs=list(v['ordered_operational_referent_signatures'])
    def content(xs):return {'operator':'ORDERED_EVIDENCE_TUPLE','ordered_operational_referent_signatures':list(xs),'arity':len(xs),'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    left=content(sigs[:split]);right=content(sigs[split:])
    ld=action_result_digest(left);rd=action_result_digest(right)
    state={'operator':'STRUCTURAL_BOUNDARY_SEGMENT_STATE','boundary_content_digest_sha256':v['boundary_content_digest_sha256'],'left_composition_content_digest_sha256':ld,'right_composition_content_digest_sha256':rd,'ordered_segment_composition_digests':[ld,rd],'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    return left,right,state


def validate_current_segment_state_prototype(ms,row,*,rows,boot):
    base={'ledger_rewrite_authority':'NONE','historical_event_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','authority_gain':'NONE'}
    if row.get('negative'):return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_MUST_BE_POSITIVE'}
    p=row.get('payload') or {}
    if p.get('kind')!=KIND:return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_KIND_REQUIRED'}
    if int(p.get('runtime_boot_seq',-1))!=boot:return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_CURRENT_BOOT_REQUIRED'}
    if p.get('operator_owner')!=OWNER or p.get('temporality')!='CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_BOUNDARY':return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_OWNER_OR_TEMPORALITY_MISMATCH'}
    if any(p.get(k)!='NONE' for k in ('ledger_rewrite_authority','historical_event_authority','effect_authority','execution_authority','semantic_grouping_authority')):return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_AUTHORITY_OVERCLAIM'}
    bref=p.get('boundary_evidence_ref') or ()
    if len(bref)!=2:return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_BOUNDARY_REF_REQUIRED'}
    brow=ms.evidence.get(str(bref[0]))
    if brow is None or str(brow.get('sha256',''))!=str(bref[1]):return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_BOUNDARY_REF_NOT_EXACT'}
    bv=ms._validate_current_native_structural_boundary_witness(brow,rows=rows,boot=boot)
    if bv.get('status')!='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS':return {**base,**bv,'status':'DEFER_UNKNOWN'}
    left,right,state=_state_content_from_boundary(bv)
    if p.get('left_content')!=left or p.get('right_content')!=right:return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_COMPOSITION_CONTENT_MISMATCH'}
    if p.get('segment_state_content')!=state or action_result_digest(state)!=str(p.get('segment_state_content_digest_sha256','')):return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_CONTENT_DIGEST_MISMATCH'}
    return {**base,'status':'CURRENT_STRUCTURAL_SEGMENT_STATE','segment_state_evidence_id':str(row['evidence_id']),'segment_state_evidence_sha256':str(row['sha256']),'boundary_evidence_id':str(bref[0]),'boundary_content_digest_sha256':bv['boundary_content_digest_sha256'],'split_index':bv['split_index'],'left_content':left,'right_content':right,'segment_state_content':state,'segment_state_content_digest_sha256':action_result_digest(state)}


def record_oldest_unconsumed_structural_segment_state_prototype(ms,*,max_records=65536):
    boot=ms._current_runtime_boot_seq();base={'selection_basis':'OLDEST_CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_BY_EVIDENCE_APPEND_ORDER','ledger_rewrite_authority':'NONE','historical_event_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','caller_supplied_boundary_id':'NO','caller_supplied_split':'NO','caller_supplied_segment_operands':'NO','caller_supplied_output_evidence_id':'NO'}
    if boot<0:return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    rows=ms.evidence.list()
    if len(rows)>int(max_records):return {**base,'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'SEGMENT_STATE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':len(rows),'max_records':int(max_records)}
    boundaries=[];states=[]
    for pos,row in enumerate(rows):
        p=row.get('payload') or {}
        if int(p.get('runtime_boot_seq',-1))!=boot:continue
        if p.get('kind')=='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS':
            v=ms._validate_current_native_structural_boundary_witness(row,rows=rows,boot=boot)
            if v.get('status')!='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS':return {**base,**v,'status':'DEFER_UNKNOWN'}
            boundaries.append((pos,row,v))
        elif p.get('kind')==KIND:
            v=validate_current_segment_state_prototype(ms,row,rows=rows,boot=boot)
            if v.get('status')!='CURRENT_STRUCTURAL_SEGMENT_STATE':return {**base,**v,'status':'DEFER_UNKNOWN'}
            states.append((pos,row,v))
    consumed={v['boundary_evidence_id'] for _,_,v in states}
    pending=[item for item in boundaries if str(item[1]['evidence_id']) not in consumed]
    if not pending:
        if states:
            _,_,v=states[-1];return {**base,**v,'status':'CURRENT_STRUCTURAL_SEGMENT_STATE_ALREADY_PRESENT','record_status':'SEGMENT_STATE_ALREADY_PRESENT'}
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_WITNESS_REQUIRED','current_boundary_count':len(boundaries)}
    _pos,brow,bv=pending[0]
    left,right,state=_state_content_from_boundary(bv);digest=action_result_digest(state)
    payload={'kind':KIND,'runtime_boot_seq':boot,'operator_owner':OWNER,'boundary_evidence_ref':[str(brow['evidence_id']),str(brow['sha256'])],'boundary_content_digest_sha256':bv['boundary_content_digest_sha256'],'split_index':bv['split_index'],'left_content':left,'right_content':right,'segment_state_content':state,'segment_state_content_digest_sha256':digest,'selection_basis':base['selection_basis'],'temporality':'CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_BOUNDARY','ledger_rewrite_authority':'NONE','historical_event_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','authority_gain':'NONE','caller_supplied_boundary_id':'NO','caller_supplied_split':'NO','caller_supplied_segment_operands':'NO','caller_supplied_output_evidence_id':'NO'}
    eid='E-NATIVE-STRUCTURAL-SEGMENT-STATE-'+action_result_digest(payload)[:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source='MICROSEED-NATIVE-STRUCTURAL-BOUNDARY-CONSUMPTION-PROTOTYPE');sha=ref.sha256;status='SEGMENT_STATE_RECORDED'
    else:
        if existing.get('negative') or existing.get('payload')!=payload:return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_STATE_EVIDENCE_ID_COLLISION','segment_state_evidence_id':eid}
        sha=str(existing.get('sha256',''));status='SEGMENT_STATE_ALREADY_PRESENT'
    return {**base,'status':'CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED','record_status':status,'segment_state_evidence_id':eid,'segment_state_evidence_sha256':sha,'boundary_evidence_id':str(brow['evidence_id']),'boundary_content_digest_sha256':bv['boundary_content_digest_sha256'],'split_index':bv['split_index'],'left_content':left,'right_content':right,'segment_state_content':state,'segment_state_content_digest_sha256':digest}
