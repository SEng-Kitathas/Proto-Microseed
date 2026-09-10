from __future__ import annotations

from typing import Any
from microseed.development.action_closure import result_digest as action_result_digest

DEPTH_ONE_PARENT_KINDS=(
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE",
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE",
)


def derive_current_depth_one_segment_parent_child_carriers(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only projection of CURRENT depth-one retrospective segment parents into child carriers."""
    base={
        'accepted_parent_depth':1,'candidate_output_depth':2,'parent_child_count':2,
        'selection_basis':'LATEST_TWO_DISTINCT_CURRENT_DEPTH_ONE_RETROSPECTIVE_SEGMENT_PARENT_CONTENTS_IN_EVIDENCE_ORDER',
        'caller_supplied_parent_ids':'NO','caller_supplied_parent_order':'NO','caller_supplied_grouping':'NO','caller_supplied_depth':'NO',
        'historical_event_authority':'NONE','ledger_rewrite_authority':'NONE','flattening_authority':'NONE','associativity_authority':'NONE',
        'semantic_composition_authority':'NONE','grammar_authority':'NONE','scheduler_authority':'NONE','execution_authority':'NONE','effect_authority':'NONE','authority_gain':'NONE',
    }
    bound=int(max_records)
    if bound<=0:
        return {**base,'status':'DEFER_UNKNOWN','reason':'DEPTH_ONE_PARENT_EVIDENCE_SCAN_BUDGET_REQUIRED'}
    total=m.evidence.count()
    if total>bound:
        return {**base,'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'DEPTH_ONE_PARENT_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':total,'max_records':bound}
    boot=m._current_runtime_boot_seq()
    if boot<0:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED'}
    rows=m.evidence.list(); carriers=[]
    for pos,row in enumerate(rows):
        payload=row.get('payload') or {}; kind=payload.get('kind')
        if int(payload.get('runtime_boot_seq',-1))!=boot or kind not in DEPTH_ONE_PARENT_KINDS:
            continue
        if kind==DEPTH_ONE_PARENT_KINDS[0]:
            cur=m._validate_current_native_structural_segment_b2_recursive_composition_state(row,rows=rows,boot=boot)
            required='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE'
        else:
            cur=m._validate_current_native_structural_segment_bounded_recursive_composition_state(row,rows=rows,boot=boot)
            required='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE'
        if cur.get('status')!=required:
            return {**base,**cur,'status':'DEFER_UNKNOWN'}
        if int(cur.get('composition_depth',-1))!=1 or int(cur.get('child_arity',-1))!=2:
            return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_DEPTH_ONE_TWO_CHILD_PARENT_REQUIRED','source_parent_kind':kind}
        nested_children=tuple(cur.get('children',()))
        child_digests=tuple(str(x) for x in cur.get('ordered_child_composition_content_digests',()))
        if len(nested_children)!=2 or len(child_digests)!=2 or len(set(child_digests))!=2:
            return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_DISTINCT_GROUPED_DEPTH_ONE_PARENT_REQUIRED','source_parent_kind':kind}
        expected=action_result_digest({
            'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'ordered_child_composition_content_digests':list(child_digests),
            'composition_depth':1,'child_arity':2,
            'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
        })
        if expected!=str(cur.get('composition_content_digest_sha256','')):
            return {**base,'status':'DEFER_UNKNOWN','reason':'DEPTH_ONE_PARENT_CONTENT_DIGEST_MISMATCH','source_parent_kind':kind}
        carriers.append({
            'carrier_kind':'CURRENT_DEPTH_ONE_RETROSPECTIVE_SEGMENT_PARENT_CHILD',
            'evidence_list_position':pos,
            'source_parent_kind':kind,
            'source_parent_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],
            'source_segment_state_evidence_ref':[str(cur['segment_state_evidence_id']),str(cur['segment_state_evidence_sha256'])],
            'source_boundary_evidence_ref':[str(cur['boundary_evidence_id']),str(cur['boundary_evidence_sha256'])],
            'composition_content_digest_sha256':expected,
            'composition_depth':1,'child_arity':2,
            'nested_children':nested_children,
            'nested_child_content_digests':child_digests,
            'retrospective_provenance':'CURRENT_APPEND_ONLY_DEPTH_ONE_SEGMENT_PARENT_STATE',
            'flattening_authority':'NONE','associativity_authority':'NONE','historical_event_authority':'NONE',
        })
    if not carriers:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_DEPTH_ONE_RETROSPECTIVE_SEGMENT_PARENT_REQUIRED'}
    return {**base,'status':'CURRENT_DEPTH_ONE_SEGMENT_PARENT_CHILD_CARRIERS_DERIVED','carriers':tuple(carriers),'carrier_count':len(carriers)}


def derive_current_depth_two_segment_parent_prototype(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only one-edge depth-two prototype from two distinct CURRENT depth-one parent contents."""
    base=derive_current_depth_one_segment_parent_child_carriers(m,max_records=max_records)
    if base.get('status')!='CURRENT_DEPTH_ONE_SEGMENT_PARENT_CHILD_CARRIERS_DERIVED':
        return base
    selected_rev=[]; seen=set()
    for child in reversed(base['carriers']):
        digest=str(child['composition_content_digest_sha256'])
        if digest in seen:
            continue
        seen.add(digest); selected_rev.append(child)
        if len(selected_rev)==2:
            break
    if len(selected_rev)<2:
        return {**base,'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_DEPTH_ONE_SEGMENT_PARENT_CONTENTS_REQUIRED','current_distinct_parent_count':len(selected_rev)}
    children=tuple(reversed(selected_rev)); child_digests=tuple(str(c['composition_content_digest_sha256']) for c in children)
    content={
        'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
        'ordered_child_composition_content_digests':list(child_digests),
        'composition_depth':2,'child_arity':2,
        'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
    }
    return {
        **base,
        'status':'CURRENT_DEPTH_TWO_SEGMENT_PARENT_PROTOTYPE_DERIVED',
        'children':children,
        'ordered_child_composition_content_digests':child_digests,
        'composition_content':content,
        'composition_content_digest_sha256':action_result_digest(content),
        'composition_operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
        'composition_depth':2,'child_arity':2,
        'input_parent_depth':1,
        'generic_recursive_closure_authority':'NONE',
        'depth_three_authority':'NONE',
    }
