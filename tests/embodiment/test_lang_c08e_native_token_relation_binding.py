from scratch.lang_c08e_native_token_relation_binding import run_campaign


def _mapping(result):
    return {item["opaque_token"]: item["relation_digest_sha256"] for item in result["bindings"]}


def test_c08e_reembodies_c07_binding_on_restart_safe_native_relation_evidence_without_microseed_delta():
    result = run_campaign("K7", "M2")
    assert result["status"] == "C08E_NATIVE_C07_TOKEN_BINDING_REEMBODIED_ON_POSTRESTART_NATIVE_RELATION"
    assert result["microseed_delta_required"] == []
    assert result["new_microseed_action_contracts_registered"] == []
    assert result["token_a_resolution"] == result["token_b_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION"
    assert result["unseen_token"] == "DEFER_UNKNOWN"
    assert result["wrong_relation"] == "DEFER_UNKNOWN"
    assert result["holdout_reversal"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "HOLDOUT_TOKEN_NATIVE_RELATION_ASSOCIATION_DISAGREES",
    }
    assert result["ambiguous_holdout"] == "DEFER_UNKNOWN"
    assert set(result["association_states_after_restart"].values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
    assert result["durable_binding_without_fresh_relation"] == {
        "status": "DEFER_UNKNOWN",
        "reason": "FRESH_CURRENT_RUNTIME_OWNED_RELATION_WITNESS_REQUIRED",
    }
    assert result["post_restart_native_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION"
    assert result["post_restart_wrong_relation"] == "DEFER_UNKNOWN"
    assert result["caller_supplied_token_meaning"] == "NO"
    assert result["caller_supplied_relation_order"] == "NO"
    assert result["caller_supplied_relation_digest"] == "NO"
    assert result["pairing_basis"] == "CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY"
    assert result["qualification_ancestry"] == "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY"
    assert result["truth_authority"] == result["semantic_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
    assert "ENDOGENOUS_QUALIFICATION" in result["not_earned"]
    assert "TOKEN_MEANING" in result["not_earned"]


def test_c08e_opaque_token_surface_permutation_swaps_only_empirical_binding_not_relation_identity():
    a = run_campaign("K7", "M2")
    b = run_campaign("M2", "K7")
    amap = _mapping(a)
    bmap = _mapping(b)
    assert a["normal_relation_digest_sha256"] == b["normal_relation_digest_sha256"]
    assert a["reverse_relation_digest_sha256"] == b["reverse_relation_digest_sha256"]
    assert amap["K7"] == bmap["M2"] == a["normal_relation_digest_sha256"]
    assert amap["M2"] == bmap["K7"] == a["reverse_relation_digest_sha256"]


def test_c08e_native_token_binding_survives_sensor_channel_permutation_and_sign_inversion():
    base = run_campaign("K7", "M2")
    permuted = run_campaign("K7", "M2", lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign("K7", "M2", lambda row: tuple(-x for x in row))
    assert base["normal_relation_digest_sha256"] == permuted["normal_relation_digest_sha256"] == inverted["normal_relation_digest_sha256"]
    assert base["reverse_relation_digest_sha256"] == permuted["reverse_relation_digest_sha256"] == inverted["reverse_relation_digest_sha256"]
    assert _mapping(base) == _mapping(permuted) == _mapping(inverted)
    assert base["post_restart_native_resolution"] == permuted["post_restart_native_resolution"] == inverted["post_restart_native_resolution"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION"
