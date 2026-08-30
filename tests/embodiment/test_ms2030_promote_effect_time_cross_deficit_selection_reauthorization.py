from scratch.ms2030_promote_effect_time_cross_deficit_selection_reauthorization import run_ms2030


def test_ms2030_stable_selection_executes_and_records_nomination_plus_fresh_selection_lineage():
    r = run_ms2030()
    s = r["stable"]
    assert s["status"] == "PASS"
    assert s["execution"]["status"] == "ACTION_EXECUTED"
    assert s["handler_calls"] == ["P2"]
    assert s["execution_lineage_contains_nomination_and_fresh_selection"] == "YES"
    premises = set(s["execution"]["execution"]["execution_premise_ids"])
    assert s["selected_unknown_evidence_id"] in premises
    assert s["nomination_selection_commitment_id"] in premises
    assert s["fresh_selection_commitment_id"] in premises


def test_ms2030_new_equal_competitor_blocks_before_effect():
    r = run_ms2030()
    x = r["new_competitor_block"]
    assert x["status"] == "PASS"
    assert x["fresh_selection"]["selection_commitment"]["reason"] == "WORST_RESIDUAL_PRESSURE_TIE"
    assert x["execution"]["status"] == "NO_EXECUTION"
    assert x["execution"]["reason"] == "CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION"
    assert x["handler_calls"] == []


def test_ms2030_forged_selected_unknown_ancestry_fails_closed():
    r = run_ms2030()
    x = r["forged_selected_unknown_ancestry_block"]
    assert x["status"] == "PASS"
    assert x["execution"]["status"] == "NO_EXECUTION"
    assert x["handler_calls"] == []
    assert r["ordinary_effect_owner"] == "CapabilityRegistry.invoke"
    assert r["new_scheduler_required"] == "NO"
    assert r["execution_authority_added_to_selection"] == "NO"
