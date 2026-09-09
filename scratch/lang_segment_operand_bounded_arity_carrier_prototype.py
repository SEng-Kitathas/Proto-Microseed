from __future__ import annotations

from typing import Any
from microseed.development.action_closure import result_digest as action_result_digest


def derive_current_bounded_structural_segment_child_carriers(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only bounded 2..4 segment-side child projection.

    The caller supplies no segment id, split, side, leaf arity, child order, grouping or output id.
    Every segment and boundary row is revalidated through production currentness owners. LEFT and
    RIGHT remain two grouped parent operands regardless of each child's internal leaf arity.
    """
    base={
        'selection_basis':'CURRENT_STRUCTURAL_SEGMENT_STATE_EVIDENCE_APPEND_ORDER_THEN_LEFT_RIGHT',
        'grouping_basis':'EXACT_SEGMENT_STATE_LEFT_RIGHT_BOUNDARY_PRESERVED',
        'bounded_min_leaf_arity':2,'bounded_max_leaf_arity':4,'parent_child_count':2,
        'recursive_depth_limit':1,
        'caller_supplied_segment_state_id':'NO','caller_supplied_split':'NO','caller_supplied_side':'NO',
        'caller_supplied_leaf_arity':'NO','caller_supplied_child_order':'NO','caller_supplied_grouping':'NO',
        'historical_event_authority':'NONE','ledger_rewrite_authority':'NONE',
        'flattening_authority':'NONE','associativity_authority':'NONE',
        'semantic_composition_authority':'NONE','grammar_authority':'NONE',
        'scheduler_authority':'NONE','execution_authority':'NONE','effect_authority':'NONE','authority_gain':'NONE',
    }
    bound=int(max_records)
    if bound<=0:
        return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_BOUNDED_CHILD_EVIDENCE_SCAN_BUDGET_REQUIRED'}
    total=m.evidence.count()
    if total>bound:
        return {**base,'status':'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED','reason':'SEGMENT_BOUNDED_CHILD_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET','total_records':total,'max_records':bound}
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
        boundary_row=m.evidence.get(str(current['boundary_evidence_id']))
        if boundary_row is None or str(boundary_row.get('sha256',''))!=str(current['boundary_evidence_sha256']):
            return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_BOUNDED_CHILD_BOUNDARY_REF_NOT_EXACT'}
        boundary=m._validate_current_native_structural_boundary_witness(boundary_row,rows=rows,boot=boot)
        if boundary.get('status')!='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS':
            return {**base,**boundary,'status':'DEFER_UNKNOWN'}
        split=int(current['split_index']); components=tuple(boundary['components'])
        specs=(
            ('LEFT',current['left_content'],current['left_composition_content_digest_sha256'],components[:split]),
            ('RIGHT',current['right_content'],current['right_composition_content_digest_sha256'],components[split:]),
        )
        local=[]
        for side_ordinal,(side,content,digest,source_components) in enumerate(specs):
            ordered=tuple(str(x) for x in content.get('ordered_operational_referent_signatures',()))
            leaf_arity=int(content.get('arity',-1))
            if (content.get('operator')!='ORDERED_EVIDENCE_TUPLE' or leaf_arity!=len(ordered)
                    or not (2<=leaf_arity<=4) or len(source_components)!=leaf_arity
                    or len(set(ordered))!=leaf_arity):
                return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_SIDE_NOT_BOUNDED_DISTINCT_ORDERED_COMPOSITION_CONTENT','segment_state_evidence_id':str(row.get('evidence_id','')),'side':side,'leaf_arity':leaf_arity}
            expected=action_result_digest({
                'operator':'ORDERED_EVIDENCE_TUPLE',
                'ordered_operational_referent_signatures':list(ordered),
                'arity':leaf_arity,'identity_scope':'OPERATIONAL_EQUIVALENCE_CLASS_ONLY',
            })
            if expected!=str(digest):
                return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_SIDE_BOUNDED_CONTENT_DIGEST_MISMATCH','side':side,'leaf_arity':leaf_arity}
            validated=[]
            for local_ordinal,(component,referent_sig) in enumerate(zip(source_components,ordered)):
                if (not isinstance(component,dict)
                        or str(component.get('operational_referent_signature_sha256',''))!=referent_sig):
                    return {**base,'status':'DEFER_UNKNOWN','reason':'SEGMENT_SIDE_SOURCE_COMPONENT_MISMATCH','side':side,'leaf_arity':leaf_arity}
                validated.append({
                    'ordinal':local_ordinal,
                    'source_boundary_component_ordinal':int(component.get('ordinal',-1)),
                    'opaque_token':str(component.get('opaque_token','')),
                    'operational_referent_signature_sha256':referent_sig,
                    'association_record_id':str(component.get('association_record_id','')),
                    'token_evidence_ref':list(component.get('token_evidence_ref',())),
                    'profile_evidence_ref':list(component.get('profile_evidence_ref',())),
                    'token_store_event_seq':int(component.get('token_store_event_seq',-1)),
                })
            local.append({
                'carrier_kind':'CURRENT_STRUCTURAL_SEGMENT_BOUNDED_GROUPED_COMPOSITION_CHILD',
                'ordinal':side_ordinal,'source_side':side,'leaf_arity':leaf_arity,
                'composition_content_digest_sha256':expected,
                'ordered_operational_referent_signatures':list(ordered),
                'validated_components':validated,
                'source_segment_state_evidence_ref':[str(row['evidence_id']),str(row['sha256'])],
                'source_boundary_evidence_ref':[str(current['boundary_evidence_id']),str(current['boundary_evidence_sha256'])],
                'retrospective_provenance':'CURRENT_APPEND_ONLY_STRUCTURAL_SEGMENT_STATE_SIDE',
                'historical_event_authority':'NONE','flattening_authority':'NONE','associativity_authority':'NONE',
            })
        if len(local)!=2 or tuple(c['source_side'] for c in local)!=('LEFT','RIGHT'):
            return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_LEFT_RIGHT_GROUPED_CHILD_PAIR_REQUIRED'}
        carriers.extend(local)
    if not carriers:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_STRUCTURAL_SEGMENT_STATE_REQUIRED'}
    return {**base,'status':'CURRENT_BOUNDED_STRUCTURAL_SEGMENT_CHILD_CARRIERS_DERIVED','carriers':tuple(carriers),'carrier_count':len(carriers)}


def derive_current_bounded_structural_segment_recursive_parent_prototypes(m, *, max_records: int = 4096) -> dict[str, Any]:
    """Read-only parent prototype: exactly two grouped segment-side children, fixed depth one."""
    base=derive_current_bounded_structural_segment_child_carriers(m,max_records=max_records)
    if base.get('status')!='CURRENT_BOUNDED_STRUCTURAL_SEGMENT_CHILD_CARRIERS_DERIVED':
        return base
    grouped={}; order=[]
    for c in base['carriers']:
        sid=str(c['source_segment_state_evidence_ref'][0])
        if sid not in grouped:
            grouped[sid]=[]; order.append(sid)
        grouped[sid].append(c)
    parents=[]; skipped=[]
    for sid in order:
        children=grouped[sid]
        if len(children)!=2 or tuple(c['source_side'] for c in children)!=('LEFT','RIGHT'):
            return {**base,'status':'DEFER_UNKNOWN','reason':'EXACT_LEFT_RIGHT_GROUPED_CHILD_PAIR_REQUIRED','segment_state_evidence_id':sid}
        child_digests=tuple(str(c['composition_content_digest_sha256']) for c in children)
        if len(set(child_digests))!=2:
            skipped.append({'segment_state_evidence_id':sid,'reason':'TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED','child_leaf_arities':tuple(c['leaf_arity'] for c in children)})
            continue
        content={
            'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'ordered_child_composition_content_digests':list(child_digests),
            'composition_depth':1,'child_arity':2,
            'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
        }
        parents.append({
            'carrier_kind':'CURRENT_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_PARENT_PROTOTYPE',
            'source_segment_state_evidence_ref':children[0]['source_segment_state_evidence_ref'],
            'source_boundary_evidence_ref':children[0]['source_boundary_evidence_ref'],
            'children':tuple(children),
            'child_leaf_arities':tuple(int(c['leaf_arity']) for c in children),
            'ordered_child_composition_content_digests':child_digests,
            'composition_content':content,
            'composition_content_digest_sha256':action_result_digest(content),
            'composition_operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'composition_depth':1,'child_arity':2,
            'flattening_authority':'NONE','associativity_authority':'NONE',
            'historical_event_authority':'NONE','authority_gain':'NONE',
        })
    if not parents:
        return {**base,'status':'DEFER_UNKNOWN','reason':'CURRENT_DISTINCT_BOUNDED_SEGMENT_CHILD_PAIR_REQUIRED','skipped':tuple(skipped)}
    return {**base,'status':'CURRENT_BOUNDED_STRUCTURAL_SEGMENT_RECURSIVE_PARENT_PROTOTYPES_DERIVED','parents':tuple(parents),'parent_count':len(parents),'skipped':tuple(skipped)}
