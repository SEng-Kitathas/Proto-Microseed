from __future__ import annotations

from typing import Any

from microseed.development.action_closure import result_digest as action_result_digest

DEPTH_ONE_PARENT_KINDS=(
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE",
    "OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE",
)
DEPTH_FOUR_KIND="OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE"


def _depth_four_ancestry_digests(current: dict[str, Any]) -> set[str]:
    out=set()
    for child in current.get("children",()):
        out.add(str(child.get("composition_content_digest_sha256","")))
        for d in child.get("nested_child_content_digests",()): out.add(str(d))
        for d in child.get("full_ancestry_content_digests",()): out.add(str(d))
    out.discard("")
    return out


def derive_current_depth_five_segment_parent_prototype(m, *, max_records: int = 65536) -> dict[str, Any]:
    base={
        "selection_basis":"LATEST_CURRENT_DEPTH_FOUR_PARENT_PLUS_LATEST_CURRENT_EXTERNAL_DEPTH_ONE_PARENT_IN_EVIDENCE_ORDER",
        "grouping_basis":"WHOLE_DEPTH_FOUR_AND_DEPTH_ONE_PARENT_BOUNDARIES_PRESERVED",
        "composition_depth":5,"child_arity":2,"max_input_parent_depth":4,"recursive_depth_limit":5,
        "generic_recursive_closure_authority":"NONE","depth_six_authority":"NONE",
        "historical_event_authority":"NONE","ledger_rewrite_authority":"NONE",
        "flattening_authority":"NONE","associativity_authority":"NONE",
        "semantic_composition_authority":"NONE","grammar_authority":"NONE",
        "effect_authority":"NONE","execution_authority":"NONE","scheduler_authority":"NONE","authority_gain":"NONE",
    }
    if max_records<=0: return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_FIVE_SCAN_BUDGET_REQUIRED"}
    total=m.evidence.count()
    if total>max_records: return {**base,"status":"DEFER_UNKNOWN","reason":"SEGMENT_DEPTH_FIVE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET","evidence_record_count":total}
    boot=m._current_runtime_boot_seq()
    if boot<0: return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_RUNTIME_BOOT_BOUNDARY_REQUIRED"}
    rows=m.evidence.list(); depth_one=[]; depth_four=[]
    for pos,row in enumerate(rows):
        payload=row.get("payload") or {}
        if int(payload.get("runtime_boot_seq",-1))!=boot: continue
        kind=payload.get("kind")
        if kind in DEPTH_ONE_PARENT_KINDS:
            c=m._native_depth_one_structural_segment_parent_child_carrier(row,rows=rows,boot=boot)
            if c.get("status")!="CURRENT_DEPTH_ONE_STRUCTURAL_SEGMENT_PARENT_CHILD": return {**base,**c,"status":"DEFER_UNKNOWN"}
            c=dict(c);c["composition_depth"]=1;c["evidence_list_position"]=pos;depth_one.append(c)
        elif kind==DEPTH_FOUR_KIND:
            cur=m._validate_current_native_structural_segment_depth_four_recursive_composition_state(row,rows=rows,boot=boot)
            if cur.get("status")!="CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE": return {**base,**cur,"status":"DEFER_UNKNOWN"}
            ancestry=_depth_four_ancestry_digests(cur)
            c={
                "status":"CURRENT_DEPTH_FOUR_STRUCTURAL_SEGMENT_PARENT_CHILD",
                "source_parent_kind":DEPTH_FOUR_KIND,
                "source_parent_evidence_ref":[str(row["evidence_id"]),str(row["sha256"])],
                "composition_content_digest_sha256":str(cur["composition_content_digest_sha256"]),
                "composition_depth":4,"child_arity":2,
                "nested_child_content_digests":tuple(str(x) for x in cur["ordered_child_composition_content_digests"]),
                "full_ancestry_content_digests":tuple(sorted(ancestry)),
                "retrospective_provenance":"CURRENT_APPEND_ONLY_DEPTH_FOUR_SEGMENT_PARENT_STATE",
                "historical_event_authority":"NONE","flattening_authority":"NONE","associativity_authority":"NONE","authority_gain":"NONE",
                "evidence_list_position":pos,
            }
            depth_four.append(c)
    if not depth_four: return {**base,"status":"DEFER_UNKNOWN","reason":"CURRENT_DEPTH_FOUR_SEGMENT_PARENT_REQUIRED"}
    d4=depth_four[-1]; ancestry=set(d4["full_ancestry_content_digests"]);ancestry.add(str(d4["composition_content_digest_sha256"]))
    external=[c for c in depth_one if str(c["composition_content_digest_sha256"]) not in ancestry]
    if not external: return {**base,"status":"DEFER_UNKNOWN","reason":"DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_FOUR_ANCESTRY_REQUIRED"}
    d1=external[-1];children=tuple(sorted((d4,d1),key=lambda x:int(x["evidence_list_position"])))
    child_digests=tuple(str(c["composition_content_digest_sha256"]) for c in children);child_depths=tuple(int(c["composition_depth"]) for c in children)
    content={"operator":"RECURSIVE_ORDERED_EVIDENCE_TUPLE","ordered_child_composition_content_digests":list(child_digests),"ordered_child_composition_depths":list(child_depths),"composition_depth":5,"child_arity":2,"identity_scope":"EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY"}
    return {**base,"status":"CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_PROTOTYPE","composition_content_digest_sha256":action_result_digest(content),"ordered_child_composition_content_digests":child_digests,"ordered_child_composition_depths":child_depths,"children":children,"caller_supplied_parent_ids":"NO","caller_supplied_parent_order":"NO","caller_supplied_grouping":"NO","caller_supplied_depth":"NO","caller_supplied_output_evidence_id":"NO"}
