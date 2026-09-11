from __future__ import annotations

from typing import Any

from microseed.development.action_closure import result_digest as action_result_digest

DEPTH_ONE_PARENT_KINDS=(
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE",
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE",
)
DEPTH_TWO_KIND="OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE"


def derive_current_depth_three_segment_parent_prototype(m, *, max_records: int = 65536) -> dict[str, Any]:
    base={
        "selection_basis":"LATEST_CURRENT_DEPTH_TWO_PARENT_PLUS_LATEST_CURRENT_EXTERNAL_DEPTH_ONE_PARENT_IN_EVIDENCE_ORDER",
        "grouping_basis":"WHOLE_DEPTH_TWO_AND_DEPTH_ONE_PARENT_BOUNDARIES_PRESERVED",
        "composition_depth":3,
        "child_arity":2,
        "max_input_parent_depth":2,
        "recursive_depth_limit":3,
        "generic_recursive_closure_authority":"NONE",
        "depth_four_authority":"NONE",
        "historical_event_authority":"NONE",
        "ledger_rewrite_authority":"NONE",
        "flattening_authority":"NONE",
        "associativity_authority":"NONE",
        "semantic_composition_authority":"NONE",
        "grammar_authority":"NONE",
        "effect_authority":"NONE",
        "execution_authority":"NONE",
        "scheduler_authority":"NONE",
        "authority_gain":"NONE",
    }
    if max_records<=0:
        return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_THREE_SCAN_BUDGET_REQUIRED"}
    total=m.evidence.count()
    if total>max_records:
        return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_THREE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET","evidence_record_count":total}
    boot=m._current_runtime_boot_seq()
    if boot<0:
        return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED"}
    rows=m.evidence.list()
    depth_one=[]
    depth_two=[]
    for pos,row in enumerate(rows):
        payload=row.get("payload") or {}
        if int(payload.get("runtime_boot_seq",-1))!=boot:
            continue
        kind=payload.get("kind")
        if kind in DEPTH_ONE_PARENT_KINDS:
            carrier=m._native_depth_one_structural_segment_parent_child_carrier(row,rows=rows,boot=boot)
            if carrier.get("status")!="CURRENT_DEPTH_ONE_STRUCTURAL_SEGMENT_PARENT_CHILD":
                return {**base,**carrier,"status":"DEFER_UNKNOWN"}
            carrier=dict(carrier)
            carrier["evidence_list_position"]=pos
            carrier["composition_depth"]=1
            depth_one.append(carrier)
        elif kind==DEPTH_TWO_KIND:
            current=m._validate_current_native_structural_segment_depth_two_recursive_composition_state(row,rows=rows,boot=boot)
            if current.get("status")!="CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE":
                return {**base,**current,"status":"DEFER_UNKNOWN"}
            current=dict(current)
            current["evidence_list_position"]=pos
            current["composition_depth"]=2
            depth_two.append(current)
    if not depth_two:
        return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_DEPTH_TWO_SEGMENT_PARENT_REQUIRED"}
    d2=depth_two[-1]
    nested=set(str(x) for x in d2.get("ordered_child_composition_content_digests",()))
    external=[c for c in depth_one if str(c.get("composition_content_digest_sha256","")) not in nested]
    if not external:
        return {**base,"status":"DEFER_UNKNOWN","reason":"DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_REQUIRED"}
    d1=external[-1]
    children=[]
    for c in sorted((d2,d1),key=lambda x:int(x["evidence_list_position"])):
        if int(c.get("composition_depth",-1))==2:
            children.append({
                "source_kind":DEPTH_TWO_KIND,
                "source_evidence_ref":[str(c["composition_state_evidence_id"]),str(c["composition_state_evidence_sha256"])],
                "composition_content_digest_sha256":str(c["composition_content_digest_sha256"]),
                "composition_depth":2,
                "child_arity":2,
                "nested_child_content_digests":list(c["ordered_child_composition_content_digests"]),
                "retrospective_provenance":"CURRENT_APPEND_ONLY_DEPTH_TWO_SEGMENT_PARENT_STATE",
                "historical_event_authority":"NONE","flattening_authority":"NONE",
                "associativity_authority":"NONE","authority_gain":"NONE",
            })
        else:
            children.append({
                "source_kind":str(c["source_parent_kind"]),
                "source_evidence_ref":list(c["source_parent_evidence_ref"]),
                "source_segment_state_evidence_ref":list(c["source_segment_state_evidence_ref"]),
                "source_boundary_evidence_ref":list(c["source_boundary_evidence_ref"]),
                "composition_content_digest_sha256":str(c["composition_content_digest_sha256"]),
                "composition_depth":1,
                "child_arity":2,
                "nested_child_content_digests":list(c["nested_child_content_digests"]),
                "retrospective_provenance":"CURRENT_APPEND_ONLY_DEPTH_ONE_SEGMENT_PARENT_STATE",
                "historical_event_authority":"NONE","flattening_authority":"NONE",
                "associativity_authority":"NONE","authority_gain":"NONE",
            })
    child_depths=[int(c["composition_depth"]) for c in children]
    child_digests=[str(c["composition_content_digest_sha256"]) for c in children]
    content={
        "operator":"RECURSIVE_ORDERED_EVIDENCE_TUPLE",
        "ordered_child_composition_content_digests":child_digests,
        "ordered_child_composition_depths":child_depths,
        "composition_depth":3,
        "child_arity":2,
        "identity_scope":"EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY",
    }
    digest=action_result_digest(content)
    return {
        **base,
        "status":"CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_PROTOTYPE",
        "composition_content_digest_sha256":digest,
        "ordered_child_composition_content_digests":tuple(child_digests),
        "ordered_child_composition_depths":tuple(child_depths),
        "children":tuple(children),
        "caller_supplied_parent_ids":"NO",
        "caller_supplied_parent_order":"NO",
        "caller_supplied_grouping":"NO",
        "caller_supplied_depth":"NO",
        "caller_supplied_output_evidence_id":"NO",
    }
