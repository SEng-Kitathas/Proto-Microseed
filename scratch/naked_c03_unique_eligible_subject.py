from __future__ import annotations
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scratch.naked_c01_explicit_experimental_warrant_quarry import ActionDescriptor,derive_warrant,authorize


def eligible(a:ActionDescriptor)->bool:
    return a.current and a.qualified and a.represented and not a.consequence_modeled

def nominate_unique(actions:list[ActionDescriptor])->dict[str,object]:
    xs=[a for a in actions if eligible(a)]
    if len(xs)==0:return {"status":"ABSTAIN","reason":"NO_CURRENT_ELIGIBLE_UNMODELED_ACTION"}
    if len(xs)>1:return {"status":"ABSTAIN","reason":"UNIQUE_EXPERIMENT_SUBJECT_REQUIRED","eligible_ids":[a.capability_id for a in xs]}
    a=xs[0]
    return {"status":"UNIQUE_EXPERIMENT_SUBJECT_NOMINATED","capability_id":a.capability_id,"epoch":a.epoch,"signature":a.signature,"scope_id":a.scope_id,
            "selection_authority":"UNIQUE_ELIGIBILITY_ONLY","preference_authority":"NONE","information_value_authority":"NONE"}

def issue_from_unique(actions:list[ActionDescriptor],state:str):
    n=nominate_unique(actions)
    if n["status"]!="UNIQUE_EXPERIMENT_SUBJECT_NOMINATED":return {"nomination":n,"warrant":None}
    a=next(a for a in actions if a.capability_id==n["capability_id"] and a.epoch==n["epoch"] and a.signature==n["signature"] and a.scope_id==n["scope_id"])
    return {"nomination":n,"warrant":derive_warrant(a,state)}

def run_campaign():
    a=ActionDescriptor("A",0,"sigA","S")
    b=ActionDescriptor("B",0,"sigB","S")
    one=issue_from_unique([a],"s0"); assert one["warrant"] is not None
    auth=authorize(one["warrant"],a,"s0",0); assert auth["status"]=="AUTHORIZED_ONCE"
    none=issue_from_unique([ActionDescriptor("M",0,"sigM","S",consequence_modeled=True)],"s0")
    assert none["warrant"] is None and none["nomination"]["reason"]=="NO_CURRENT_ELIGIBLE_UNMODELED_ACTION"
    many=issue_from_unique([a,b],"s0"); assert many["warrant"] is None and many["nomination"]["reason"]=="UNIQUE_EXPERIMENT_SUBJECT_REQUIRED"
    # One action becomes ineligible through already-modeled consequence; the other may then be uniquely nominated.
    narrowed=issue_from_unique([ActionDescriptor("A",0,"sigA","S",consequence_modeled=True),b],"s1")
    assert narrowed["warrant"] is not None and narrowed["nomination"]["capability_id"]=="B"
    return {"status":"PASS","single":one["nomination"],"multiple":many["nomination"],"none":none["nomination"],"narrowed":narrowed["nomination"],
      "earned":"A1_CAN_AVOID_A_NEW_CROSS_ACTION_RANKING_POLICY_BY_ISSUING_ONLY_WHEN_CURRENT_EXPERIMENT_ELIGIBILITY_HAS_EXACTLY_ONE_SUBJECT",
      "preserve":"MULTIPLE_ELIGIBLE_UNKNOWN_ACTIONS_REQUIRE_ABSTENTION_UNLESS_A_SEPARATE_LAWFUL_SELECTOR_IS_EARNED",
      "open_seam":"ELIGIBILITY_ITSELF_STILL_DOES_NOT_PROVE_BOUNDED_DOWNSTREAM_RISK",
      "next":"NAKED_C04_RESIDUAL_RISK_CONSTITUTIONAL_BOUNDARY"}
if __name__=='__main__':print(json.dumps(run_campaign(),indent=2,sort_keys=True))
