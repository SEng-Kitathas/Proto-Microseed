from scratch.ms2004_unified_referent_lifetime_policy import run_ms2004


def test_ms2004_unified_referent_lifetime_policy_composes_without_new_manager_or_authority_gain():
    r = run_ms2004()
    assert r["status"] == "PASS"
    assert r["session_count"] == 4
    assert r["restart_count"] == 3
    assert r["same_world_owns_control_and_referent_observations"] == "YES"
    assert r["drift_relearning"] == "YES"
    assert r["persisted_referent_class_reentry"] == "YES"
    assert r["zero_row_policy"] == "YES"
    assert r["ambiguous_referent_policy"] == "NONE"
    assert r["capability_requalification_co_present"] == "YES"
    assert r["capability_requalification_authority_gain"] == "NONE"
    assert r["caller_supplied_runtime_bucket"] == "NO"
    assert r["caller_supplied_referent_class"] == "NO"
    assert r["caller_supplied_preferred_action"] == "NO"
    assert r["identity_authority"] == "NONE"
    assert r["semantic_reference_authority"] == "NONE"
    assert r["truth_authority"] == "NONE"
    assert r["new_cross_cutting_manager"] == "NO"
    assert r["new_referent_manager"] == "NO"
    assert r["new_policy_manager"] == "NO"
    assert r["zero_p"]["supplied_rehearsal_rows"] == 0
    assert r["zero_n"]["supplied_rehearsal_rows"] == 0
    assert r["zero_p"]["selected_actions"] == r["zero_n"]["selected_actions"]
    assert r["zero_p"]["final_state"] != r["zero_n"]["final_state"]
