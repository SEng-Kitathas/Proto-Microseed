from __future__ import annotations

from typing import Any


def derive_current_structural_segment_side_child_carriers(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only prototype: expose validated CURRENT segment sides as grouped composition child carriers.

    The caller supplies no segment-state id, side, order, grouping, or output id. The scan follows
    evidence append order and each segment-state row is revalidated through the production validator.
    This emits transient research carriers only; it writes no evidence and grants no historical,
    semantic, scheduling, flattening, associativity, or EFFECT authority.
    """
    base={
        'selection_basis':'CURRENT_STRUCTURAL_SEGMENT_STATE_EVIDENCE_APPEND_ORDER_THEN_LEFT_RIGHT',
        'caller_supplied_segment_state_id':'NO','caller_supplied_side':'NO',
        'caller_supplied_child_order':'NO','caller_supplied_grouping':'NO',
        'historical_event_authority':'NONE','ledger_rewrite_authority':'NONE',
        'semantic_grouping_authority':'NONE','effect_authority':'NONE',
        'execution_authority':'NONE','scheduler_authority':'NONE',
        'flattening_authority':'NONE','associativity_authority':'NONE','authority_gain':'NONE',
    }
    bound=int(max_records)
    if bound<=0:
        return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_SIDE_CARRIER_EVIDENCE_SCAN_BUDGET_REQUIRED'}
    total=m.evidence.count()
    if total>bound:
        return {**base,'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'SEGMENT_SIDE_CARRIER_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':total,'max_records':bound}
    boot=m._current_runtime_boot_seq()
    if boot<0:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    rows=m.evidence.list(); carriers=[]
    for pos,row in enumerate(rows):
        payload=row.get('payload') or {}
        if payload.get('kind')!='OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' or int(payload.get('runtime_boot_seq',-1))!=boot:
            continue
        current=m._validate_current_native_structural_segment_state(row,rows=rows,boot=boot)
        if current.get('status')!='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE':
            return {**base,**current,'status':'DEFER_UNKNOWN'}
        for side_ordinal,(side_name,content,digest) in enumerate((
            ('LEFT',current['left_content'],current['left_composition_content_digest_sha256']),
            ('RIGHT',current['right_content'],current['right_composition_content_digest_sha256']),
        )):
            ordered=tuple(str(x) for x in content.get('ordered_operational_referent_signatures',()))
            if content.get('operator')!='ORDERED_EVIDENCE_TUPLE' or int(content.get('arity',-1))!=len(ordered) or len(ordered)<2 or len(ordered)>4:
                return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_SIDE_NOT_BOUNDED_ORDERED_COMPOSITION_CONTENT','segment_state_evidence_id':str(row.get('evidence_id','')),'side':side_name}
            carriers.append({
                'carrier_kind':'CURRENT_STRUCTURAL_SEGMENT_SIDE_GROUPED_COMPOSITION_CHILD',
                'segment_state_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],
                'segment_state_content_digest_sha256':str(current['segment_state_content_digest_sha256']),
                'boundary_evidence_ref':[str(current['boundary_evidence_id']),str(current['boundary_evidence_sha256'])],
                'side':side_name,'side_ordinal':side_ordinal,
                'composition_content_digest_sha256':str(digest),
                'ordered_operational_referent_signatures':list(ordered),
                'arity':len(ordered),'composition_operator':'ORDERED_EVIDENCE_TUPLE',
                'evidence_list_position':pos,
                'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
                'retrospective_provenance':'CURRENT_APPEND_ONLY_STRUCTURAL_SEGMENT_STATE_SIDE',
                'historical_event_authority':'NONE','flattening_authority':'NONE','associativity_authority':'NONE',
            })
    if not carriers:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_STRUCTURAL_SEGMENT_STATE_REQUIRED'}
    return {**base,'status':'CURRENT_STRUCTURAL_SEGMENT_SIDE_CHILD_CARRIERS_DERIVED','carriers':tuple(carriers),'carrier_count':len(carriers)}
