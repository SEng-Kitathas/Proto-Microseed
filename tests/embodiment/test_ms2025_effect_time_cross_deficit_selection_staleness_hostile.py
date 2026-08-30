from scratch.ms2025_effect_time_cross_deficit_selection_staleness_hostile import run_ms2025


def test_ms2025_new_equal_competitor_after_nomination_exposes_stale_cross_deficit_selection_at_effect_time():
    r = run_ms2025()
    assert r["status"] == "VIOLATION_REPRODUCED"
    assert r["selected_probe_at_nomination"] == "P2"
    assert set(r["fresh_probe_action_ids"]) >= {"P2", "P4"}
    assert r["fresh_comparison"]["status"] == "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE"
    assert r["fresh_selection"]["commitment"] != "YES"
    assert r["execution_status"] == "ACTION_EXECUTED"
    assert r["handler_calls"] == ["P2"]
    assert r["local_selected_deficit_remained_current"] == "YES"
    assert r["cross_deficit_selection_reauthorized_at_effect"] == "NO"
