from scratch.lang_c08b_owned_relation_evidence_owner_boundary import run_boundary


def test_existing_c01_c06_language_lineage_does_not_own_relation_currentness_evidence():
    result = run_boundary()
    assert result["status"] == "STOP_C08B_EXISTING_LANGUAGE_LINEAGE_HAS_NO_ORGANISM_OWNED_C06_RELATION_EVIDENCE"
    assert result["evidence_count_before_c06_episode"] == 0
    assert result["evidence_count_after_c06_episode"] == 0
    assert result["evidence_delta"] == 0
    assert result["native_relation_evidence_rows"] == []
    assert result["missing_native_b1_ancestry_fields"] == [
        "action_response_rows",
        "raw_evidence_refs",
        "source_evidence_refs",
    ]
    assert all(result["later_native_surfaces_already_present"].values())
    assert result["missing_owner"] == "C01_C06_LANGUAGE_LINEAGE_BRIDGE_TO_EXISTING_OWNED_RAW_ACTION_REFERENT_EVIDENCE"
    assert result["truth_authority"] == result["semantic_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
