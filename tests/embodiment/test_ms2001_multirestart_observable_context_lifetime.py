from scratch.ms2001_multirestart_observable_context_lifetime import run_ms2001


def test_ms2001_multirestart_observable_context_lifetime():
    result = run_ms2001()
    assert result["status"] == "PASS"
    assert len(result["sessions"]) == 4
    assert result["sessions"][-1]["outcomes"] == 258
    assert result["automatic_reauthorization"] == "NO__FRESH_ENVIRONMENT_AUTHORITY_EACH_SESSION"
    assert result["caller_supplied_projection_bucket"] == "NO"
    assert result["caller_supplied_routed_relation"] == "NO"
    assert result["evaluator_mode_durable_evidence"] == "NO"
    assert result["new_cross_cutting_manager"] == "NO"
    assert result["projection_subset_evaluation_budget"] == 2
    assert result["projection_search_complete_under_budget"] == "YES"
    assert result["capability_requalification_co_present"] == "YES"
    assert result["capability_requalification_authority_gain"] == "NONE"
    assert result["capability_requalification_signature_preserved"] is True
    assert result["sessions"][-1]["zero_p"]["selected_actions"] == ["K-17", "M-23", "R-41"]
    assert result["sessions"][-1]["zero_n"]["selected_actions"] == ["K-17", "M-23", "R-41"]
