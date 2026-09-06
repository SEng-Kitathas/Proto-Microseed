from scratch.lang_c08g_native_b2_ordered_composition import run_campaign


def test_c08g_native_b2_composes_current_observed_token_referent_operands_in_evidence_order():
    result = run_campaign("R4", "T9")
    assert result["status"] == "C08G_NATIVE_B2_ORDERED_COMPOSITION_REEMBODIED"
    assert result["order_sensitive"] is True
    assert result["xy_composition_digest_sha256"] != result["yx_composition_digest_sha256"]
    assert result["xy_ordered_referent_signatures"] == list(reversed(result["yx_ordered_referent_signatures"]))
    assert result["duplicate_operands"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "INDEPENDENT_NATIVE_REFERENT_OPERANDS_REQUIRED",
    }
    assert result["unseen_operand"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "EVERY_OBSERVED_TOKEN_OPERAND_MUST_HAVE_NATIVE_REFERENT_BINDING",
    }
    assert result["restart_without_fresh_profiles"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED",
    }
    assert result["post_restart_xy"] == result["post_restart_yx"] == "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED"
    assert result["composition_operator"] == "ORDERED_EVIDENCE_TUPLE"
    assert result["ordering_basis"] == "CURRENT_RUNTIME_OPAQUE_TOKEN_EVIDENCE_APPEND_ORDER"
    assert result["operand_selection_basis"] == "LATEST_TWO_CURRENT_RUNTIME_OPAQUE_TOKEN_OBSERVATIONS"
    assert result["caller_supplied_token_operands"] == "NO"
    assert result["caller_supplied_operand_order"] == "NO"
    assert result["caller_supplied_grammar_roles"] == "NO"
    assert result["caller_supplied_referent_identity"] == "NO"
    assert result["microseed_delta_required"] == []
    assert result["new_microseed_action_contracts_registered"] == []
    assert result["identity_scope"] == "OPERATIONAL_EQUIVALENCE_CLASS_ONLY"
    assert result["grammar_authority"] == result["predicate_authority"] == "NONE"
    assert result["language_authority"] == result["semantic_reference_authority"] == "NONE"
    assert "SYSTEMATIC_RECOMBINATION" in result["not_earned"]
    assert "GRAMMAR" in result["not_earned"]


def test_c08g_token_surface_permutation_preserves_grounded_composition_identity():
    base = run_campaign("R4", "T9")
    swapped = run_campaign("T9", "R4")
    assert base["xy_composition_digest_sha256"] == swapped["xy_composition_digest_sha256"]
    assert base["yx_composition_digest_sha256"] == swapped["yx_composition_digest_sha256"]
    assert base["xy_ordered_referent_signatures"] == swapped["xy_ordered_referent_signatures"]
    assert base["yx_ordered_referent_signatures"] == swapped["yx_ordered_referent_signatures"]


def test_c08g_sensor_representation_transformations_preserve_ordered_native_composition():
    base = run_campaign("R4", "T9")
    permuted = run_campaign("R4", "T9", lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign("R4", "T9", lambda row: tuple(-x for x in row))
    assert base["xy_composition_digest_sha256"] == permuted["xy_composition_digest_sha256"] == inverted["xy_composition_digest_sha256"]
    assert base["yx_composition_digest_sha256"] == permuted["yx_composition_digest_sha256"] == inverted["yx_composition_digest_sha256"]
    assert base["xy_ordered_referent_signatures"] == permuted["xy_ordered_referent_signatures"] == inverted["xy_ordered_referent_signatures"]
    assert base["yx_ordered_referent_signatures"] == permuted["yx_ordered_referent_signatures"] == inverted["yx_ordered_referent_signatures"]
