from scratch.ms2034_pareto_value_frame_completeness_authority_blocker import run_ms2034


def test_ms2034_full_frame_tradeoff_remains_unselected_and_order_independent():
    r = run_ms2034()
    x = r["full_frame_tradeoff"]
    assert r["status"] == "SUBSTANTIVE_VALUE_FRAME_AUTHORITY_BLOCKER_REPRODUCED"
    assert x["status"] == "PASS"
    assert x["selection"]["status"] == "NO_STRICT_PARETO_SELECTION"
    assert x["selection"]["reason"] == "NO_UNIQUE_STRICT_PARETO_DOMINATOR"
    assert x["order_independent"] is True


def test_ms2034_caller_omission_can_create_false_pareto_dominance():
    r = run_ms2034()
    x = r["caller_subset_violation"]
    assert x["status"] == "AUTHORITY_VIOLATION_REPRODUCED"
    assert x["full_frame_selection"]["status"] == "NO_STRICT_PARETO_SELECTION"
    assert x["caller_subset_selection"]["status"] == "CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY"
    assert x["caller_subset_selection"]["selected_probe_action_id"] == "P2"
    assert x["omitted_coordinate"] == "W"
    assert x["false_dominance_created_by_omission"] == "YES"
    assert x["handler_calls"] == []


def test_ms2034_current_frame_descriptor_drift_blocks_comparison():
    r = run_ms2034()
    x = r["frame_descriptor_drift_block"]
    assert x["status"] == "PASS"
    assert x["selection"]["status"] == "DEFER_UNKNOWN"
    assert x["selection"]["reason"] == "EXACT_MATCHING_CURRENT_VALUE_FRAME_REQUIRED"
    assert x["handler_calls"] == []


def test_ms2034_incomplete_vector_blocks_comparison():
    r = run_ms2034()
    x = r["incomplete_vector_block"]
    assert x["status"] == "PASS"
    assert x["selection"]["status"] == "DEFER_UNKNOWN"
    assert x["selection"]["reason"] == "COMPLETE_CURRENT_VECTOR_REQUIRED"
    assert r["blocker"] == "EXACT_MATCHING_VECTOR_FRAME != COMPLETE_CURRENT_VALUE_FRAME"
    assert r["scar"] == "CALLER_SELECTED_VALUE_SUBSET_CAN_CREATE_FALSE_PARETO_DOMINANCE"
    assert r["runtime_pareto_selection_authorized"] == "NO"
