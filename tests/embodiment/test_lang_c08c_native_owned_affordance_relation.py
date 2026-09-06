from scratch.lang_c08c_native_owned_affordance_relation import run_campaign


def test_c08c_native_relation_is_derived_from_owned_raw_action_evidence_and_drifts_on_reversal():
    result = run_campaign()
    assert result["status"] == "C08C_NATIVE_B1_C06_RELATION_EVIDENCE_OWNER_EARNED_LIVE_RUNTIME"
    assert result["profile_count"] == 2
    assert len(result["owned_referent_signature_evidence"]) == 2
    assert result["association_currentness_from_owned_relation_evidence"] == "CURRENTNESS_CONFIRMED"
    assert result["empirical_reversal"] == "DRIFT_WITNESS"
    assert result["relation_digest_sha256"] != result["reversed_relation_digest_sha256"]
    assert result["ordered_operational_referent_signatures"] == list(reversed(result["reversed_order"]))
    assert result["new_action_contracts_registered"] == []
    assert result["caller_supplied_referent_groups"] == "NO"
    assert result["caller_supplied_relation_order"] == "NO"
    assert result["caller_supplied_relation_digest"] == "NO"
    assert result["coordinate_arithmetic"] == "NONE"
    assert result["semantic_authority"] == result["truth_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
    assert "POST_RESTART_NATIVE_RELATION_REDERIVATION" in result["not_earned"]


def test_c08c_relation_content_is_invariant_to_channel_permutation_and_sensor_sign_inversion():
    base = run_campaign()
    permuted = run_campaign(lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign(lambda row: tuple(-x for x in row))
    assert base["ordered_operational_referent_signatures"] == permuted["ordered_operational_referent_signatures"]
    assert base["ordered_operational_referent_signatures"] == inverted["ordered_operational_referent_signatures"]
    assert base["relation_digest_sha256"] == permuted["relation_digest_sha256"]
    assert base["relation_digest_sha256"] == inverted["relation_digest_sha256"]
