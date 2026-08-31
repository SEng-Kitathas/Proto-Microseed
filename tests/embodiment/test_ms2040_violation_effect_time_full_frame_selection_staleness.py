from scratch.ms2040_violation_effect_time_full_frame_selection_staleness import run_ms2040


def test_ms2040_stale_full_frame_selection_still_executes_before_repair():
    r = run_ms2040()
    assert r["status"] == "VIOLATION_REPRODUCED"
    assert r["fresh_full_frame_selection"]["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert r["fresh_full_frame_selection"]["selection_authority"] == "NONE"
    assert r["execution"]["status"] == "ACTION_EXECUTED"
    assert r["handler_calls"] == ["P2"]
    assert r["violation"] == "NOMINATION_TIME_FULL_FRAME_SELECTION != EFFECT_TIME_FULL_FRAME_SELECTION_CURRENTNESS"
    assert r["marker_bypass"] == "UNRECOGNIZED_SELECTED_ORIGIN_MARKER_BYPASSES_EFFECT_TIME_GLOBAL_SELECTION_REAUTHORIZATION"
