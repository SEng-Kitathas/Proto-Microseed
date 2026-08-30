from scratch.ms2026_fresh_cross_deficit_selection_reauthorization_adapter import run_ms2026

def test_ms2026_historical_adapter_is_superseded_by_native_stable_reauthorization():
    r=run_ms2026()
    assert r["status"]=="HISTORICAL_ADAPTER_SUPERSEDED_BY_NATIVE_RUNTIME"
    x=r["stable"]
    assert x["status"]=="PASS"
    assert x["execution"]["status"]=="ACTION_EXECUTED"
    assert x["calls"]==["P2"]
    assert x["native_reauthorization_owner"]=="MS2030_RUNTIME"

def test_ms2026_native_runtime_blocks_new_equal_competitor_before_effect():
    r=run_ms2026()
    x=r["new_competitor_block"]
    assert x["status"]=="PASS"
    assert x["execution"]["status"]=="NO_EXECUTION"
    assert x["execution"]["reason"]=="CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION"
    assert x["calls"]==[]
    assert r["new_scheduler_required"]==r["persistent_opportunity_registry_required"]=="NO"
