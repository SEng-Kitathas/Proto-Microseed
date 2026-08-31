from scratch.ms2040_violation_effect_time_full_frame_selection_staleness import run_ms2040


def test_ms2040_historical_full_frame_selection_violation_is_closed_by_effect_time_reauthorization():
    r = run_ms2040()
    assert r["status"] == "HISTORICAL_VIOLATION_CLOSED"
    assert r["fresh_full_frame_selection"]["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert r["fresh_full_frame_selection"]["selection_authority"] == "NONE"
    assert r["execution"]["status"] == "NO_EXECUTION"
    assert r["execution"]["reason"] == "CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION"
    assert r["handler_calls"] == []
    assert r["full_frame_selection_reauthorized_at_effect"] == "YES"
    assert r["violation"] == "NOMINATION_TIME_FULL_FRAME_SELECTION != EFFECT_TIME_FULL_FRAME_SELECTION_CURRENTNESS"
