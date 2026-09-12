from __future__ import annotations

from typing import Any

from microseed import EpistemicStatus
from scratch.grounded_language_concept_formation_prototype import _sha, resolve_owned_concept

NONE={
    "language_authority":"NONE",
    "semantic_reference_authority":"NONE",
    "predicate_authority":"NONE",
    "truth_authority":"NONE",
    "causal_theorem_authority":"NONE",
    "general_causal_learner_authority":"NONE",
    "execution_authority":"NONE",
    "planner_authority":"NONE",
    "value_priority_authority":"NONE",
    "external_oracle_authority":"NONE",
    "authority_gain":"NONE",
}


def _current_relation(ms,relation_id:str)->tuple[dict[str,Any]|None,dict[str,Any]]:
    status=ms.action_outcome_predictive_relation_status(str(relation_id))
    if status.get("status")!="CURRENT_PREDICTIVE_RELATION":
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_ACTION_OUTCOME_PREDICTIVE_RELATION_REQUIRED","relation_status":status}
    r=ms.action_outcome_learning.relations.get(str(relation_id))
    if r is None:
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"PREDICTIVE_RELATION_OBJECT_NOT_FOUND"}
    packet=r.serializable()
    if packet.get("truth_authority")!="NONE" or packet.get("causal_theorem_authority")!="NONE" or packet.get("execution_authority")!="NONE":
        return None,{**NONE,"status":"DEFER_UNKNOWN","reason":"PREDICTIVE_RELATION_AUTHORITY_OVERCLAIM"}
    return packet,status


def _concept_shell(concept_set:dict[str,Any])->dict[str,Any]:
    return {
        "status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY",
        "concept_set_id":concept_set.get("concept_set_id"),
        "concept_evidence_id":concept_set.get("concept_evidence_id"),
        "concept_evidence_sha256":concept_set.get("concept_evidence_sha256"),
    }


def grounded_action_concept_observation(
    ms,
    *,
    relation_id:str,
    action_outcome_evidence_id:str,
    concept_set:dict[str,Any],
    surface_token:str,
    grounded_sequence_episode:dict[str,Any],
)->dict[str,Any]:
    """Bind one actual observed action outcome to one grounded learned concept observation.

    The action relation and concept must both already be CURRENT/owned. The language token indexes
    the concept; it cannot manufacture the outcome relation or change concept content.
    """
    relation,relation_status=_current_relation(ms,relation_id)
    if relation is None:
        return relation_status
    erow=ms.evidence.get(str(action_outcome_evidence_id))
    if erow is None or erow.get("negative"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_POSITIVE_ACTION_OUTCOME_EVIDENCE_REQUIRED"}
    ep=dict(erow.get("payload") or {})
    if (
        str(ep.get("start_state_id"))!=str(relation.get("start_state_id"))
        or str(ep.get("capability_id"))!=str(relation.get("capability_id"))
        or int(ep.get("capability_epoch",-1))!=int(relation.get("capability_epoch",-2))
        or str(ep.get("next_state_id"))!=str(relation.get("next_state_id"))
        or round(float(ep.get("actual_value_effect",999999.0)),6)!=round(float(relation.get("value_effect",-999999.0)),6)
    ):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTION_OUTCOME_DOES_NOT_MATCH_CURRENT_EMPIRICAL_RELATION"}
    concept=resolve_owned_concept(ms,_concept_shell(concept_set),str(surface_token))
    if concept.get("status")!="OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY":
        return {**NONE,**concept,"status":"DEFER_UNKNOWN"}
    seq=grounded_sequence_episode
    if seq.get("status")!="CURRENT_GROUNDED_LANGUAGE_RELATION_SEQUENCE_EPISODE":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_GROUNDED_CONCEPT_OBSERVATION_REQUIRED"}
    if str(seq.get("sequence_sha256",""))!=_sha(seq.get("payload",{})):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"GROUNDED_CONCEPT_OBSERVATION_CONTENT_HASH_MISMATCH"}
    observed_pattern=tuple(int(x) for x in seq["payload"]["relation_transform_permutation"])
    concept_pattern=tuple(int(x) for x in concept["grounded_concept_content"]["relation_transform_permutation"])
    if observed_pattern!=concept_pattern:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"GROUNDED_OBSERVATION_DISAGREES_WITH_LANGUAGE_INDEXED_CONCEPT"}
    payload={
        "relation_id":str(relation["relation_id"]),
        "relation_snapshot_sha256":_sha(relation),
        "relation_capability_id":str(relation["capability_id"]),
        "relation_start_state_id":str(relation["start_state_id"]),
        "relation_next_state_id":str(relation["next_state_id"]),
        "relation_value_effect":float(relation["value_effect"]),
        "action_outcome_evidence_id":str(erow["evidence_id"]),
        "action_outcome_evidence_sha256":str(erow["sha256"]),
        "concept_set_id":str(concept_set["concept_set_id"]),
        "concept_evidence_id":str(concept_set["concept_evidence_id"]),
        "concept_evidence_sha256":str(concept_set["concept_evidence_sha256"]),
        "surface_token":str(surface_token),
        "concept_content_digest_sha256":str(concept["concept_content_digest_sha256"]),
        "grounded_concept_content":dict(concept["grounded_concept_content"]),
        "grounded_sequence_sha256":str(seq["sequence_sha256"]),
    }
    pair_sha=_sha(payload)
    pair_evidence_id="E-VEYA-P04-ACTION-CONCEPT-PAIR-"+pair_sha[:24]
    existing=ms.evidence.get(pair_evidence_id)
    pair_record={
        "kind":"OWNED_VEYA_GROUNDED_ACTION_CONCEPT_OBSERVATION",
        "pair_sha256":pair_sha,
        "payload":payload,
        "authority_gain":"NONE",
        "causal_theorem_authority":"NONE",
    }
    if existing is None:
        ref=ms.append_evidence(pair_evidence_id,pair_record,EpistemicStatus.PRESSURE_SUPPORTED,source="VEYA-P04-GROUNDED-ACTION-CONCEPT-OBSERVATION")
        pair_evidence_sha=ref.sha256
    else:
        if existing.get("negative") or existing.get("payload")!=pair_record:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTION_CONCEPT_PAIR_EVIDENCE_ID_COLLISION"}
        pair_evidence_sha=str(existing.get("sha256",""))
    return {**NONE,"status":"CURRENT_GROUNDED_ACTION_CONCEPT_OBSERVATION_RESEARCH_ONLY","payload":payload,"pair_sha256":pair_sha,"pair_evidence_id":pair_evidence_id,"pair_evidence_sha256":pair_evidence_sha}


def derive_owned_action_concept_couplings(
    ms,
    train_pairs:list[dict[str,Any]],
    holdout_pairs:list[dict[str,Any]],
    *,
    evidence_id:str="E-VEYA-P04-ACTION-CONCEPT-COUPLING-SET",
)->dict[str,Any]:
    """Learn a bounded empirical action-relation -> grounded-concept coupling.

    This is evidence-bound predictive composition, never a general causal theorem.
    """
    if len(train_pairs)<8:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_ACTION_CONCEPT_TRAINING_HISTORY_REQUIRED"}
    if len(holdout_pairs)<4:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"INDEPENDENT_ACTION_CONCEPT_HOLDOUT_REQUIRED"}
    rows=tuple(train_pairs)+tuple(holdout_pairs)
    if any(r.get("status")!="CURRENT_GROUNDED_ACTION_CONCEPT_OBSERVATION_RESEARCH_ONLY" for r in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_ACTION_CONCEPT_EXEMPLAR_MUST_BE_CURRENT_AND_GROUNDED"}
    if any(str(r.get("pair_sha256",""))!=_sha(r.get("payload",{})) for r in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTION_CONCEPT_EXEMPLAR_CONTENT_HASH_MISMATCH"}
    for r in rows:
        stored_pair=ms.evidence.get(str(r.get("pair_evidence_id","")))
        expected_record={
            "kind":"OWNED_VEYA_GROUNDED_ACTION_CONCEPT_OBSERVATION",
            "pair_sha256":str(r["pair_sha256"]),
            "payload":r["payload"],
            "authority_gain":"NONE",
            "causal_theorem_authority":"NONE",
        }
        if stored_pair is None or str(stored_pair.get("sha256",""))!=str(r.get("pair_evidence_sha256","")) or stored_pair.get("payload")!=expected_record:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_ACTION_CONCEPT_PAIR_EVIDENCE_REQUIRED"}

    concept_ids={(r["payload"]["concept_set_id"],r["payload"]["concept_evidence_id"],r["payload"]["concept_evidence_sha256"]) for r in rows}
    if len(concept_ids)!=1:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"ONE_EXACT_OWNED_CONCEPT_SET_REQUIRED"}
    concept_set_id,concept_evidence_id,concept_evidence_sha256=next(iter(concept_ids))
    stored=ms.evidence.get(str(concept_evidence_id))
    if stored is None or str(stored.get("sha256",""))!=str(concept_evidence_sha256) or stored.get("payload",{}).get("concept_set_id")!=concept_set_id:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_CONCEPT_SET_EVIDENCE_REQUIRED"}

    def relation_map(part):
        out={}; snapshots={}; structural={}; tokens={}
        for r in part:
            p=r["payload"]; rid=str(p["relation_id"]); dig=str(p["concept_content_digest_sha256"])
            out.setdefault(rid,set()).add(dig)
            snapshots.setdefault(rid,set()).add(str(p["relation_snapshot_sha256"]))
            structural[rid]=(str(p["relation_capability_id"]),str(p["relation_start_state_id"]),str(p["relation_next_state_id"]),round(float(p["relation_value_effect"]),6))
            tokens.setdefault(rid,set()).add(str(p["surface_token"]))
        if len(out)!=2:
            return None,"EXACTLY_TWO_EMPIRICAL_ACTION_RELATIONS_REQUIRED",None,None,None
        if any(len(v)!=1 for v in out.values()):
            return None,"ACTION_RELATION_TO_CONCEPT_NOT_FUNCTIONAL",None,None,None
        if any(len(v)!=1 for v in snapshots.values()):
            return None,"ACTION_RELATION_SNAPSHOT_NOT_STABLE",None,None,None
        concept_to_rel={}
        for rid,digs in out.items(): concept_to_rel.setdefault(next(iter(digs)),set()).add(rid)
        if len(concept_to_rel)!=2 or any(len(v)!=1 for v in concept_to_rel.values()):
            return None,"CONCEPT_TO_ACTION_RELATION_NOT_DISCRIMINATIVE",None,None,None
        return {rid:next(iter(v)) for rid,v in out.items()},None,{rid:next(iter(v)) for rid,v in snapshots.items()},structural,tokens

    tm,err,ts,structural,tokens=relation_map(train_pairs)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"TRAIN_"+err}
    hm,err,hs,hstruct,htokens=relation_map(holdout_pairs)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_"+err}
    if tm!=hm or structural!=hstruct:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_ACTION_CONCEPT_COUPLING_DISAGREES"}
    if ts!=hs:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_RELATION_SNAPSHOT_DISAGREES"}

    couplings=[]
    for rid in sorted(tm):
        relation,status=_current_relation(ms,rid)
        if relation is None:return status
        if _sha(relation)!=ts[rid]:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_RELATION_SNAPSHOT_DISAGREES_WITH_ACQUISITION","relation_id":rid}
        cap,start,nxt,effect=structural[rid]
        couplings.append({
            "relation_id":rid,
            "relation_snapshot_sha256":ts[rid],
            "capability_id":cap,
            "start_state_id":start,
            "next_state_id":nxt,
            "value_effect":effect,
            "concept_content_digest_sha256":tm[rid],
            "observed_surface_tokens":sorted(tokens[rid]|htokens.get(rid,set())),
        })
    durable={
        "kind":"OWNED_VEYA_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET",
        "coupling_set_id":"VEYA-P04-COUPLING-"+_sha({"couplings":couplings,"concept_set_id":concept_set_id})[:24],
        "concept_set_id":concept_set_id,
        "concept_evidence_id":concept_evidence_id,
        "concept_evidence_sha256":concept_evidence_sha256,
        "couplings":couplings,
        "training_pair_sha256":[r["pair_sha256"] for r in train_pairs],
        "training_pair_evidence_ids":[r["pair_evidence_id"] for r in train_pairs],
        "holdout_pair_sha256":[r["pair_sha256"] for r in holdout_pairs],
        "holdout_pair_evidence_ids":[r["pair_evidence_id"] for r in holdout_pairs],
        "acquisition_basis":"CURRENT_QUALIFIED_ACTION_OUTCOME_RELATIONS_PLUS_LANGUAGE_INDEXED_GROUNDED_CONCEPT_OBSERVATIONS",
        "causal_theorem_authority":"NONE",
        "general_causal_learner_authority":"NONE",
        "execution_authority":"NONE",
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
        "authority_gain":"NONE",
    }
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,durable,EpistemicStatus.PRESSURE_SUPPORTED,source="VEYA-P04-GROUNDED-LANGUAGE-CAUSAL-COMPOSITION")
        evidence_sha=ref.sha256
    else:
        if existing.get("negative") or existing.get("payload")!=durable:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTION_CONCEPT_COUPLING_EVIDENCE_ID_COLLISION"}
        evidence_sha=str(existing.get("sha256",""))
    stored_c=ms.evidence.get(evidence_id)
    if stored_c is None or stored_c.get("sha256")!=evidence_sha or stored_c.get("payload")!=durable:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_ACTION_CONCEPT_COUPLING_NOT_READABLE_EXACT"}
    return {
        **NONE,
        "status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY",
        "coupling_set_id":durable["coupling_set_id"],
        "coupling_evidence_id":evidence_id,
        "coupling_evidence_sha256":evidence_sha,
        "concept_set_id":concept_set_id,
        "concept_evidence_id":concept_evidence_id,
        "concept_evidence_sha256":concept_evidence_sha256,
        "couplings":couplings,
        "acquisition_basis":durable["acquisition_basis"],
    }


def compose_current_action_relation_with_language_concept(ms,coupling_set:dict[str,Any],*,relation_id:str,surface_token:str)->dict[str,Any]:
    """Compose one CURRENT empirical action relation with one owned language-indexed concept."""
    if coupling_set.get("status")!="OWNED_GROUNDED_LANGUAGE_MEDIATED_ACTION_CONCEPT_COUPLING_SET_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_ACTION_CONCEPT_COUPLING_SET_REQUIRED"}
    stored=ms.evidence.get(str(coupling_set.get("coupling_evidence_id","")))
    if stored is None or stored.get("sha256")!=coupling_set.get("coupling_evidence_sha256") or stored.get("payload",{}).get("coupling_set_id")!=coupling_set.get("coupling_set_id"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_ACTION_CONCEPT_COUPLING_EVIDENCE_REQUIRED"}
    relation,status=_current_relation(ms,str(relation_id))
    if relation is None:return status
    matches=[c for c in stored["payload"]["couplings"] if c["relation_id"]==str(relation_id)]
    if len(matches)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"ACTION_RELATION_NOT_IN_OWNED_COUPLING_SET"}
    coupling=matches[0]
    if _sha(relation)!=coupling["relation_snapshot_sha256"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_RELATION_SNAPSHOT_DISAGREES_WITH_COUPLING"}
    concept_shell={
        "status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY",
        "concept_set_id":stored["payload"]["concept_set_id"],
        "concept_evidence_id":stored["payload"]["concept_evidence_id"],
        "concept_evidence_sha256":stored["payload"]["concept_evidence_sha256"],
    }
    concept=resolve_owned_concept(ms,concept_shell,str(surface_token))
    if concept.get("status")!="OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY":return {**NONE,**concept,"status":"DEFER_UNKNOWN"}
    if concept["concept_content_digest_sha256"]!=coupling["concept_content_digest_sha256"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"LANGUAGE_INDEXED_CONCEPT_DISAGREES_WITH_EMPIRICAL_ACTION_COUPLING","relation_id":str(relation_id),"requested_concept_digest":concept["concept_content_digest_sha256"],"expected_concept_digest":coupling["concept_content_digest_sha256"]}
    return {
        **NONE,
        "status":"CURRENT_OWNED_GROUNDED_LANGUAGE_MEDIATED_CAUSAL_COMPOSITION_RESEARCH_ONLY",
        "coupling_set_id":coupling_set["coupling_set_id"],
        "relation_id":str(relation_id),
        "relation_capability_id":coupling["capability_id"],
        "relation_next_state_id":coupling["next_state_id"],
        "relation_value_effect":coupling["value_effect"],
        "surface_token":str(surface_token),
        "concept_content_digest_sha256":concept["concept_content_digest_sha256"],
        "grounded_concept_content":dict(concept["grounded_concept_content"]),
        "composition_basis":"CURRENT_EMPIRICAL_ACTION_OUTCOME_RELATION_PLUS_OWNED_LANGUAGE_INDEXED_GROUNDED_CONCEPT",
        "prediction_scope":"BOUNDED_EMPIRICAL_ACTION_TO_CONCEPT_COUPLING_ONLY",
    }


def inspect_owned_action_concept_couplings_without_language(ms,coupling_set:dict[str,Any])->dict[str,Any]:
    stored=ms.evidence.get(str(coupling_set.get("coupling_evidence_id","")))
    if stored is None or stored.get("sha256")!=coupling_set.get("coupling_evidence_sha256"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_ACTION_CONCEPT_COUPLING_EVIDENCE_REQUIRED"}
    return {
        **NONE,
        "status":"OWNED_ACTION_CONCEPT_COUPLING_CONTENT_AVAILABLE_WITHOUT_LANGUAGE_INDEX",
        "couplings":[{k:c[k] for k in ("relation_id","capability_id","start_state_id","next_state_id","value_effect","concept_content_digest_sha256")} for c in stored["payload"]["couplings"]],
        "lexical_retrieval_available":False,
    }


def attempt_text_only_causal_composition(text:str)->dict[str,Any]:
    return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_EMPIRICAL_RELATION_AND_OWNED_GROUNDED_CONCEPT_REQUIRED","surface_text":str(text)}
