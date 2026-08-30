from scratch.ms2028_promote_current_owned_referent_opportunity_selection_surface import run_ms2028


def test_ms2028_runtime_owned_opportunity_surface_preserves_tie_and_selects_only_strict_same_value_case():
    r = run_ms2028()
    assert r["status"] == "PASS"
    sym = r["symmetric"]
    assert sym["surface"]["status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES"
    assert sym["selection"]["status"] == "NO_CURRENT_STRICT_CROSS_DEFICIT_SELECTION"
    assert sym["selection"]["selection_commitment"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    asym = r["asymmetric"]
    assert asym["selection"]["status"] == "CURRENT_STRICT_SAME_VALUE_CROSS_DEFICIT_SELECTION"
    assert asym["selection"]["selected_probe_action_id"] == "P2"
    assert asym["selection"]["selection_authority"] == "STRICT_SAME_VALUE_REGULATORY_DOMINANCE_ONLY"


def test_ms2028_runtime_surface_is_read_only_and_value_drift_erases_opportunities():
    r = run_ms2028()
    for key in ("symmetric", "asymmetric", "value_drift"):
        assert tuple(r[key]["before"]) == tuple(r[key]["after"])
        assert r[key]["calls"] == []
    assert r["value_drift"]["surface"]["status"] == "NO_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY"
    assert r["persistent_state_created"] == "NO"
    assert r["execution_authority"] == "NONE"
    assert r["new_scheduler_required"] == "NO"
