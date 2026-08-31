from scratch.ms2036_full_frame_bound_pareto_research import run_ms2036


def test_ms2036_full_frame_tradeoff_remains_unselected():
    r = run_ms2036()
    assert r["status"] == "FULL_FRAME_BOUND_STRICT_PARETO_EARNED_RESEARCH_ONLY"
    x = r["tradeoff"]
    assert x["status"] == "PASS"
    assert x["selection"]["status"] == "NO_STRICT_PARETO_SELECTION"
    assert x["read_only"] is True
    assert x["handler_calls"] == []


def test_ms2036_full_frame_dominance_selects_p2_research_only():
    r = run_ms2036()
    x = r["dominance"]
    assert x["status"] == "PASS"
    assert x["selection"]["status"] == "CURRENT_STRICT_PARETO_SELECTION_RESEARCH_ONLY"
    assert x["selection"]["selected_probe_action_id"] == "P2"
    assert x["selection"]["research_selection_authority"] == "STRICT_PARETO_REGULATORY_DOMINANCE_ONLY"
    assert x["handler_calls"] == []


def test_ms2036_frame_drift_and_missing_state_fail_closed():
    r = run_ms2036()
    for key in ("new_value_staleness", "same_epoch_observation_staleness"):
        x = r[key]
        assert x["status"] == "PASS"
        assert x["selection"]["status"] == "DEFER_UNKNOWN"
        assert x["selection"]["reason"] == "COMPLETE_VALUE_FRAME_NOT_CURRENT_AT_SELECTION"
    assert r["missing_observation"]["surface"]["status"] == "DEFER_UNKNOWN"
    assert r["missing_effect"]["surface"]["status"] == "DEFER_UNKNOWN"


def test_ms2036_lawful_api_has_no_caller_frame_scope():
    r = run_ms2036()
    assert r["api_scope"]["caller_frame_parameter"] == "ABSENT"
    assert r["earned"] == "CROSS_VALUE_STRICT_PARETO_COMPARISON_IS_LAWFUL_ONLY_OVER_ORGANISM_OWNED_COMPLETE_CURRENT_VALUE_FRAME"
    assert r["currentness_law"] == "FULL_FRAME_CURRENTNESS_MUST_BE_REDERIVED_BEFORE_CROSS_VALUE_SELECTION"
    assert r["runtime_selection_authorized"] == "NO"
