from scratch.ms2014_endogenous_referent_opportunity_enumeration import run_unique, run_multiple

def test_ms2014_unique_owned_referent_opportunity_requires_no_caller_binding_or_deficit():
    r=run_unique(); assert r["status"]=="PASS"
    assert r["enumeration_status"]=="CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY"
    assert r["probe_action_ids"]==["P2"] and r["opportunity_count"]==1
    assert r["caller_supplied_binding_id"]==r["caller_supplied_deficit_id"]=="NO"

def test_ms2014_two_independent_live_deficits_stop_at_no_cross_deficit_selection_authority():
    r=run_multiple(); assert r["status"]=="BLOCKED_AS_DESIGNED"
    assert r["enumeration_status"]=="MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES"
    assert set(r["probe_action_ids"])=={"P2","P4"} and r["opportunity_count"]==2
    assert r["reason"]=="NO_CROSS_DEFICIT_SELECTION_AUTHORITY" and r["selection_authority"]=="NONE"
    assert r["existing_candidate_arbitration_scope"]=="SINGLE_DEFICIT_ONLY"
