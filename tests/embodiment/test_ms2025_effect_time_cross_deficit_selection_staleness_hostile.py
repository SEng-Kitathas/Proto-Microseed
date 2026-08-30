from scratch.ms2025_effect_time_cross_deficit_selection_staleness_hostile import run_ms2025

def test_ms2025_historical_stale_selection_violation_is_closed_by_native_effect_time_reauthorization():
    r=run_ms2025()
    assert r["status"]=="HISTORICAL_VIOLATION_CLOSED"
    assert r["execution_status"]=="NO_EXECUTION"
    assert r["execution_reason"]=="CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION"
    assert r["handler_calls"]==[]
    assert r["cross_deficit_selection_reauthorized_at_effect"]=="YES"
