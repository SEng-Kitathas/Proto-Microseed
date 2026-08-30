from scratch.ms2027_promote_strict_same_value_cross_deficit_selection import run_ms2027


def test_ms2027_priority_owner_preserves_ties_and_licenses_only_strict_same_value_dominance():
    r = run_ms2027()
    assert r["status"] == "PASS"
    assert r["symmetric"]["commitment"]["commitment"] == "UNKNOWN"
    assert r["symmetric"]["commitment"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    asym = r["asymmetric"]["commitment"]
    assert asym["commitment"] == "YES"
    q = dict(asym["qualifiers"])
    assert q["selected_probe_action_id"] == "P2"
    assert q["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"
    assert q["execution_authority"] == "NONE"


def test_ms2027_fresh_value_observation_and_cross_value_rows_fail_closed():
    r = run_ms2027()
    assert r["value_drift"]["before"]["commitment"] == "YES"
    assert r["value_drift"]["after"]["commitment"] != "YES"
    assert r["value_drift"]["after"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    cross = r["cross_value_refusal"]["commitment"]
    assert cross["commitment"] != "YES"
    assert cross["reason"] == "EXACT_SAME_VALUE_COORDINATE_REQUIRED"
    assert dict(cross["qualifiers"])["selection_authority"] == "NONE"
    assert r["new_scheduler_required"] == r["new_weighted_utility_required"] == "NO"
    assert r["runtime_orchestration_added"] == "NO"
