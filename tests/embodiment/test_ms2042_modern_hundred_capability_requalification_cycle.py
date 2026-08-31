from scratch.ms2042_modern_hundred_capability_requalification_cycle import run_ms2042


def test_ms2042_modern_hundred_capability_cycle_closes_with_full_frame_selection_co_present():
    r = run_ms2042()
    assert r["status"] == "MODERN_LARGE_N_CAPABILITY_CYCLE_EARNED"
    x = r["unrelated_chain"]
    assert x["status"] == "PASS"
    assert x["before_effect_count"] == 100
    assert x["during_effect_count"] == 90
    assert x["after_effect_count"] == 100
    assert x["stale_count"] == 10
    assert x["selection_before"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert x["selection_during"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert x["selection_after"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert x["selected_probe_before_after"] == ["P2", "P2"]
    assert x["same_identity_signatures_preserved"] is True
    assert x["authority_gain"] == "NONE"
    assert x["dependent_auto_reactivation"] == "NONE"
    assert x["new_manager_required"] == "NO"
    assert x["handler_calls"] == []


def test_ms2042_capability_requalification_does_not_resurrect_stale_relational_evidence():
    r = run_ms2042()
    x = r["critical_p2_boundary"]
    assert x["status"] == "PASS_BOUNDARY"
    assert x["before_effect_count"] == 100
    assert x["during_effect_count"] == 99
    assert x["after_effect_count"] == 100
    assert x["selection_before"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert x["selection_during"] == "NO_CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED"
    assert x["selection_after_requalification"] == "NO_CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED"
    assert x["derived_relational_evidence_auto_requalified"] == "NO"
    assert x["same_identity_signatures_preserved"] is True
    assert x["handler_calls"] == []
    assert r["boundary"] == "CAPABILITY_REQUALIFICATION_CURRENTNESS != DERIVED_RELATIONAL_EVIDENCE_REQUALIFICATION"
