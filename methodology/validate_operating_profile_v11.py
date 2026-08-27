from __future__ import annotations
import copy,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location("v10",ROOT/"validate_operating_profile_v10.py")
v10=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(v10)
PROFILE=ROOT/"MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_1.json"
REQ={
"BEHAVIORAL_SYNCHRONY_NE_CAUSAL_AUTHORSHIP":"SYNCHRONY_LAUNDERED_AS_AUTHORSHIP",
"BEHAVIORAL_EQUIVALENCE_NE_GENEALOGICAL_RELATION":"BEHAVIOR_LAUNDERED_AS_GENEALOGY",
"COMMON_ANCESTRY_NE_SHARED_CURRENT_ACTION_AUTHORITY":"COMMON_ANCESTRY_LAUNDERED_AS_SHARED_ACTION_AUTHORITY",
"STABLE_COUNTERPARTY_HANDLE_NE_CURRENT_RELATION":"HANDLE_LAUNDERED_AS_CURRENT_RELATION",
"PARENT_PRESSURE_NE_CHILD_VALUE_STATE":"PARENT_VALUE_LAUNDERED_AS_CHILD_VALUE",
"OWN_CAPABILITY_CURRENT_NE_DISTRIBUTED_CAPABILITY_CURRENT":"LOCAL_CURRENTNESS_LAUNDERED_AS_DISTRIBUTED_CURRENTNESS",
"COUNTERPARTY_RELATION_NE_PERSISTENT_NUMERICAL_AGENT_IDENTITY":"RELATION_LAUNDERED_AS_AGENT_IDENTITY",
"RELATIONAL_IDENTIFIABILITY_NE_TRACTABLE_PARTNER_COMBINATION_SEARCH":"IDENTIFIABILITY_LAUNDERED_AS_TRACTABILITY",
"distributed_capability_must_bind_counterparty_epoch_when_counterparty_is_load_bearing":"COUNTERPARTY_EPOCH_DEPENDENCY_DROPPED",
"counterparty_contract_grants_operational_role_currentness_only":"COUNTERPARTY_CONTRACT_AUTHORITY_INFLATED",
"passive_common_cause_requires_intervention_or_unknown":"COMMON_CAUSE_ATTACK_DROPPED",
"social_other_agent_research_remains_prelingual":"LANGUAGE_SMUGGLED_INTO_SOCIAL_AUDIT",
}
def validate(p):
    # ensure v1.0 baseline itself remains valid
    ok10,e10=v10.validate(json.loads(v10.PROFILE.read_text()));e=list(e10)
    if not ok10 and not e:e.append("V10_ANCESTRY_INVALID")
    if p.get("inherits")!="microseed.maindev-operating-profile.v1.0":e.append("V11_ANCESTRY_LOST")
    if p.get("core_shape_unchanged") is not True:e.append("V11_CORE_METHOD_REPLACED")
    for k,err in REQ.items():
        if not p.get("refinements_from_ms1053_1077",{}).get(k):e.append(err)
    lang=p.get("language_policy",{})
    if lang.get("active_phase")!="PRELINGUAL" or lang.get("cognitive_substrate")!="DEFERRED":e.append("LANGUAGE_PREMATURELY_ADMITTED")
    ci=p.get("current_integration",{})
    if ci.get("research_terminal_ms")!=1077:e.append("WRONG_RESEARCH_TERMINAL")
    if ci.get("ms1078_started") is not False:e.append("HARD_STOP_MS1078_VIOLATED")
    if ci.get("selected_frontier")!="ATTN-MS1077-PRELINGUAL-COORDINATION-COMMITMENT-AND-JOINT-ACTION-GROUNDING":e.append("WRONG_SELECTED_FRONTIER")
    for item in ("PERSISTENT_OTHER_AGENT_IDENTITY_NOT_QUALIFIED","GENERAL_THEORY_OF_MIND","GENERAL_MULTI_AGENT_PLANNING","GENERAL_PARTNER_COMBINATION_SEARCH","PRELINGUAL_COORDINATION_COMMITMENT_JOINT_ACTION_GROUNDING"):
        if item not in ci.get("integration_debt_open",[]):e.append("OPEN_FRONTIER_DROPPED:"+item)
    if "MS1067_V10_NO_FIRST_CLASS_COUNTERPARTY_CURRENTNESS" not in ci.get("integration_debt_resolved",[]):e.append("COUNTERPARTY_INTEGRATION_DEBT_NOT_RECORDED")
    return not e,e
def mutants(p):
    out=[]
    x=copy.deepcopy(p);x["core_shape_unchanged"]=False;out.append(("replace_core_method",x))
    for k in REQ:
        x=copy.deepcopy(p);x["refinements_from_ms1053_1077"][k]=False;out.append(("drop_"+k.lower(),x))
    x=copy.deepcopy(p);x["language_policy"]["cognitive_substrate"]="ACTIVE";out.append(("premature_language",x))
    x=copy.deepcopy(p);x["current_integration"]["ms1078_started"]=True;out.append(("quiet_next_pass",x))
    x=copy.deepcopy(p);x["inherits"]="NONE";out.append(("drop_method_ancestry",x))
    x=copy.deepcopy(p);x["current_integration"]["integration_debt_open"]=[];out.append(("erase_open_frontiers",x))
    x=copy.deepcopy(p);x["current_integration"]["integration_debt_resolved"]=[];out.append(("erase_resolved_debt",x))
    x=copy.deepcopy(p);x["current_integration"]["research_terminal_ms"]=1078;out.append(("lie_about_terminal",x))
    x=copy.deepcopy(p);x["current_integration"]["selected_frontier"]="LOCAL_SOCIAL_HELIX_ONLY";out.append(("replace_cross_family_frontier",x))
    # authority inflation mutant
    x=copy.deepcopy(p);x["refinements_from_ms1053_1077"]["counterparty_contract_grants_operational_role_currentness_only"]=False;out.append(("inflate_counterparty_identity_authority",x))
    return out
def main():
    p=json.loads(PROFILE.read_text());ok,errs=validate(p);rej=[];esc=[]
    for name,m in mutants(p):
        mok,merr=validate(m)
        if mok:esc.append(name)
        else:rej.append({"mutant":name,"errors":merr})
    out={"schema":"microseed.maindev-operating-profile-validation.v1.1","baseline_pass":ok,"baseline_errors":errs,"hostile_mutants":len(rej)+len(esc),"hostile_mutants_rejected":len(rej),"escaped":esc,"all_pass":ok and not esc}
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if out["all_pass"] else 1
if __name__=="__main__":raise SystemExit(main())
