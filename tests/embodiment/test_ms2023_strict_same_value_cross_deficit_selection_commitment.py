from scratch.ms2023_strict_same_value_cross_deficit_selection_commitment import run_ms2023


def test_ms2023_strict_same_value_dominance_can_license_only_one_cross_deficit_selection():
    r = run_ms2023()
    assert r["status"] == "PASS"
    sym = r["symmetric"]["commitment"]
    assert sym["commitment"] == "UNKNOWN"
    assert sym["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    asym = r["asymmetric"]["commitment"]
    assert asym["commitment"] == "YES"
    q = dict(asym["qualifiers"])
    assert q["selected_probe_action_id"] == "P2"
    assert q["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"
    assert q["execution_authority"] == "NONE"
    assert r["symmetric"]["calls"] == r["asymmetric"]["calls"] == []


def test_ms2023_current_value_observation_drift_erases_prior_cross_deficit_dominance():
    r = run_ms2023()
    d = r["value_observation_drift"]
    assert d["status"] == "PASS"
    assert d["before"]["commitment"] == "YES"
    assert d["after"]["commitment"] != "YES"
    assert dict(d["after"]["qualifiers"])["selection_authority"] == "NONE"
    assert d["calls"] == []
    assert r["new_scheduler_required"] == r["new_weighted_utility_required"] == "NO"
