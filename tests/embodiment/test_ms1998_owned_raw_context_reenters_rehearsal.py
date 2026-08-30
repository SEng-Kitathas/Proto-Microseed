from scratch.ms1998_owned_raw_context_reenters_rehearsal import run_ms1998


def test_ms1998_owned_current_raw_projection_reenters_existing_rehearsal_without_caller_bucket():
    result = run_ms1998()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["caller_supplied_projection_bucket"] == "NO"
    assert result["caller_supplied_routed_relation"] == "NO"
    assert result["current_context_basis"] == "CURRENT_BOUNDED_RAW_OBSERVATION_PLUS_EXACT_ADMITTED_PROJECTION"
    assert result["even_path"] == ["ALIAS", "EVEN"]
    assert result["odd_path"] == ["ALIAS", "ODD"]
    assert result["duplicate_current_receipts"] == "DEFER_UNKNOWN_NO_REHEARSAL"
    assert result["new_persistent_state_owner"] == "NO"
    assert result["selection_authority"] == result["truth_authority"] == result["execution_authority"] == result["semantic_projection_authority"] == "NONE"
    assert result["new_core_mechanism_required"] == "YES__NARROW_COMPOSITION_BRIDGE_ONLY"
