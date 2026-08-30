from scratch.ms2026_fresh_cross_deficit_selection_reauthorization_adapter import run_ms2026


def test_ms2026_stable_cross_deficit_selection_delegates_one_effect_to_ordinary_executor():
    r = run_ms2026()
    x = r["stable"]
    assert x["status"] == "PASS"
    assert x["result"]["status"] == "ACTION_EXECUTED"
    assert x["calls"] == ["P2"]
    assert x["result"]["execution_authority"] == "DELEGATED_TO_ORDINARY_EXECUTOR_ONLY"


def test_ms2026_new_equal_competitor_blocks_before_effect():
    r = run_ms2026()
    x = r["new_competitor_block"]
    assert x["status"] == "PASS"
    assert x["result"]["status"] == "NO_EXECUTION"
    assert x["result"]["reason"] == "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED"
    assert x["result"]["fresh_comparison"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    assert x["calls"] == []
    assert r["new_scheduler_required"] == r["persistent_opportunity_registry_required"] == "NO"
