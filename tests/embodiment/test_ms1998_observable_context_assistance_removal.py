from scratch.ms1998_observable_context_assistance_removal import MAIN, run_ms1998


def test_ms1998_observable_context_removes_evaluator_mode_guidance_and_reaches_zero_row_handoff():
    result = run_ms1998()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["training_guidance_reads_evaluator_mode"] == "NO"
    assert result["training_guidance_basis"] == "CURRENT_ORGANISM_VISIBLE_CONTROL_STATE_PLUS_REGULATORY_VALUE_ONLY"
    assert result["terminal_identity_supplied_during_training"] == "NO"
    assert result["caller_supplied_preferred_action"] == "NO__ALL_CURRENT_OPAQUE_OPTIONS_PRESENT"
    assert result["caller_supplied_projection_bucket"] == "NO__CORE_BRIDGE_DERIVES_CURRENT_BUCKET_FROM_OWNED_RAW_EVIDENCE"
    assert result["caller_supplied_routed_relation"] == "NO"
    assert result["owned_raw_projection_sample_count"] >= 180
    assert result["context_projection_validation_accuracy"] == 1.0
    assert result["missing_raw_context_policy"] == "DEFER_UNKNOWN"
    assert result["duplicate_raw_context_policy"] == "DEFER_UNKNOWN"
    assert result["historical_relation_global_reactivation"] == "NO__STALE_RELATION_REUSED_ONLY_INSIDE_QUALIFIED_CONTEXT_ROUTE"
    assert result["semantic_regime_authority"] == "NONE"
    assert result["model_switch_authority"] == "NONE"
    assert result["execution_authority_gain"] == "NONE"
    assert result["zero_row_handoff"] == "YES"
    assert result["zero_row_historical"]["selected_actions"] == list(MAIN)
    assert result["zero_row_replacement"]["selected_actions"] == list(MAIN)
    assert result["zero_row_historical"]["supplied_rehearsal_row_count"] == 0
    assert result["zero_row_replacement"]["supplied_rehearsal_row_count"] == 0
    assert result["zero_row_historical"]["final_state"] == "u"
    assert result["zero_row_replacement"]["final_state"] == "v"
    assert result["zero_row_historical"]["final_value"] == 0.0
    assert result["zero_row_replacement"]["final_value"] == 0.0
    assert result["new_core_mechanism_required"] == "YES__NARROW_COMPOSITION_BRIDGE_ONLY__NO_NEW_STATE_OR_POLICY_OWNER"
