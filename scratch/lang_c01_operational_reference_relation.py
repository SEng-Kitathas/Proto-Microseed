from __future__ import annotations
import json,tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scratch.ms2046_grounded_operational_token_referent_binding_quarry import (_build,_history,derive_binding_candidate,binding_status)

AUTHORITY_NONE={"semantic_reference_authority":"NONE","truth_authority":"NONE","execution_authority":"NONE",
                "numerical_identity_authority":"NONE","semantic_identity_authority":"NONE"}

def admit_operational_reference_relation(ms,candidate:dict[str,object])->dict[str,object]:
    current=binding_status(ms,candidate)
    if current.get("status")!="CURRENT_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE":
        return {**AUTHORITY_NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_GROUNDED_BINDING_CANDIDATE_REQUIRED"}
    b=candidate["binding"]
    relation={"token_capability_id":b["signal_capability_id"],"token_capability_epoch":b["signal_capability_epoch"],
              "token_capability_signature_sha256":b["signal_capability_signature_sha256"],
              "coordination_id":b["coordination_id"],"coordination_epoch":b["coordination_epoch"],
              "coordination_signature_sha256":b["coordination_signature_sha256"],
              "operational_referent_signature_sha256":b["operational_referent_signature_sha256"],
              "binding_id":candidate["binding_id"],"source_episode_sha256":candidate["source_episode_sha256"]}
    return {**AUTHORITY_NONE,"status":"CURRENT_OPERATIONAL_REFERENCE_RELATION_RESEARCH_ONLY",
            "reason":"OPERATOR_ADMITTED_REFERENCE_RESEARCH_PLUS_CURRENT_EXACT_GROUNDED_BINDING",
            "relation":relation,"reference_layer":"B1_OPERATIONAL_REFERENCE","authority_gain":"NONE"}

def resolve_current_operational_referent(ms,relation:dict[str,object],token_capability_id:str)->dict[str,object]:
    if relation.get("status")!="CURRENT_OPERATIONAL_REFERENCE_RELATION_RESEARCH_ONLY":
        return {**AUTHORITY_NONE,"status":"DEFER_UNKNOWN","reason":"CURRENT_OPERATIONAL_REFERENCE_RELATION_REQUIRED"}
    r=relation["relation"]
    if token_capability_id!=r["token_capability_id"]:
        return {**AUTHORITY_NONE,"status":"DEFER_UNKNOWN","reason":"EXACT_TOKEN_BINDING_REQUIRED"}
    sid=str(r["token_capability_id"]); cid=str(r["coordination_id"])
    if (not ms.capabilities.is_current(sid) or ms.capabilities.epochs[sid]!=r["token_capability_epoch"] or
        ms.capabilities.contracts[sid].computed_signature_sha256()!=r["token_capability_signature_sha256"]):
        return {**AUTHORITY_NONE,"status":"DEFER_UNKNOWN","reason":"TOKEN_BINDING_NOT_CURRENT"}
    if (not ms.coordinations.is_current(cid,r["coordination_epoch"]) or
        ms.coordinations.contracts[cid].computed_signature_sha256()!=r["coordination_signature_sha256"]):
        return {**AUTHORITY_NONE,"status":"DEFER_UNKNOWN","reason":"COORDINATION_BINDING_NOT_CURRENT"}
    return {**AUTHORITY_NONE,"status":"OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY",
            "operational_referent_signature_sha256":r["operational_referent_signature_sha256"],
            "reference_layer":"B1_OPERATIONAL_REFERENCE","authority_gain":"NONE"}

def run_campaign()->dict[str,object]:
    with tempfile.TemporaryDirectory(prefix='lang-c01-') as td:
        ms,world=_build(Path(td))
        try:
            train,hold=_history(ms,world); cand=derive_binding_candidate(ms,train,hold)
            rel=admit_operational_reference_relation(ms,cand)
            assert rel["status"]=="CURRENT_OPERATIONAL_REFERENCE_RELATION_RESEARCH_ONLY",rel
            pos=resolve_current_operational_referent(ms,rel,"SIG-X")
            assert pos["status"]=="OPERATIONAL_REFERENT_RESOLVED_RESEARCH_ONLY",pos
            wrong=resolve_current_operational_referent(ms,rel,"hello"); assert wrong["status"]=="DEFER_UNKNOWN"
            ms.invalidate_capability("SIG-X",reason="LANG_C01_SIGNAL_DRIFT")
            stale=resolve_current_operational_referent(ms,rel,"SIG-X"); assert stale["status"]=="DEFER_UNKNOWN"
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    with tempfile.TemporaryDirectory(prefix='lang-c01-reversal-') as td:
        ms,world=_build(Path(td))
        try:
            train,hold=_history(ms,world,train_mode="P",hold_mode="Q")
            cand2=derive_binding_candidate(ms,train,hold)
            reversed_rel=admit_operational_reference_relation(ms,cand2)
            assert reversed_rel["status"]=="DEFER_UNKNOWN"
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    with tempfile.TemporaryDirectory(prefix='lang-c01-readable-') as td:
        ms,world=_build(Path(td))
        try:
            readable=derive_binding_candidate(ms,(),(),signal_id="hello")
            readable_rel=admit_operational_reference_relation(ms,readable)
            assert readable_rel["status"]=="DEFER_UNKNOWN"
        finally:
            ms.biography.close(); ms.evidence.conn.close(); ms.store.conn.close()
    assert pos["semantic_reference_authority"]==pos["truth_authority"]==pos["execution_authority"]=="NONE"
    return {"status":"PASS","positive":pos,"wrong_token":wrong,"stale":stale,
            "convention_reversal":reversed_rel,"readable_ungrounded":readable_rel,
            "earned":"CURRENT_EXACT_GROUNDED_BINDING_CAN_SUPPORT_A_BRANCH_OWNED_B1_OPERATIONAL_REFERENCE_RELATION_WITHOUT_SEMANTIC_REFERENCE_AUTHORITY",
            "next":"PRESS_B1_RELATION_PERSISTENCE_RESTART_AND_MULTIPLE_TOKENS_BEFORE_B2_COMPOSITION"}

if __name__=='__main__': print(json.dumps(run_campaign(),indent=2,sort_keys=True))
