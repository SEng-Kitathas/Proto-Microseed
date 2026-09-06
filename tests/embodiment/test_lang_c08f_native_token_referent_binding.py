from scratch.lang_c08f_native_token_referent_binding import run_campaign


def _mapping(result):
    return {item["opaque_token"]: item["operational_referent_signature_sha256"] for item in result["bindings"]}


def test_c08f_observed_tokens_bind_restart_safe_native_operational_referent_classes():
    result = run_campaign("R4", "T9")
    assert result["status"] == "C08F_NATIVE_OBSERVED_TOKEN_REFERENT_BINDING_REEMBODIED"
    assert result["token_x_resolution"] == result["token_y_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT"
    assert result["unseen_token"] == "DEFER_UNKNOWN"
    assert result["wrong_referent"] == "DEFER_UNKNOWN"
    assert result["holdout_reversal"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "HOLDOUT_TOKEN_NATIVE_REFERENT_ASSOCIATION_DISAGREES",
    }
    assert result["ambiguous_holdout"] == "DEFER_UNKNOWN"
    assert set(result["association_states_after_restart"].values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
    assert result["durable_binding_without_fresh_referent"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "FRESH_CURRENT_RUNTIME_OWNED_REFERENT_PROFILE_WITNESS_REQUIRED",
    }
    assert result["post_restart_native_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT"
    assert result["post_restart_wrong_referent"] == "DEFER_UNKNOWN"
    assert result["identity_scope"] == "OPERATIONAL_EQUIVALENCE_CLASS_ONLY"
    assert result["numerical_identity_authority"] == "NONE"
    assert result["caller_supplied_token_meaning"] == "NO"
    assert result["caller_supplied_referent_class"] == "NO"
    assert result["new_microseed_action_contracts_registered"] == []
    assert result["qualification_ancestry"] == "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY"
    assert result["semantic_authority"] == result["truth_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
    assert "NUMERICAL_OBJECT_IDENTITY" in result["not_earned"]
    assert "TOKEN_MEANING" in result["not_earned"]


def test_c08f_token_surface_permutation_swaps_only_empirical_referent_binding():
    a = run_campaign("R4", "T9")
    b = run_campaign("T9", "R4")
    amap = _mapping(a)
    bmap = _mapping(b)
    assert a["referent_x_signature_sha256"] == b["referent_x_signature_sha256"]
    assert a["referent_y_signature_sha256"] == b["referent_y_signature_sha256"]
    assert amap["R4"] == bmap["T9"] == a["referent_x_signature_sha256"]
    assert amap["T9"] == bmap["R4"] == a["referent_y_signature_sha256"]


def test_c08f_sensor_representation_changes_preserve_native_referent_class_bindings():
    base = run_campaign("R4", "T9")
    permuted = run_campaign("R4", "T9", lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign("R4", "T9", lambda row: tuple(-x for x in row))
    assert base["referent_x_signature_sha256"] == permuted["referent_x_signature_sha256"] == inverted["referent_x_signature_sha256"]
    assert base["referent_y_signature_sha256"] == permuted["referent_y_signature_sha256"] == inverted["referent_y_signature_sha256"]
    assert _mapping(base) == _mapping(permuted) == _mapping(inverted)
    assert base["post_restart_native_resolution"] == permuted["post_restart_native_resolution"] == inverted["post_restart_native_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT"
