from scratch.ms2035_organism_owned_current_value_frame_completeness import run_ms2035


def test_ms2035_complete_frame_rejects_caller_subset_without_new_selection_authority():
    r = run_ms2035()
    assert r["status"] == "CURRENT_VALUE_FRAME_COMPLETENESS_EARNED_RESEARCH_ONLY"
    x = r["complete_frame_and_subset_rejection"]
    assert x["status"] == "PASS"
    assert x["frame"]["status"] == "CURRENT_COMPLETE_VALUE_FRAME"
    assert x["frame"]["current_value_ids"] == ["V", "W"]
    assert x["full_vector_match"]["frame_match"] is True
    assert x["caller_subset_match"]["frame_match"] is False
    assert x["read_only"] is True
    assert x["handler_calls"] == []


def test_ms2035_missing_current_observation_blocks_whole_frame():
    r = run_ms2035()
    x = r["missing_current_observation"]
    assert x["status"] == "PASS"
    assert x["frame"]["status"] == "DEFER_UNKNOWN"
    assert x["frame"]["reason"] == "CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X"
    assert x["frame"]["current_value_ids"] == ["V", "W", "X"]
    assert x["silent_omission"] == "NO"


def test_ms2035_stale_values_leave_frame_only_via_registry_currentness():
    r = run_ms2035()
    x = r["stale_value_exclusion"]
    assert x["status"] == "PASS"
    assert x["before"]["current_value_ids"] == ["V", "W", "X"]
    assert x["after"]["current_value_ids"] == ["V", "W"]
    assert x["after"]["excluded_noncurrent_value_ids"] == ["X"]
    assert x["exclusion_basis"] == "REGISTRY_IS_CURRENT_FALSE"


def test_ms2035_new_value_and_same_epoch_observation_change_stale_old_frames():
    r = run_ms2035()
    new_value = r["new_value_invalidates_old_frame"]
    assert new_value["status"] == "PASS"
    assert new_value["old_frame_current"]["frame_current"] is False
    assert new_value["old_frame_current"]["reason"] == "VALUE_FRAME_DESCRIPTOR_DRIFT"
    obs = r["same_epoch_observation_change"]
    assert obs["status"] == "PASS"
    assert obs["epoch_unchanged"] is True
    assert obs["old_frame_current"]["frame_current"] is False
    assert obs["old_frame_current"]["reason"] == "VALUE_FRAME_DESCRIPTOR_DRIFT"


def test_ms2035_frame_is_order_independent_and_registry_rejects_duplicate_value_identity():
    r = run_ms2035()
    x = r["order_and_duplicate_identity"]
    assert x["status"] == "PASS"
    assert x["order_independent"] is True
    assert x["duplicate_identity_rejected"] is True
    assert r["earned"] == "COMPLETE_CURRENT_VALUE_FRAME_IS_DERIVABLE_FROM_VALUE_REGISTRY_WITHOUT_CALLER_SUBSET_AUTHORITY"
    assert r["missing_observation_law"] == "CURRENT_VALUE_WITHOUT_CURRENT_OBSERVATION_BLOCKS_FRAME_COMPLETENESS"
    assert r["runtime_pareto_selection_authorized"] == "NO"
