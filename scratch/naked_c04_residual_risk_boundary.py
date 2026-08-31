from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scratch.naked_c01_explicit_experimental_warrant_quarry import ActionDescriptor
from scratch.naked_c03_unique_eligible_subject import issue_from_unique

def bounded_exposure(action,warrant)->dict[str,object]:
    ok=(warrant is not None and warrant.capability_id==action.capability_id and warrant.capability_epoch==action.epoch and
        warrant.capability_signature==action.signature and warrant.scope_id==action.scope_id and warrant.max_invocations==1)
    return {"status":"BOUNDED_EXPERIMENTAL_EXPOSURE" if ok else "NOT_BOUNDED_EXPOSURE",
            "max_invocations":getattr(warrant,"max_invocations",None),"exact_scope":ok}

def bounded_downstream_risk(action,warrant,independent_current_safety_premise:dict[str,object]|None)->dict[str,object]:
    exposure=bounded_exposure(action,warrant)
    if exposure["status"]!="BOUNDED_EXPERIMENTAL_EXPOSURE": return {"status":"UNKNOWN_INCOMPLETE","reason":"BOUNDED_EXPOSURE_REQUIRED"}
    if action.consequence_modeled: return {"status":"NOT_FIRST_UNMODELED_ACTION","reason":"CONSEQUENCE_ALREADY_MODELED"}
    if not independent_current_safety_premise:
        return {"status":"UNKNOWN_INCOMPLETE","reason":"UNMODELED_DOWNSTREAM_CONSEQUENCE_HAS_NO_CURRENT_RISK_BOUND"}
    if independent_current_safety_premise.get("current") is not True or independent_current_safety_premise.get("scope_id")!=action.scope_id or independent_current_safety_premise.get("capability_id")!=action.capability_id:
        return {"status":"UNKNOWN_INCOMPLETE","reason":"EXACT_CURRENT_SAFETY_PREMISE_REQUIRED"}
    return {"status":"BOUNDED_DOWNSTREAM_RISK_BY_SEPARATE_PREMISE","authority_source":"INDEPENDENT_CURRENT_SAFETY_PREMISE"}

def run_campaign():
    a=ActionDescriptor("A",0,"sigA","S")
    issued=issue_from_unique([a],"s0"); w=issued["warrant"]; assert w
    exp=bounded_exposure(a,w); assert exp["status"]=="BOUNDED_EXPERIMENTAL_EXPOSURE"
    naked=bounded_downstream_risk(a,w,None); assert naked["status"]=="UNKNOWN_INCOMPLETE"
    wrong=bounded_downstream_risk(a,w,{"current":True,"scope_id":"T","capability_id":"A"}); assert wrong["status"]=="UNKNOWN_INCOMPLETE"
    equipped=bounded_downstream_risk(a,w,{"current":True,"scope_id":"S","capability_id":"A"}); assert equipped["status"]=="BOUNDED_DOWNSTREAM_RISK_BY_SEPARATE_PREMISE"
    return {"status":"PASS","exposure":exp,"naked_risk":naked,"wrong_safety":wrong,"equipped_risk":equipped,
      "earned":"A1_CAN_PROVE_BOUNDED_EXPERIMENTAL_EXPOSURE_BUT_CANNOT_PROVE_BOUNDED_DOWNSTREAM_RISK_FOR_A_TRULY_UNMODELED_ACTION_WITHOUT_A_SEPARATE_CURRENT_SAFETY_PREMISE",
      "constitutional_fork":{
        "NAKED_RESIDUAL_RISK_ACCEPTANCE":"constitution explicitly permits one exact bounded exposure despite unknown downstream risk",
        "SAFETY_PREMISE_REQUIRED":"first intervention remains blocked until separate current safety premise exists; this is equipped/federated unless safety can itself be earned NAKED"},
      "operator_authority_required":True}
if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
