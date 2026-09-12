from __future__ import annotations

import hashlib
import json
from typing import Any

from microseed import EpistemicStatus
from scratch.lang_c06_grounded_directional_relation import external_direction_episode

NONE={
    "language_authority":"NONE",
    "semantic_reference_authority":"NONE",
    "predicate_authority":"NONE",
    "truth_authority":"NONE",
    "execution_authority":"NONE",
    "planner_authority":"NONE",
    "value_priority_authority":"NONE",
    "authority_gain":"NONE",
}


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def _grounding_dependency_fingerprint(ms)->list[dict[str,object]]:
    out=[]
    for cid in ("SIG-X","SIG-Y","FX-P","FX-Q"):
        if cid not in ms.capabilities.contracts:
            continue
        c=ms.capabilities.contracts[cid]
        out.append({
            "capability_id":cid,
            "epoch":int(ms.capabilities.epochs.get(cid,-1)),
            "signature_sha256":str(c.computed_signature_sha256()),
            "current":bool(ms.capabilities.is_current(cid)),
        })
    return out


def grounded_relation_sequence_episode(ms,world,*,surface_token:str,first_mode:str,second_mode:str,index:int)->dict[str,Any]:
    """Pair two CURRENT grounded directional events with an observed language surface.

    The structural pattern is derived from the grounded relation orders; the token spelling has no role.
    """
    first=external_direction_episode(ms,world,"A" if index%2==0 else "B",index*2,first_mode)
    second=external_direction_episode(ms,world,"B" if index%2==0 else "A",index*2+1,second_mode)
    if first.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE" or second.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TWO_CURRENT_GROUNDED_DIRECTIONAL_EVENTS_REQUIRED"}
    a=tuple(first["payload"]["ordered_operational_referent_signatures"])
    b=tuple(second["payload"]["ordered_operational_referent_signatures"])
    if len(a)!=2 or len(b)!=2 or set(a)!=set(b):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"COMMON_TWO_REFERENT_RELATION_DOMAIN_REQUIRED"}
    if b==a:
        transform=(0,1)
    elif b==(a[1],a[0]):
        transform=(1,0)
    else:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"RELATION_SEQUENCE_TRANSFORM_NOT_BOUNDED_BINARY_PERMUTATION"}
    payload={
        "surface_token":str(surface_token),
        "first_relation_order":list(a),
        "second_relation_order":list(b),
        "relation_transform_permutation":list(transform),
        "source_direction_episode_sha256":[first["episode_sha256"],second["episode_sha256"]],
    }
    return {
        **NONE,
        "status":"CURRENT_GROUNDED_LANGUAGE_RELATION_SEQUENCE_EPISODE",
        "payload":payload,
        "sequence_sha256":_sha(payload),
        "first_episode":first,
        "second_episode":second,
    }


def derive_owned_language_mediated_concepts(ms,train:list[dict[str,Any]],holdouts:list[dict[str,Any]],*,evidence_id:str="E-VEYA-P03-CONCEPT-SET")->dict[str,Any]:
    """Derive second-order relation concepts from language-grouped grounded sequence episodes.

    Language participates in acquisition by grouping examples. Concept *content* is the grounded
    transform invariant, not token spelling. The durable evidence makes the learned state owned/inspectable.
    """
    if len(train)<12:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_LANGUAGE_GROUPED_TRAINING_HISTORY_REQUIRED"}
    if len(holdouts)<6:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"INDEPENDENT_LANGUAGE_GROUPED_HOLDOUT_REQUIRED"}
    rows=tuple(train)+tuple(holdouts)
    if any(r.get("status")!="CURRENT_GROUNDED_LANGUAGE_RELATION_SEQUENCE_EPISODE" for r in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_CONCEPT_EXEMPLAR_MUST_BE_CURRENT_AND_GROUNDED"}
    if any(str(r.get("sequence_sha256",""))!=_sha(r.get("payload",{})) for r in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONCEPT_EXEMPLAR_CONTENT_HASH_MISMATCH"}

    def mapping(part):
        token_to_patterns={}; pattern_to_tokens={}
        for r in part:
            token=str(r["payload"]["surface_token"])
            pattern=tuple(int(x) for x in r["payload"]["relation_transform_permutation"])
            token_to_patterns.setdefault(token,set()).add(pattern)
            pattern_to_tokens.setdefault(pattern,set()).add(token)
        if len(token_to_patterns)!=2 or len(pattern_to_tokens)!=2:
            return None,"EXACTLY_TWO_LANGUAGE_GROUPS_AND_TWO_GROUNDED_PATTERNS_REQUIRED"
        if any(len(v)!=1 for v in token_to_patterns.values()):
            return None,"TOKEN_CONCEPT_ASSOCIATION_NOT_FUNCTIONAL"
        if any(len(v)!=1 for v in pattern_to_tokens.values()):
            return None,"GROUNDED_PATTERN_NOT_LEXICALLY_DISTINCT"
        return {t:next(iter(v)) for t,v in token_to_patterns.items()},None

    tm,err=mapping(train)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"TRAIN_"+err}
    hm,err=mapping(holdouts)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_"+err}
    if tm!=hm:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_LANGUAGE_CONCEPT_ASSOCIATION_DISAGREES"}

    concepts=[]
    for token in sorted(tm):
        pattern=tm[token]
        content={
            "concept_basis":"GROUNDED_SECOND_ORDER_RELATION_SEQUENCE_TRANSFORM",
            "relation_transform_permutation":list(pattern),
            "arity":2,
        }
        concepts.append({
            "surface_token":token,
            "concept_content_digest_sha256":_sha(content),
            "grounded_concept_content":content,
        })
    source_hashes=[r["sequence_sha256"] for r in rows]
    durable={
        "kind":"OWNED_VEYA_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET",
        "concept_set_id":"VEYA-CONCEPT-"+_sha({"concepts":concepts})[:24],
        "concepts":concepts,
        "training_sequence_sha256":[r["sequence_sha256"] for r in train],
        "holdout_sequence_sha256":[r["sequence_sha256"] for r in holdouts],
        "source_sequence_sha256":source_hashes,
        "grounding_dependency_fingerprint":_grounding_dependency_fingerprint(ms),
        "acquisition_basis":"LANGUAGE_GROUPED_CURRENT_GROUNDED_RELATION_SEQUENCE_EXPERIENCE",
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
        "authority_gain":"NONE",
    }
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,durable,EpistemicStatus.PRESSURE_SUPPORTED,source="VEYA-P03-GROUNDED-LANGUAGE-CONCEPT-ACQUISITION")
        evidence_sha=ref.sha256
    else:
        if existing.get("negative") or existing.get("payload")!=durable:
            return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONCEPT_EVIDENCE_ID_COLLISION"}
        evidence_sha=str(existing.get("sha256",""))
    stored=ms.evidence.get(evidence_id)
    if stored is None or stored.get("sha256")!=evidence_sha or stored.get("payload")!=durable:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_CONCEPT_EVIDENCE_NOT_READABLE_EXACT"}
    return {
        **NONE,
        "status":"OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY",
        "concept_set_id":durable["concept_set_id"],
        "concept_evidence_id":evidence_id,
        "concept_evidence_sha256":evidence_sha,
        "concepts":concepts,
        "source_sequence_sha256":source_hashes,
        "grounding_dependency_fingerprint":durable["grounding_dependency_fingerprint"],
        "acquisition_basis":durable["acquisition_basis"],
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
    }


def resolve_owned_concept(ms,concept_set:dict[str,Any],surface_token:str)->dict[str,Any]:
    if concept_set.get("status")!="OWNED_GROUNDED_LANGUAGE_MEDIATED_CONCEPT_SET_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"OWNED_GROUNDED_CONCEPT_SET_REQUIRED"}
    stored=ms.evidence.get(str(concept_set.get("concept_evidence_id","")))
    if stored is None or stored.get("sha256")!=concept_set.get("concept_evidence_sha256"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_CONCEPT_EVIDENCE_REQUIRED"}
    if stored.get("payload",{}).get("concept_set_id")!=concept_set.get("concept_set_id"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONCEPT_SET_IDENTITY_MISMATCH"}
    if stored.get("payload",{}).get("grounding_dependency_fingerprint")!=_grounding_dependency_fingerprint(ms):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONCEPT_GROUNDING_DEPENDENCY_DRIFT_REVALIDATION_REQUIRED","concept_set_id":concept_set.get("concept_set_id")}
    matches=[c for c in stored["payload"]["concepts"] if c["surface_token"]==str(surface_token)]
    if len(matches)!=1:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"SURFACE_TOKEN_NOT_LEARNED_AS_OWNED_CONCEPT_INDEX"}
    c=matches[0]
    return {
        **NONE,
        "status":"OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY",
        "surface_token":str(surface_token),
        "concept_content_digest_sha256":c["concept_content_digest_sha256"],
        "grounded_concept_content":dict(c["grounded_concept_content"]),
        "concept_set_id":concept_set["concept_set_id"],
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
    }


def revalidate_owned_concept_after_grounding_drift(ms,concept_set:dict[str,Any],surface_token:str,fresh_sequence:dict[str,Any])->dict[str,Any]:
    """Revalidate learned concept content against fresh grounded evidence after dependency drift."""
    stored=ms.evidence.get(str(concept_set.get("concept_evidence_id","")))
    if stored is None or stored.get("sha256")!=concept_set.get("concept_evidence_sha256"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_CONCEPT_EVIDENCE_REQUIRED"}
    if fresh_sequence.get("status")!="CURRENT_GROUNDED_LANGUAGE_RELATION_SEQUENCE_EPISODE" or str(fresh_sequence.get("sequence_sha256",""))!=_sha(fresh_sequence.get("payload",{})):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"FRESH_CONTENT_BOUND_GROUNDED_SEQUENCE_REQUIRED"}
    matches=[c for c in stored["payload"]["concepts"] if c["surface_token"]==str(surface_token)]
    if len(matches)!=1:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"SURFACE_TOKEN_NOT_LEARNED_AS_OWNED_CONCEPT_INDEX"}
    c=matches[0]
    observed=tuple(int(x) for x in fresh_sequence["payload"]["relation_transform_permutation"])
    expected=tuple(int(x) for x in c["grounded_concept_content"]["relation_transform_permutation"])
    if observed!=expected:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"FRESH_GROUNDED_CONCEPT_PATTERN_DISAGREES","observed_pattern":list(observed),"expected_pattern":list(expected)}
    return {
        **NONE,
        "status":"CURRENT_OWNED_LANGUAGE_CONCEPT_REVALIDATED_RESEARCH_ONLY",
        "surface_token":str(surface_token),
        "concept_content_digest_sha256":c["concept_content_digest_sha256"],
        "grounded_concept_content":dict(c["grounded_concept_content"]),
        "concept_set_id":concept_set["concept_set_id"],
        "fresh_sequence_sha256":fresh_sequence["sequence_sha256"],
        "current_grounding_dependency_fingerprint":_grounding_dependency_fingerprint(ms),
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
    }


def inspect_owned_concept_contents_without_language(ms,concept_set:dict[str,Any])->dict[str,Any]:
    """Language-disabled inspection: lexical retrieval is gone, owned concept content remains."""
    stored=ms.evidence.get(str(concept_set.get("concept_evidence_id","")))
    if stored is None or stored.get("sha256")!=concept_set.get("concept_evidence_sha256"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_OWNED_CONCEPT_EVIDENCE_REQUIRED"}
    contents=[{
        "concept_content_digest_sha256":c["concept_content_digest_sha256"],
        "grounded_concept_content":dict(c["grounded_concept_content"]),
    } for c in stored["payload"]["concepts"]]
    return {**NONE,"status":"OWNED_CONCEPT_CONTENTS_AVAILABLE_WITHOUT_LANGUAGE_INDEX","concept_contents":contents,"lexical_retrieval_available":False}


def predict_second_relation_from_concept(concept:dict[str,Any],first_episode:dict[str,Any])->dict[str,Any]:
    if concept.get("status") not in {"OWNED_LANGUAGE_CONCEPT_RESOLVED_RESEARCH_ONLY","CURRENT_OWNED_LANGUAGE_CONCEPT_REVALIDATED_RESEARCH_ONLY"}:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"RESOLVED_OR_REVALIDATED_OWNED_CONCEPT_REQUIRED"}
    if first_episode.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_GROUNDED_FIRST_RELATION_REQUIRED"}
    order=tuple(first_episode["payload"]["ordered_operational_referent_signatures"])
    pattern=tuple(int(x) for x in concept["grounded_concept_content"]["relation_transform_permutation"])
    if len(order)!=2 or pattern not in {(0,1),(1,0)}:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"BOUNDED_BINARY_CONCEPT_APPLICATION_REQUIRED"}
    predicted=tuple(order[i] for i in pattern)
    return {
        **NONE,
        "status":"OWNED_LANGUAGE_CONCEPT_CAUSAL_PREDICTION_RESEARCH_ONLY",
        "concept_content_digest_sha256":concept["concept_content_digest_sha256"],
        "predicted_second_relation_order":list(predicted),
        "prediction_basis":"OWNED_GROUNDED_CONCEPT_CONTENT_PLUS_CURRENT_FIRST_RELATION",
        "surface_spelling_authority":"NONE",
        "external_oracle_authority":"NONE",
    }


def attempt_text_only_concept(surface_text:str)->dict[str,Any]:
    return {
        **NONE,
        "status":"DEFER_UNKNOWN",
        "reason":"GROUNDED_LANGUAGE_GROUPED_ACQUISITION_HISTORY_REQUIRED",
        "surface_text":str(surface_text),
        "external_oracle_authority":"NONE",
        "surface_spelling_authority":"NONE",
    }
