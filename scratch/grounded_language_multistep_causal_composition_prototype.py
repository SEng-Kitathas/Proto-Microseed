from __future__ import annotations

from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_language_concept_formation_prototype import resolve_owned_concept
from scratch.grounded_language_causal_composition_prototype import NONE,_sha,_current_relation


def _owned_coupling_payload(ms,coupling_set:dict[str,Any])->tuple[dict[str,Any]|None,dict[str,Any]|None]:
    if coupling_set.get("status")!="OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY":
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_ACTION_CONCEPT_COUPLING_SET_REQUIRED"}
    row=ms.evidence.get(str(coupling_set.get("coupling_evidence_id","")))
    if row is None or row.get("sha256")!=coupling_set.get("coupling_evidence_sha256") or row.get("payload",{}).get("coupling_set_id")!=coupling_set.get("coupling_set_id"):
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_ACTION_CONCEPT_COUPLING_EVIDENCE_REQUIRED"}
    return dict(row["payload"]),None


def _current_coupling_relation(ms,coupling:dict[str,Any])->tuple[dict[str,Any]|None,dict[str,Any]|None]:
    relation,status=_current_relation(ms,str(coupling["relation_id"]))
    if relation is None:return None,status
    if _sha(relation)!=str(coupling["relation_snapshot_sha256"]):
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_RELATION_SNAPSHOT_DISAGREES_WITH_CHAIN_PREMISE","relation_id":str(coupling["relation_id"])}
    return relation,None


def derive_owned_two_step_language_causal_chain(ms,coupling_set:dict[str,Any],*,first_relation_id:str,second_relation_id:str,evidence_id:str="E-VEYA-P05-TWO-STEP-CHAIN")->dict[str,Any]:
    payload,err=_owned_coupling_payload(ms,coupling_set)
    if err:return err
    selected=[]
    for rid in (str(first_relation_id),str(second_relation_id)):
        m=[c for c in payload["couplings"] if c["relation_id"]==rid]
        if len(m)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"CHAIN_RELATION_NOT_UNIQUELY_OWNED_IN_COUPLING_SET","relation_id":rid}
        selected.append(m[0])
    if selected[0]["relation_id"]==selected[1]["relation_id"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_DISTINCT_EMPIRICAL_RELATIONS_REQUIRED"}
    r1,err=_current_coupling_relation(ms,selected[0]);
    if err:return err
    r2,err=_current_coupling_relation(ms,selected[1]);
    if err:return err
    if str(r1["next_state_id"])!=str(r2["start_state_id"]):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EMPIRICAL_RELATION_STATE_JOIN_REQUIRED","first_next_state_id":str(r1["next_state_id"]),"second_start_state_id":str(r2["start_state_id"])}
    chain={
        "kind":"OWNED_VEYA_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN",
        "chain_id":"VEYA-P05-CHAIN-"+_sha({"relations":[r1["relation_id"],r2["relation_id"]],"concepts":[selected[0]["concept_content_digest_sha256"],selected[1]["concept_content_digest_sha256"]]})[:24],
        "coupling_set_id":payload["coupling_set_id"],
        "coupling_evidence_id":str(coupling_set["coupling_evidence_id"]),
        "coupling_evidence_sha256":str(coupling_set["coupling_evidence_sha256"]),
        "concept_set_id":payload["concept_set_id"],
        "concept_evidence_id":payload["concept_evidence_id"],
        "concept_evidence_sha256":payload["concept_evidence_sha256"],
        "relation_ids":[r1["relation_id"],r2["relation_id"]],
        "relation_snapshot_sha256":[selected[0]["relation_snapshot_sha256"],selected[1]["relation_snapshot_sha256"]],
        "capability_sequence":[r1["capability_id"],r2["capability_id"]],
        "state_path":[r1["start_state_id"],r1["next_state_id"],r2["next_state_id"]],
        "step_value_effects":[float(r1["value_effect"]),float(r2["value_effect"])],
        "cumulative_value_effect":round(float(r1["value_effect"])+float(r2["value_effect"]),6),
        "concept_content_digest_sequence":[selected[0]["concept_content_digest_sha256"],selected[1]["concept_content_digest_sha256"]],
        "chain_basis":"TWO_CURRENT_EVIDENCE_BOUND_PREDICTIVE_RELATIONS_WITH_EXACT_STATE_JOIN_PLUS_OWNED_ACTION_CONCEPT_COUPLINGS",
        "counterfactual_scope":"BOUNDED_TWO_STEP_EMPIRICAL_COMPOSITION_ONLY",
        "causal_theorem_authority":"NONE",
        "general_causal_learner_authority":"NONE",
        "planner_authority":"NONE",
        "execution_authority":"NONE",
        "truth_authority":"NONE",
        "value_priority_authority":"NONE",
        "external_oracle_authority":"NONE",
        "authority_gain":"NONE",
    }
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,chain,EpistemicStatus.PRESSURE_SUPPORTED,source="VEYA-P05-GROUNDED-LANGUAGE-MULTISTEP-CAUSAL-CHAIN")
        sha=ref.sha256
    else:
        if existing.get("negative") or existing.get("payload")!=chain:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_STEP_CHAIN_EVIDENCE_ID_COLLISION"}
        sha=str(existing.get("sha256",""))
    return {**NONE,"status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN_RESEARCH_ONLY","chain_id":chain["chain_id"],"chain_evidence_id":evidence_id,"chain_evidence_sha256":sha,**{k:chain[k] for k in ("coupling_set_id","concept_set_id","relation_ids","relation_snapshot_sha256","capability_sequence","state_path","step_value_effects","cumulative_value_effect","concept_content_digest_sequence","chain_basis","counterfactual_scope")}}


def _chain_payload(ms,chain:dict[str,Any])->tuple[dict[str,Any]|None,dict[str,Any]|None]:
    if chain.get("status")!="OWNED_GROUNDED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_CHAIN_RESEARCH_ONLY":
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_TWO_STEP_CAUSAL_CHAIN_REQUIRED"}
    row=ms.evidence.get(str(chain.get("chain_evidence_id","")))
    if row is None or row.get("sha256")!=chain.get("chain_evidence_sha256") or row.get("payload",{}).get("chain_id")!=chain.get("chain_id"):
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_TWO_STEP_CHAIN_EVIDENCE_REQUIRED"}
    return dict(row["payload"]),None


def compose_owned_chain_with_language(ms,chain:dict[str,Any],surface_tokens:tuple[str,str])->dict[str,Any]:
    cp,err=_chain_payload(ms,chain)
    if err:return err
    if len(surface_tokens)!=2:return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_TWO_LANGUAGE_CONCEPT_INDICES_REQUIRED"}
    cset={"status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY","concept_set_id":cp["concept_set_id"],"concept_evidence_id":cp["concept_evidence_id"],"concept_evidence_sha256":cp["concept_evidence_sha256"]}
    resolved=[]
    for token in surface_tokens:
        c=resolve_owned_concept(ms,cset,str(token))
        if c.get("status")!="OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY":return {**NONE,**c,"status":"DEFER_UNKNOWN"}
        resolved.append(c)
    if [c["concept_content_digest_sha256"] for c in resolved]!=list(cp["concept_content_digest_sequence"]):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"LANGUAGE_CONCEPT_SEQUENCE_DISAGREES_WITH_OWNED_CAUSAL_CHAIN"}
    for rid,snap in zip(cp["relation_ids"],cp["relation_snapshot_sha256"]):
        r,status=_current_relation(ms,rid)
        if r is None:return status
        if _sha(r)!=snap:return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_RELATION_SNAPSHOT_DISAGREES_WITH_CHAIN","relation_id":rid}
    return {**NONE,"status":"CURRENT_OWNED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_COMPOSITION_RESEARCH_ONLY","chain_id":cp["chain_id"],"surface_tokens":list(surface_tokens),"state_path":list(cp["state_path"]),"capability_sequence":list(cp["capability_sequence"]),"step_value_effects":list(cp["step_value_effects"]),"cumulative_value_effect":cp["cumulative_value_effect"],"concept_content_digest_sequence":list(cp["concept_content_digest_sequence"]),"prediction_scope":"BOUNDED_TWO_STEP_EMPIRICAL_CHAIN_ONLY"}


def evaluate_counterfactual_language_sequence(ms,coupling_set:dict[str,Any],surface_tokens:tuple[str,str])->dict[str,Any]:
    payload,err=_owned_coupling_payload(ms,coupling_set)
    if err:return err
    if len(surface_tokens)!=2:return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_TWO_LANGUAGE_CONCEPT_INDICES_REQUIRED"}
    cset={"status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY","concept_set_id":payload["concept_set_id"],"concept_evidence_id":payload["concept_evidence_id"],"concept_evidence_sha256":payload["concept_evidence_sha256"]}
    resolved=[]
    for token in surface_tokens:
        c=resolve_owned_concept(ms,cset,str(token))
        if c.get("status")!="OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY":return {**NONE,**c,"status":"DEFER_UNKNOWN"}
        resolved.append(c)
    couplings=[]
    for c in resolved:
        m=[x for x in payload["couplings"] if x["concept_content_digest_sha256"]==c["concept_content_digest_sha256"]]
        if len(m)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"LANGUAGE_CONCEPT_DOES_NOT_UNIQUELY_INDEX_EMPIRICAL_COUPLING"}
        couplings.append(m[0])
    relations=[]
    for c in couplings:
        r,err=_current_coupling_relation(ms,c)
        if err:return err
        relations.append(r)
    if str(relations[0]["next_state_id"])!=str(relations[1]["start_state_id"]):
        return {**NONE,"status":"COUNTERFACTUAL_CHAIN_INFEASIBLE_RESEARCH_ONLY","reason":"EMPIRICAL_STATE_JOIN_MISMATCH","surface_tokens":list(surface_tokens),"first_relation_id":relations[0]["relation_id"],"second_relation_id":relations[1]["relation_id"],"first_next_state_id":relations[0]["next_state_id"],"second_start_state_id":relations[1]["start_state_id"],"counterfactual_scope":"BOUNDED_RELATION_ORDER_ONLY"}
    return {**NONE,"status":"BOUNDED_COUNTERFACTUAL_LANGUAGE_CAUSAL_CHAIN_RESEARCH_ONLY","surface_tokens":list(surface_tokens),"relation_ids":[r["relation_id"] for r in relations],"state_path":[relations[0]["start_state_id"],relations[0]["next_state_id"],relations[1]["next_state_id"]],"cumulative_value_effect":round(float(relations[0]["value_effect"])+float(relations[1]["value_effect"]),6),"counterfactual_scope":"BOUNDED_RELATION_ORDER_ONLY"}


def validate_two_step_chain_against_actual_holdout(ms,composition:dict[str,Any],first_outcome_evidence_id:str,second_outcome_evidence_id:str)->dict[str,Any]:
    if composition.get("status")!="CURRENT_OWNED_LANGUAGE_MEDIATED_TWO_STEP_CAUSAL_COMPOSITION_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_TWO_STEP_COMPOSITION_REQUIRED"}
    rows=[]
    for eid in (first_outcome_evidence_id,second_outcome_evidence_id):
        r=ms.evidence.get(str(eid))
        if r is None or r.get("negative"):return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_POSITIVE_CHAIN_HOLDOUT_EVIDENCE_REQUIRED"}
        rows.append(r)
    p1,p2=(dict(r.get("payload") or {}) for r in rows)
    observed_path=[str(p1.get("start_state_id")),str(p1.get("next_state_id")),str(p2.get("next_state_id"))]
    if str(p1.get("next_state_id"))!=str(p2.get("start_state_id")):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTUAL_HOLDOUT_STATE_JOIN_MISMATCH"}
    effect=round(float(p1.get("actual_value_effect"))+float(p2.get("actual_value_effect")),6)
    observed_caps=[str(p1.get("capability_id")),str(p2.get("capability_id"))]
    matched=(observed_path==list(composition["state_path"]) and observed_caps==list(composition["capability_sequence"]) and effect==round(float(composition["cumulative_value_effect"]),6))
    return {**NONE,"status":"TWO_STEP_CHAIN_HOLDOUT_MATCH" if matched else "TWO_STEP_CHAIN_HOLDOUT_VIOLATION","matched":matched,"predicted_state_path":list(composition["state_path"]),"observed_state_path":observed_path,"predicted_capability_sequence":list(composition["capability_sequence"]),"observed_capability_sequence":observed_caps,"predicted_cumulative_value_effect":composition["cumulative_value_effect"],"observed_cumulative_value_effect":effect,"holdout_evidence_ids":[str(first_outcome_evidence_id),str(second_outcome_evidence_id)]}


def inspect_owned_chain_without_language(ms,chain:dict[str,Any])->dict[str,Any]:
    cp,err=_chain_payload(ms,chain)
    if err:return err
    return {**NONE,"status":"OWNED_TWO_STEP_CAUSAL_CHAIN_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX","state_path":list(cp["state_path"]),"relation_ids":list(cp["relation_ids"]),"concept_content_digest_sequence":list(cp["concept_content_digest_sequence"]),"cumulative_value_effect":cp["cumulative_value_effect"],"lexical_retrieval_available":False}


def attempt_text_only_multistep_causal_chain(text:str)->dict[str,Any]:
    return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_CURRENT_EMPIRICAL_RELATIONS_AND_OWNED_CAUSAL_CHAIN_REQUIRED","surface_text":str(text)}
