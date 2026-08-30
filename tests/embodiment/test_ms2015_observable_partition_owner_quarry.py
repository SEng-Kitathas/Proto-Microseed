from scratch.ms2015_observable_partition_owner_quarry import run_ms2015


def test_ms2015_existing_contrast_owner_represents_raw_information_without_state_split():
    r = run_ms2015()
    assert r["status"] == "PASS"
    assert r["existing_owner_sufficient"] == "YES__EPISTEMIC_CONTRAST_ROW"
    assert r["missing_surface"] == "PROGRAM_INFORMATION_WIRING_TO_OWNED_OBSERVABLE_CONTRAST"
    assert r["p2_control_state_predictions"] == ["s0", "s0"]
    assert r["raw_probe_action_id"] == "P2"
    assert r["trace_information"]["commitment"] == "NO"
    assert r["trace_information"]["reason"] == "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
    assert r["contrast_signature_content_sensitive"] is True
    assert r["transition_model_fields_in_contrast_row"] == []
    assert r["execution_authority"] == r["truth_authority"] == r["semantic_reference_authority"] == "NONE"
    assert r["handler_calls"] == []
