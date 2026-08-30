from scratch.ms2002_persisted_operational_referent_class import run_ms2002


def test_ms2002_persisted_operational_referent_class():
    result = run_ms2002()
    assert result["status"] == "PASS"
    assert result["persistent_vs_perfect_copy_replacement_operationally_indistinguishable"] is True
    assert result["numerical_identity_authority"] == "NONE"
    assert result["semantic_reference_authority"] == "NONE"
    assert result["new_referent_manager_required"] == "NO__EXISTING_EVIDENCE_LEDGER_ONLY"
    assert result["aliased_post"]["status"] == "UNKNOWN_INCOMPLETE"
    assert result["budget_hostile"]["bounded_status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED"
    assert result["budget_hostile"]["complete_status"] == "OPERATIONAL_REFERENT_SIGNATURE_CLASS_REASSOCIATED"
    assert result["persistent_variant"]["post_signatures"] == result["perfect_copy_replacement_variant"]["post_signatures"]
    assert result["persistent_variant"]["post_match_counts"] == result["perfect_copy_replacement_variant"]["post_match_counts"]
