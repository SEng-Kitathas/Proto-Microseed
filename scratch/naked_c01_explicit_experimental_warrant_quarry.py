from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
import json

@dataclass(frozen=True)
class ActionDescriptor:
    capability_id: str
    epoch: int
    signature: str
    scope_id: str
    current: bool = True
    qualified: bool = True
    represented: bool = True
    consequence_modeled: bool = False

@dataclass(frozen=True)
class ConstitutionalExperimentalWarrant:
    warrant_id: str
    capability_id: str
    capability_epoch: int
    capability_signature: str
    scope_id: str
    issue_state_digest: str
    max_invocations: int
    current: bool
    authority: str = "NAKED_EXPERIMENTAL_EFFECT_ONCE"
    purpose: str = "FIRST_UNMODELED_PHYSICAL_SAMPLE"


def digest(x: object) -> str:
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def derive_warrant(action: ActionDescriptor, state_digest: str) -> ConstitutionalExperimentalWarrant | None:
    # This is the candidate NEW constitutional premise under study. It is not
    # claimed to follow from V1 and carries no information-value/utility input.
    if not (action.current and action.qualified and action.represented):
        return None
    if action.consequence_modeled:
        return None
    payload={"capability_id":action.capability_id,"epoch":action.epoch,"signature":action.signature,
             "scope_id":action.scope_id,"issue_state_digest":state_digest,"max_invocations":1}
    return ConstitutionalExperimentalWarrant("NW-"+digest(payload)[:20],action.capability_id,action.epoch,
        action.signature,action.scope_id,state_digest,1,True)


def authorize(w: ConstitutionalExperimentalWarrant | None, action: ActionDescriptor, state_digest: str,
              invocation_count: int, *, ordinary_capability_authority: bool=True) -> dict[str,object]:
    base={"selection_authority":"NONE","truth_authority":"NONE","semantic_goal_authority":"NONE",
          "information_value_authority":"NONE","general_action_authority":"NONE"}
    if w is None: return {**base,"status":"ABSTAIN","reason":"CURRENT_EXPERIMENTAL_WARRANT_REQUIRED"}
    if not w.current: return {**base,"status":"ABSTAIN","reason":"EXPERIMENTAL_WARRANT_NOT_CURRENT"}
    if not ordinary_capability_authority: return {**base,"status":"ABSTAIN","reason":"ORDINARY_CAPABILITY_AUTHORITY_REQUIRED"}
    if not (action.current and action.qualified and action.represented):
        return {**base,"status":"ABSTAIN","reason":"CURRENT_QUALIFIED_REPRESENTED_ACTION_REQUIRED"}
    exact=(w.capability_id==action.capability_id and w.capability_epoch==action.epoch and
           w.capability_signature==action.signature and w.scope_id==action.scope_id)
    if not exact: return {**base,"status":"ABSTAIN","reason":"EXACT_WARRANT_ACTION_BINDING_REQUIRED"}
    if w.issue_state_digest!=state_digest:
        return {**base,"status":"ABSTAIN","reason":"WARRANT_ISSUE_STATE_CURRENTNESS_REQUIRED"}
    if invocation_count>=w.max_invocations:
        return {**base,"status":"ABSTAIN","reason":"EXPERIMENTAL_WARRANT_EXHAUSTED"}
    if action.consequence_modeled:
        return {**base,"status":"ABSTAIN","reason":"FIRST_UNMODELED_SAMPLE_ONLY"}
    return {**base,"status":"AUTHORIZED_ONCE","reason":"EXACT_CURRENT_CONSTITUTIONAL_EXPERIMENTAL_WARRANT",
            "execution_authority":"BOUNDED_BY_WARRANT_AND_ORDINARY_CAPABILITY_AUTHORITY",
            "remaining_after_effect":w.max_invocations-invocation_count-1}


def run_campaign() -> dict[str,object]:
    a=ActionDescriptor("A",3,"sig-A3","S")
    state="state-17"
    w=derive_warrant(a,state); assert w is not None
    positive=authorize(w,a,state,0); assert positive["status"]=="AUTHORIZED_ONCE" and positive["remaining_after_effect"]==0
    hostiles={
      "repeat":authorize(w,a,state,1),
      "different_capability":authorize(w,replace(a,capability_id="B"),state,0),
      "epoch_drift":authorize(w,replace(a,epoch=4),state,0),
      "signature_drift":authorize(w,replace(a,signature="sig-A3-mut"),state,0),
      "scope_drift":authorize(w,replace(a,scope_id="T"),state,0),
      "state_drift":authorize(w,a,"state-18",0),
      "capability_stale":authorize(w,replace(a,current=False),state,0),
      "qualification_lost":authorize(w,replace(a,qualified=False),state,0),
      "ordinary_authority_missing":authorize(w,a,state,0,ordinary_capability_authority=False),
      "already_modeled":authorize(w,replace(a,consequence_modeled=True),state,0),
      "no_warrant":authorize(None,a,state,0),
      "warrant_stale":authorize(replace(w,current=False),a,state,0),
    }
    assert all(v["status"]=="ABSTAIN" for v in hostiles.values()),hostiles
    assert positive["information_value_authority"]==positive["general_action_authority"]=="NONE"
    return {"status":"PASS","candidate_family":"A1_EXPLICIT_CONSTITUTIONAL_EXPERIMENTAL_WARRANT",
            "positive":positive,"hostiles":hostiles,
            "earned":"ONE_SHOT_EXACT_ACTION_BOUND_CURRENT_STATE_BOUND_EXPERIMENTAL_WARRANT_CAN_BE_DEFINED_WITHOUT_INFORMATION_VALUE_OR_GENERAL_ACTION_AUTHORITY",
            "not_earned":"THE_CONSTITUTIONAL_PREMISE_IS_NOT_YET_JUSTIFIED_OR_PROMOTED; DOWNSTREAM_RISK_IS_NOT PROVEN BOUNDED",
            "next":"PRESS_WARRANT_ISSUANCE_RULE_AND_POST_EFFECT_CONSUMPTION_AGAINST_SELF_AUTHORIZATION_AND_CRASH_WINDOWS"}

if __name__=='__main__': print(json.dumps(run_campaign(),indent=2,sort_keys=True))
