from scratch.ms2041_repair_effect_time_full_frame_selection_reauthorization import run_ms2041


def test_ms2041_stable_full_frame_selection_executes_and_records_full_ancestry():
    r = run_ms2041()
    s = r["stable"]
    assert r["status"] == "PASS"
    assert s["execution"]["status"] == "ACTION_EXECUTED"
    assert s["handler_calls"] == ["P2"]
    assert s["execution_lineage_contains_full_frame_nomination_and_fresh_selection"] == "YES"
    premises = set(s["execution"]["execution"]["execution_premise_ids"])
    assert s["selected_unknown_evidence_id"] in premises
    assert s["nomination_selection_commitment_id"] in premises
    assert s["fresh_selection_commitment_id"] in premises
    assert s["nomination_frame_digest"] in premises


def test_ms2041_new_current_value_without_effects_blocks_before_handler():
    r = run_ms2041()
    x = r["new_value_block"]
    assert x["fresh_selection"]["status"] == "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert x["execution"]["status"] == "NO_EXECUTION"
    assert x["execution"]["reason"] == "CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION"
    assert x["handler_calls"] == []


def test_ms2041_forged_selected_unknown_fails_closed_and_effect_owner_unchanged():
    r = run_ms2041()
    x = r["forged_unknown_block"]
    assert x["execution"]["status"] == "NO_EXECUTION"
    assert x["handler_calls"] == []
    assert r["ordinary_effect_owner"] == "CapabilityRegistry.invoke"
    assert r["selection_execution_authority"] == "NONE"
    assert r["new_scheduler_required"] == "NO"
