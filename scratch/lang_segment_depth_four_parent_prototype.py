from __future__ import annotations

from typing import Any

from microseed.development.action_closure import result_digest as action_result_digest

DEPTH_ONE_PARENT_KINDS=(
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE",
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE",
)
DEPTH_THREE_KIND="OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE"


def _depth_three_ancestry_digests(current: dict[str, Any]) -> set[str]:
    out=set()
    for child in current.get("children",()):
        out.add(str(child.get("composition_content_digest_sha256","")))
        for d in child.get("nested_child_content_digests",()):
            out.add(str(d))
    out.discard("")
    return out


def derive_current_depth_four_segment_parent_prototype(m, *, max_records: int = 65536) -> dict[str, Any]:
    base={
        "selection_basis":"LATEST_CURRENT_DEPTH_THREE_PARENT_PLUS_LATEST_CURRENT_EXTERNAL_DEPTH_ONE_PARENT_IN_EVIDENCE_ORDER",
        "grouping_basis":"WHOLE_DEPTH_THREE_AND_DEPTH_ONE_PARENT_BOUNDARIES_PRESERVED",
        "composition_depth":4,"child_arity":2,"max_input_parent_depth":3,"recursive_depth_limit":4,
        "generic_recursive_closure_authority":"NONE","depth_five_authority":"NONE",
        "historical_event_authority":"NONE","ledger_rewrite_authority":"NONE",
        "flattening_authority":"NONE","associativity_authority":"NONE",
        "semantic_composition_authority":"NONE","grammar_authority":"NONE",
        "effect_authority":"NONE","execution_authority":"NONE","scheduler_authority":"NONE","authority_gain":"NONE",
    }
    if max_records<=0:
        return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_FOUR_SCAN_BUDGET_REQUIRED"}
    total=m.evidence.count()
    if total>max_records:
        return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_FOUR_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET","evidence_record_count":total}
    boot=m._current_runtime_boot_seq()
    if boot<0:
        return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED"}
    rows=m.evidence.list(); depth_one=[]; depth_three=[]
    for pos,row in enumerate(rows):
        payload=row.get("payload") or {}
        if int(payload.get("runtime_boot_seq",-1))!=boot:
            continue
        kind=payload.get("kind")
        if kind in DEPTH_ONE_PARENT_KINDS:
            carrier=m._native_depth_one_structural_segment_parent_child_carrier(row,rows=rows,boot=boot)
            if carrier.get("status")!="CURRENT_DEPTH_ONE_STRUCTURAL_SEGMENT_PARENT_CHILD":
                return {**base,**carrier,"status":"DEFER_UNKNOWN"}
            carrier=dict(carrier);carrier["composition_depth"]=1;carrier["evidence_list_position"]=pos;depth_one.append(carrier)
        elif kind==DEPTH_THREE_KIND:
            current=m._validate_current_native_structural_segment_depth_three_recursive_composition_state(row,rows=rows,boot=boot)
            if current.get("status")!="CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE":
                return {**base,**current,"status":"DEFER_UNKNOWN"}
            carrier={
                "status":"CURRENT_DEPTH_THREE_STRUCTURAL_SEGMENT_PARENT_CHILD",
                "source_parent_kind":DEPTH_THREE_KIND,
                "source_parent_evidence_ref":[str(row["evidence_id"]),str(row["sha256"])],
                "composition_content_digest_sha256":str(current["composition_content_digest_sha256"]),
                "composition_depth":3,"child_arity":2,
                "nested_child_content_digests":tuple(str(x) for x in current["ordered_child_composition_content_digests"]),
                "full_ancestry_content_digests":tuple(sorted(_depth_three_ancestry_digests(current))),
                "retrospective_provenance":"CURRENT_APPEND_ONLY_DEPTH_THREE_SEGMENT_PARENT_STATE",
                "historical_event_authority":"NONE","flattening_authority":"NONE",
                "associativity_authority":"NONE","authority_gain":"NONE",
                "evidence_list_position":pos,
            }
            depth_three.append(carrier)
    if not depth_three:
        return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_DEPTH_THREE_SEGMENT_PARENT_REQUIRED"}
    d3=depth_three[-1]
    ancestry=set(d3["full_ancestry_content_digests"])
    ancestry.add(str(d3["composition_content_digest_sha256"]))
    external=[c for c in depth_one if str(c.get("composition_content_digest_sha256","")) not in ancestry]
    if not external:
        return {**base,"status":"DEFER_UNKNOWN","reason":"DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_THREE_ANCESTRY_REQUIRED"}
    d1=external[-1]
    children=tuple(sorted((d3,d1),key=lambda x:int(x["evidence_list_position"])))
    child_digests=tuple(str(c["composition_content_digest_sha256"]) for c in children)
    child_depths=tuple(int(c["composition_depth"]) for c in children)
    content={
        "operator":"RECURSIVE_ORDERED_EVIDENCE_TUPLE",
        "ordered_child_composition_content_digests":list(child_digests),
        "ordered_child_composition_depths":list(child_depths),
        "composition_depth":4,"child_arity":2,
        "identity_scope":"EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY",
    }
    return {
        **base,"status":"CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_PROTOTYPE",
        "composition_content_digest_sha256":action_result_digest(content),
        "ordered_child_composition_content_digests":child_digests,
        "ordered_child_composition_depths":child_depths,
        "children":children,
        "caller_supplied_parent_ids":"NO","caller_supplied_parent_order":"NO",
        "caller_supplied_grouping":"NO","caller_supplied_depth":"NO","caller_supplied_output_evidence_id":"NO",
    }
