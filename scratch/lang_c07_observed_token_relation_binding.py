from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from microseed import EpistemicStatus
from scratch.lang_c02_multi_token_restart_revalidation import build_two_relations
from scratch.lang_c06_grounded_directional_relation import (
    NONE, external_direction_episode, derive_directional_relation_candidate,
    revalidate_directional_relation,
)


def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def observe_opaque_relation_token(ms, token:str, index:int)->dict[str,object]:
    """Write an external observation as content-bound evidence, then read the token back from Microseed-owned evidence."""
    evidence_id=f"E-C07-TOKEN-{index}"
    supplied={"kind":"OPAQUE_EXTERNAL_TOKEN_OBSERVATION","capture_id":f"C07-TOKEN-{index}",
        "opaque_token":str(token),"event_lineage":f"C07-EVENT-{index}","observation_authority":"OBSERVATION_ONLY"}
    ref=ms.append_evidence(evidence_id,supplied,EpistemicStatus.PRESSURE_SUPPORTED,source="EXTERNAL-WORLD")
    stored=ms.evidence.get(evidence_id)
    if stored is None or stored.get("sha256")!=ref.sha256:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONTENT_BOUND_TOKEN_EVIDENCE_NOT_READABLE"}
    payload=stored.get("payload",{})
    if payload.get("kind")!="OPAQUE_EXTERNAL_TOKEN_OBSERVATION" or payload.get("observation_authority")!="OBSERVATION_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"OBSERVATION_ONLY_TOKEN_EVIDENCE_REQUIRED"}
    return {**NONE,"status":"OPAQUE_TOKEN_OBSERVED_RESEARCH_ONLY","evidence_id":evidence_id,
        "evidence_sha256":ref.sha256,"payload":payload,"token_observation_sha256":_sha(payload)}

def paired_relation_token_episode(ms,world,layout:str,index:int,mode:str,token:str)->dict[str,object]:
    rel=external_direction_episode(ms,world,layout,index,mode)
    tok=observe_opaque_relation_token(ms,token,index)
    if rel.get("status")!="CURRENT_GROUNDED_EXTERNAL_DIRECTIONAL_EVENT_EPISODE" or tok.get("status")!="OPAQUE_TOKEN_OBSERVED_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_RELATION_EVENT_AND_OBSERVED_TOKEN_REQUIRED"}
    stored=ms.evidence.get(tok["evidence_id"])
    if stored is None or stored.get("sha256")!=tok["evidence_sha256"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TOKEN_EVIDENCE_NOT_CURRENTLY_READABLE"}
    payload={
        "event_lineage":f"C07-EVENT-{index}",
        "opaque_token":stored["payload"]["opaque_token"],
        "relation_order":list(rel["payload"]["ordered_operational_referent_signatures"]),
        "relation_episode_sha256":rel["episode_sha256"],
        "token_observation_sha256":tok["token_observation_sha256"],
    }
    return {**NONE,"status":"CURRENT_PAIRED_TOKEN_RELATION_EPISODE_RESEARCH_ONLY","payload":payload,"pair_sha256":_sha(payload)}


def derive_observed_token_relation_bindings(ms,train,holdouts,evidence_id:str="E-C07-BINDING-SET")->dict[str,object]:
    """Derive a bijection only from paired lived evidence; token spelling has no supplied role."""
    if len(train)<16:return {**NONE,"status":"DEFER_UNKNOWN","reason":"SUFFICIENT_PAIRED_HISTORY_REQUIRED"}
    if len(holdouts)<8:return {**NONE,"status":"DEFER_UNKNOWN","reason":"INDEPENDENT_PAIRED_HOLDOUT_REQUIRED"}
    rows=tuple(train)+tuple(holdouts)
    if any(r.get("status")!="CURRENT_PAIRED_TOKEN_RELATION_EPISODE_RESEARCH_ONLY" for r in rows):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"EVERY_TOKEN_RELATION_PAIR_MUST_BE_CURRENT"}

    def mapping(part):
        token_to_orders={}; order_to_tokens={}
        for r in part:
            token=r["payload"]["opaque_token"]; order=tuple(r["payload"]["relation_order"])
            token_to_orders.setdefault(token,set()).add(order); order_to_tokens.setdefault(order,set()).add(token)
        if len(token_to_orders)!=2 or len(order_to_tokens)!=2:
            return None,"EXACTLY_TWO_OBSERVED_TOKENS_AND_TWO_RELATION_ORDERS_REQUIRED"
        if any(len(v)!=1 for v in token_to_orders.values()) or any(len(v)!=1 for v in order_to_tokens.values()):
            return None,"TOKEN_RELATION_ASSOCIATION_NOT_BIJECTIVE"
        return {t:next(iter(v)) for t,v in token_to_orders.items()},None

    tm,err=mapping(train)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"TRAIN_"+err}
    hm,err=mapping(holdouts)
    if err:return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_"+err}
    if tm!=hm:return {**NONE,"status":"DEFER_UNKNOWN","reason":"HOLDOUT_TOKEN_RELATION_ASSOCIATION_DISAGREES"}
    evidence={
        "bindings":[{"opaque_token":t,"relation_order":list(tm[t])} for t in sorted(tm)],
        "training_pair_sha256":[r["pair_sha256"] for r in train],
        "holdout_pair_sha256":[r["pair_sha256"] for r in holdouts],
    }
    binding_set_id="OP-TOK-REL-"+_sha(evidence)[:24]
    durable={"kind":"DERIVED_OPAQUE_TOKEN_RELATION_BINDING_EVIDENCE","binding_set_id":binding_set_id,
        "bindings":evidence["bindings"],"source_pair_sha256":evidence["training_pair_sha256"]+evidence["holdout_pair_sha256"],
        "authority_gain":"NONE"}
    ref=ms.append_evidence(evidence_id,durable,EpistemicStatus.PRESSURE_SUPPORTED,source="DERIVED-PAIRED-EXPERIENCE")
    stored=ms.evidence.get(evidence_id)
    if stored is None or stored.get("sha256")!=ref.sha256:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"DERIVED_BINDING_EVIDENCE_NOT_READABLE"}
    return {**NONE,"status":"OBSERVED_OPAQUE_TOKEN_RELATION_BINDINGS_RESEARCH_ONLY",
        "binding_set_id":binding_set_id,"binding_evidence_id":evidence_id,"binding_evidence_sha256":ref.sha256,
        "bindings":stored["payload"]["bindings"],"source_pair_sha256":stored["payload"]["source_pair_sha256"],"authority_gain":"NONE"}


def resolve_observed_token_relation(ms,binding_set,token:str,current_relation_candidate)->dict[str,object]:
    if binding_set.get("status")!="OBSERVED_OPAQUE_TOKEN_RELATION_BINDINGS_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_OBSERVED_TOKEN_BINDING_SET_REQUIRED"}
    stored=ms.evidence.get(str(binding_set.get("binding_evidence_id","")))
    if stored is None or stored.get("sha256")!=binding_set.get("binding_evidence_sha256"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CONTENT_BOUND_BINDING_EVIDENCE_REQUIRED"}
    if stored.get("payload",{}).get("binding_set_id")!=binding_set.get("binding_set_id"):
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"BINDING_EVIDENCE_IDENTITY_MISMATCH"}
    if current_relation_candidate.get("status")!="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY":
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_GROUNDED_DIRECTIONAL_RELATION_REQUIRED"}
    matches=[b for b in stored["payload"]["bindings"] if b["opaque_token"]==str(token)]
    if len(matches)!=1:return {**NONE,"status":"DEFER_UNKNOWN","reason":"OPAQUE_TOKEN_NOT_GROUNDED_BY_PAIRED_EVIDENCE"}
    observed=matches[0]["relation_order"]
    if observed!=current_relation_candidate["ordered_operational_referent_signatures"]:
        return {**NONE,"status":"DEFER_UNKNOWN","reason":"TOKEN_BINDING_DOES_NOT_MATCH_CURRENT_RELATION"}
    return {**NONE,"status":"OPAQUE_OBSERVED_TOKEN_RESOLVES_CURRENT_RELATION_RESEARCH_ONLY",
        "opaque_token":str(token),"derived_relation_id":current_relation_candidate["derived_relation_id"],
        "ordered_operational_referent_signatures":list(observed),"binding_set_id":binding_set["binding_set_id"],"authority_gain":"NONE"}


def _relation_candidate_for_mode(ms,world,rx,ry,mode:str,start:int):
    train=tuple(external_direction_episode(ms,world,"A" if i%2==0 else "B",start+i,mode) for i in range(10))
    hold=tuple(external_direction_episode(ms,world,"B" if i%2==0 else "A",start+100+i,mode) for i in range(6))
    return derive_directional_relation_candidate(ms,train,hold,rx,ry)


def run_campaign(token_a="K7",token_b="M2"):
    with tempfile.TemporaryDirectory(prefix="lang-c07-") as td:
        ms,world,rx,ry=build_two_relations(Path(td))
        try:
            action_ids_before=set(ms.capabilities.contracts)
            # Two opposing world relations prevent single-token co-occurrence from passing as grounding.
            train=[]; hold=[]
            for i in range(20):
                mode="PQ" if i%2==0 else "QP"; token=token_a if mode=="PQ" else token_b
                train.append(paired_relation_token_episode(ms,world,"A" if i%3 else "B",i,mode,token))
            for i in range(10):
                mode="QP" if i%2==0 else "PQ"; token=token_b if mode=="QP" else token_a
                hold.append(paired_relation_token_episode(ms,world,"B" if i%3 else "A",100+i,mode,token))
            bindings=derive_observed_token_relation_bindings(ms,tuple(train),tuple(hold))
            assert bindings["status"]=="OBSERVED_OPAQUE_TOKEN_RELATION_BINDINGS_RESEARCH_ONLY",bindings
            pq=_relation_candidate_for_mode(ms,world,rx,ry,"PQ",300)
            qp=_relation_candidate_for_mode(ms,world,rx,ry,"QP",500)
            assert pq["status"]==qp["status"]=="GROUNDED_OPERATIONAL_DIRECTIONAL_RELATION_CANDIDATE_RESEARCH_ONLY"
            ra=resolve_observed_token_relation(ms,bindings,token_a,pq); rb=resolve_observed_token_relation(ms,bindings,token_b,qp)
            assert ra["status"]==rb["status"]=="OPAQUE_OBSERVED_TOKEN_RESOLVES_CURRENT_RELATION_RESEARCH_ONLY"
            assert resolve_observed_token_relation(ms,bindings,"UNSEEN",pq)["status"]=="DEFER_UNKNOWN"
            assert resolve_observed_token_relation(ms,bindings,token_a,qp)["status"]=="DEFER_UNKNOWN"

            # Convention reversal in independent holdout must fail closed rather than remap the tokens.
            reversed_hold=[]
            for i in range(10):
                mode="PQ" if i%2==0 else "QP"; token=token_b if mode=="PQ" else token_a
                reversed_hold.append(paired_relation_token_episode(ms,world,"A" if i%2 else "B",700+i,mode,token))
            reversal=derive_observed_token_relation_bindings(ms,tuple(train),tuple(reversed_hold),"E-C07-REVERSAL")
            assert reversal["status"]=="DEFER_UNKNOWN" and reversal["reason"]=="HOLDOUT_TOKEN_RELATION_ASSOCIATION_DISAGREES"

            # Ambiguous evidence must fail closed.
            ambiguous=list(hold)
            ambiguous[0]=paired_relation_token_episode(ms,world,"A",900,"PQ",token_b)
            ambiguity=derive_observed_token_relation_bindings(ms,tuple(train),tuple(ambiguous),"E-C07-AMBIGUITY")
            assert ambiguity["status"]=="DEFER_UNKNOWN"

            # Currentness is owned by fresh C06 reality, not the token memory.
            fresh_pq=revalidate_directional_relation(ms,world,pq,rx,ry,"PQ",1000)
            drift_pq=revalidate_directional_relation(ms,world,pq,rx,ry,"QP",1100)
            assert fresh_pq["status"]=="CURRENT_DIRECTIONAL_RELATION_REVALIDATED_RESEARCH_ONLY"
            assert drift_pq["status"]=="DEFER_UNKNOWN"

            action_ids_after=set(ms.capabilities.contracts)
            new_actions=sorted(action_ids_after-action_ids_before)
            assert new_actions==[],new_actions
            assert ms.status()["language"]=="DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
            # Anti-smuggling: no output schema grants or names capability/faculty/predicate roles.
            for obj in (bindings,ra,rb):
                keys={str(k).lower() for k in obj}
                assert not any("capability" in k or "faculty" in k for k in keys),keys
                assert not any(k in keys for k in {"predicate","subject","object","agent","patient"}),keys
            return {
                "status":"PASS_BOUNDED_RESEARCH_ONLY",
                "technical_name":"Paired-experience grounding of opaque observed tokens to current affordance-relative relations",
                "bindings":bindings,"token_a_resolution":ra,"token_b_resolution":rb,
                "unseen_token":"DEFER_UNKNOWN","wrong_relation":"DEFER_UNKNOWN",
                "convention_reversal":reversal,"ambiguous_holdout":ambiguity,
                "fresh_relation":fresh_pq,"relation_drift":drift_pq,
                "new_microseed_action_contracts_registered":new_actions,
                "language_status":ms.status()["language"],
                "nonclaim":["NO_SEMANTIC_PREDICATE","NO_PROPOSITION","NO_TRUTH_BEARER","NO_LANGUAGE_FACULTY","NO_GENERIC_CAPABILITY","NO_EXECUTABLE_RELATION_ACTION","NO_TOKEN_MEANING_REGISTRY","NO_CANON_PROMOTION"],
            }
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()

if __name__=="__main__":
    print(json.dumps(run_campaign(),indent=2,sort_keys=True))
