from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import run_ms2008

def test_ms2008_owned_referent_ambiguity_is_decision_bearing_and_p2_informative_without_execution():
    r=run_ms2008(False); assert r["status"]=="PASS"
    assert r["priority"]["commitment"]=="YES" and set(dict(r["priority"]["qualifiers"])["first_actions"].split("|"))=={"A","B"}
    assert r["information"]["commitment"]=="YES"
    assert r["nominated_capability_id"]=="P2" and r["handler_calls"]==[]
    assert r["caller_supplied_decision_alternatives"]=="NO" and r["execution_authority"]=="NONE"

def test_ms2008_same_downstream_action_removes_decision_bearing_pressure():
    r=run_ms2008(True); assert r["status"]=="PASS"
    assert r["same_downstream_priority"]["commitment"]!="YES"
    assert r["nomination_status"]=="ABSTAIN"
