from scratch.ms2046_grounded_operational_token_referent_binding_quarry import run_ms2046


def test_ms2046_grounded_use_supports_operational_binding_candidate_without_semantic_reference_authority():
    r = run_ms2046()
    assert r["status"] == "GROUNDED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_EARNED"
    p = r["positive"]
    c = p["candidate"]
    assert c["status"] == "QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE"
    assert p["train_groups"] != p["holdout_groups"]
    assert c["semantic_reference_authority"] == "NONE"
    assert c["token_meaning_authority"] == "NONE"
    assert c["numerical_identity_authority"] == "NONE"
    assert c["truth_authority"] == "NONE"
    assert c["execution_authority"] == "NONE"
    assert c["language_authority"] == "NONE"
    assert r["new_language_or_reference_manager_required"] == "NO"


def test_ms2046_alias_ambiguity_copy_fluency_and_convention_reversal_fail_closed():
    r = run_ms2046()
    assert r["ambiguity"]["ambiguous_signal"]["status"] == "DEFER_UNKNOWN"
    assert r["ambiguity"]["referent_alias"]["status"] == "DEFER_UNKNOWN"
    assert r["copy_and_fluency"]["perfect_copy_generation_changed"] == 1
    assert r["copy_and_fluency"]["operational_binding_survives"] is True
    assert r["copy_and_fluency"]["numerical_identity_authority"] == "NONE"
    assert r["copy_and_fluency"]["readable_ungrounded_token"]["reason"] == "SUFFICIENT_GROUNDED_USE_HISTORY_REQUIRED"
    assert r["convention_reversal"]["candidate"]["reason"] == "HOLDOUT_REFERENT_BINDING_DISAGREES"
    assert r["convention_reversal"]["automatic_new_meaning"] == "NO"


def test_ms2046_binding_candidate_is_currentness_bound_and_language_gate_stays_separate():
    r = run_ms2046()
    assert r["currentness"]["signal_drift"]["status"] == "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE"
    assert r["currentness"]["coordination_drift"]["status"] == "STALE_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE"
    assert r["earned"] == "REPEATED_CURRENT_SIGNAL_USE_PLUS_REFERENT_LOCALIZED_COUNTERPARTY_EFFECT_CAN_SUPPORT_A_QUALIFIED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_WITHOUT_SEMANTIC_REFERENCE_AUTHORITY"
    assert r["gate_law"] == "GROUNDING_CANDIDATE != LANGUAGE_GATE_ADMISSION"
    assert r["semantic_reference_authority"] == "NONE"
    assert r["language_authority"] == "NONE"
