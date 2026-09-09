from __future__ import annotations

from typing import Any

from microseed.development.action_closure import result_digest as action_result_digest
from scratch.lang_segment_state_operand_carrier_prototype import derive_current_structural_segment_side_child_carriers


def derive_current_segment_state_b2_recursive_parent_prototypes(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only prototype for B2-compatible segment-state-side reuse.

    Each CURRENT segment state contributes exactly its LEFT then RIGHT grouped child carriers.
    Only 2+2 child arity is admitted here because that is the exact already-earned recursive-B2
    child contract. Mixed 2..4 child arity remains deliberately unearned. No historical B2 row,
    parent row, grouping choice, flattening, associativity, semantic or EFFECT authority is created.
    """
    base={
        'selection_basis':'CURRENT_STRUCTURAL_SEGMENT_STATE_EVIDENCE_APPEND_ORDER_WITHIN_STATE_LEFT_RIGHT',
        'caller_supplied_segment_state_id':'NO','caller_supplied_child_ids':'NO',
        'caller_supplied_child_order':'NO','caller_supplied_grouping':'NO',
        'historical_event_authority':'NONE','ledger_rewrite_authority':'NONE',
        'flattening_authority':'NONE','associativity_authority':'NONE',
        'semantic_composition_authority':'NONE','grammar_authority':'NONE',
        'effect_authority':'NONE','execution_authority':'NONE','scheduler_authority':'NONE',
        'authority_gain':'NONE','recursive_depth_limit':1,'admitted_child_arity':2,
    }
    carriers=derive_current_structural_segment_side_child_carriers(m,max_records=max_records)
    if carriers.get('status')!='CURRENT_STRUCTURAL_SEGMENT_SIDE_CHILD_CARRIERS_DERIVED':
        return {**base,**carriers,'status':carriers.get('status','DEFER_UNKNOWN')}
    grouped={}; order=[]
    for c in carriers['carriers']:
        sid=str(c['segment_state_evidence_ref'][0])
        if sid not in grouped:
            grouped[sid]=[];order.append(sid)
        grouped[sid].append(c)
    parents=[]; skipped=[]
    for sid in order:
        children=grouped[sid]
        if len(children)!=2 or tuple(c['side'] for c in children)!=('LEFT','RIGHT'):
            return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_LEFT_RIGHT_SEGMENT_CHILD_PAIR_REQUIRED','segment_state_evidence_id':sid}
        arities=tuple(int(c['arity']) for c in children)
        if arities!=(2,2):
            skipped.append({'segment_state_evidence_id':sid,'child_arities':arities,'reason':'MIXED_OR_NON_B2_SEGMENT_CHILD_ARITY_NOT_EARNED'})
            continue
        child_digests=tuple(str(c['composition_content_digest_sha256']) for c in children)
        if len(set(child_digests))!=2:
            return {**base,'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED','segment_state_evidence_id':sid}
        content={
            'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'ordered_child_composition_content_digests':list(child_digests),
            'composition_depth':1,'child_arity':2,
            'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
        }
        parents.append({
            'carrier_kind':'CURRENT_STRUCTURAL_SEGMENT_B2_RECURSIVE_PARENT_PROTOTYPE',
            'segment_state_evidence_ref':children[0]['segment_state_evidence_ref'],
            'boundary_evidence_ref':children[0]['boundary_evidence_ref'],
            'ordered_child_composition_content_digests':child_digests,
            'children':tuple(children),'composition_content':content,
            'composition_content_digest_sha256':action_result_digest(content),
            'composition_operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'composition_depth':1,'child_arity':2,
            'historical_event_authority':'NONE','flattening_authority':'NONE',
            'associativity_authority':'NONE','authority_gain':'NONE',
        })
    if not parents:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED','skipped':tuple(skipped)}
    return {**base,'status':'CURRENT_SEGMENT_STATE_B2_RECURSIVE_PARENT_PROTOTYPES_DERIVED','parents':tuple(parents),'parent_count':len(parents),'skipped':tuple(skipped)}
