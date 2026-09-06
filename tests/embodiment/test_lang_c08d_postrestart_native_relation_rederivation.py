from scratch.lang_c08d_postrestart_native_relation_rederivation import run_campaign


def test_c08d_restart_requires_explicit_body_reattachment_and_fresh_owned_relation_evidence():
    result = run_campaign()
    assert result["status"] == "C08D_POST_RESTART_NATIVE_RELATION_REDERIVATION_EARNED"
    assert result["body_capabilities_before_reattach"] == []
    assert result["association_after_restart"] == "REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"
    assert result["historical_relation_witness_after_restart"] == {
        "status": "UNKNOWN_INCOMPLETE",
        "reason": "FRESH_CURRENT_RUNTIME_OWNED_RELATION_WITNESS_REQUIRED",
    }
    assert result["reattached_without_fresh_evidence"]["status"] == "DEFER_UNKNOWN"
    assert result["durable_history_reauthorized_body"] == "NO"
    assert result["body_reattachment"] == "EXPLICIT_SUPPLIED_LOW_LEVEL_BODY_INTERFACE"
    assert result["fresh_post_restart_organism_owned_evidence_required"] == "YES"
    assert result["relation_digest_stable_across_restart"] is True
    assert result["relation_digest_before_restart"] == result["relation_digest_after_fresh_restart_evidence"]
    assert result["fresh_relation_runtime_boot_seq"] == result["second_runtime_boot_seq"]
    assert result["second_runtime_boot_seq"] > result["first_runtime_boot_seq"]
    assert result["post_restart_revalidation"] == "CURRENTNESS_CONFIRMED"
    assert result["empirical_reversal"] == "DRIFT_WITNESS"
    assert result["reversed_relation_digest_sha256"] != result["relation_digest_before_restart"]
    assert result["caller_supplied_referent_groups"] == "NO"
    assert result["caller_supplied_relation_order"] == "NO"
    assert result["caller_supplied_relation_digest"] == "NO"
    assert result["coordinate_arithmetic"] == "NONE"
    assert result["semantic_authority"] == result["truth_authority"] == "NONE"
    assert result["execution_authority_from_history"] == result["language_authority"] == "NONE"
    assert "C07_TOKEN_BINDING_REEMBODIMENT" in result["not_earned"]


def test_c08d_postrestart_relation_identity_survives_representation_permutation_and_sign_inversion():
    base = run_campaign()
    permuted = run_campaign(lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign(lambda row: tuple(-x for x in row))
    expected = base["relation_digest_before_restart"]
    assert expected == permuted["relation_digest_before_restart"] == inverted["relation_digest_before_restart"]
    assert expected == base["relation_digest_after_fresh_restart_evidence"]
    assert expected == permuted["relation_digest_after_fresh_restart_evidence"]
    assert expected == inverted["relation_digest_after_fresh_restart_evidence"]
    assert base["post_restart_revalidation"] == permuted["post_restart_revalidation"] == inverted["post_restart_revalidation"] == "CURRENTNESS_CONFIRMED"
