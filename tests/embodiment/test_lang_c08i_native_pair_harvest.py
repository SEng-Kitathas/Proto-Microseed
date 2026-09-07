from scratch.lang_c08i_native_pair_harvest import run_campaign


def test_c08i_auto_harvests_qualifies_and_registers_native_association_evidence():
    result = run_campaign()
    assert result["status"] == "C08I_NATIVE_OPAQUE_ASSOCIATION_PAIR_HARVEST_EARNED"
    assert result["harvested_pair_count"] == 12
    assert set(result["harvested_scopes"]) == {"NATIVE_TOKEN_REFERENT", "NATIVE_TOKEN_RELATION"}
    assert result["caller_supplied_pair_evidence_ids"] == "NO"
    assert result["caller_supplied_association_scope"] == "NO"
    assert result["caller_supplied_mapping_answer"] == "NO"
    assert result["caller_supplied_qualification_id"] == "NO"
    assert result["caller_supplied_referent_class"] == "NO"
    assert result["external_train_holdout_partition"] == "NONE"
    assert result["pairing_basis"] == "AUTO_HARVESTED_CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY"
    assert result["identity_scope"] == "OPERATIONAL_EQUIVALENCE_CLASS_ONLY"
    assert result["qualification_authority"] == "EPISTEMIC_ADEQUACY_EVIDENCE_ONLY"
    assert result["experience_generation"] == "EXOGENOUS_PASSIVE_EVENT_AND_OPAQUE_TOKEN_PRESENTATION_REMAIN"
    assert result["new_microseed_action_contracts_registered"] == []
    assert result["budget_hostile"]["status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED"
    assert result["restart_without_current_token"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "CURRENT_RUNTIME_OPAQUE_TOKEN_EVIDENCE_REQUIRED",
    }
    assert result["contradiction"] == {
        "status": "PAIR_EVIDENCE_HARVESTED_QUALIFICATION_INCOMPLETE",
        "referent_reason": "PAIR_EVIDENCE_NOT_EXACT_BIJECTION",
    }
    assert result["truth_authority"] == result["semantic_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
    assert "ACTIVE_EXPERIMENT_SELECTION_FOR_MISSING_ASSOCIATION_EVIDENCE" in result["not_earned"]
    assert "ENDOGENOUS_OPAQUE_TOKEN_GENERATION" in result["not_earned"]


def test_c08i_token_surface_permutation_preserves_grounded_right_hand_structure():
    base = run_campaign("R4", "T9", "K7", "M2")
    swapped = run_campaign("T9", "R4", "M2", "K7")
    base_refs = {right for _left, right in base["referent_bindings"]}
    swapped_refs = {right for _left, right in swapped["referent_bindings"]}
    base_rels = {right for _left, right in base["relation_bindings"]}
    swapped_rels = {right for _left, right in swapped["relation_bindings"]}
    assert base_refs == swapped_refs
    assert base_rels == swapped_rels
    assert base["harvested_pair_count"] == swapped["harvested_pair_count"] == 12


def test_c08i_sensor_representation_transformations_preserve_grounded_pair_structure():
    base = run_campaign()
    permuted = run_campaign(sensor_transform=lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign(sensor_transform=lambda row: tuple(-x for x in row))
    assert base["referent_bindings"] == permuted["referent_bindings"] == inverted["referent_bindings"]
    assert base["relation_bindings"] == permuted["relation_bindings"] == inverted["relation_bindings"]
    assert base["harvested_scopes"] == permuted["harvested_scopes"] == inverted["harvested_scopes"]
