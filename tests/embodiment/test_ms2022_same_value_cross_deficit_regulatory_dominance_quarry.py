from scratch.ms2022_same_value_cross_deficit_regulatory_dominance_quarry import run_ms2022


def test_ms2022_symmetric_cross_deficit_pressures_remain_unordered():
    r = run_ms2022()
    assert r["status"] == "PASS"
    c = r["symmetric"]["comparison"]
    assert c["status"] == "NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE"
    assert c["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    assert c["selection_authority"] == "NONE"
    assert r["symmetric"]["calls"] == []


def test_ms2022_exact_same_value_strict_residual_dominance_is_present_in_existing_rehearsal_content():
    r = run_ms2022()
    c = r["asymmetric"]["comparison"]
    assert c["status"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_QUARRY"
    assert c["dominant_probe_action_id"] == "P2"
    assert c["dominant_worst_residual_pressure"] == 0.0
    assert c["next_worst_residual_pressure"] == 0.5
    assert c["comparison_basis"] == "EXACT_SAME_VALUE_COORDINATE__STRICT_WORST_RESIDUAL_PRESSURE_ONLY"
    assert c["selection_authority"] == "NONE__RESEARCH_QUARRY_ONLY"
    assert r["asymmetric"]["calls"] == []
    assert r["new_scheduler_required"] == r["new_weighted_utility_required"] == "NO"
