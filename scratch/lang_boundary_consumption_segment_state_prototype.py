from __future__ import annotations
from microseed.runtime.entity import action_result_digest


def derive_current_segment_state_from_unique_boundary(ms,*,max_records=65536):
    boot=ms._current_runtime_boot_seq()
    base={'ledger_rewrite_authority':'NONE','historical_event_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE','caller_supplied_boundary_id':'NO','caller_supplied_split':'NO','caller_supplied_segment_operands':'NO'}
    if boot<0:return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    rows=ms.evidence.list()
    if len(rows)>int(max_records):return {**base,'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'SEGMENT_STATE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':len(rows),'max_records':int(max_records)}
    current=[]
    for row in rows:
        p=row.get('payload') or {}
        if p.get('kind')!='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS' or int(p.get('runtime_boot_seq',-1))!=boot:continue
        v=ms._validate_current_native_structural_boundary_witness(row,rows=rows,boot=boot)
        if v.get('status')=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS':current.append((row,v))
    if len(current)!=1:return {**base,'status':'DEFER_UNKNOWN','reason':'UNIQUE_CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_WITNESS_REQUIRED','current_boundary_count':len(current)}
    row,v=current[0];split=int(v['split_index']);sigs=list(v['ordered_operational_referent_signatures']);comps=list(v['components'])
    left_sigs=sigs[:split];right_sigs=sigs[split:]
    def content(xs):return {'operator':'ORDERED_EVIDENCE_TUPLE','ordered_operational_referent_signatures':list(xs),'arity':len(xs),'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY'}
    left_content=content(left_sigs);right_content=content(right_sigs)
    state_content={
        'operator':'STRUCTURAL_BOUNDARY_SEGMENT_STATE',
        'boundary_content_digest_sha256':v['boundary_content_digest_sha256'],
        'left_composition_content_digest_sha256':action_result_digest(left_content),
        'right_composition_content_digest_sha256':action_result_digest(right_content),
        'ordered_segment_composition_digests':[action_result_digest(left_content),action_result_digest(right_content)],
        'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY',
    }
    return {**base,'status':'CURRENT_RETROSPECTIVE_SEGMENT_STATE_PROTOTYPE','boundary_evidence_ref':[v['boundary_evidence_id'],v['boundary_evidence_sha256']],
        'boundary_content_digest_sha256':v['boundary_content_digest_sha256'],'split_index':split,
        'left_components':tuple(comps[:split]),'right_components':tuple(comps[split:]),
        'left_content':left_content,'right_content':right_content,
        'left_composition_content_digest_sha256':action_result_digest(left_content),'right_composition_content_digest_sha256':action_result_digest(right_content),
        'segment_state_content':state_content,'segment_state_content_digest_sha256':action_result_digest(state_content),
        'temporality':'CURRENT_RETROSPECTIVE_DERIVATION_FROM_EXACT_BOUNDARY_WITNESS'}
