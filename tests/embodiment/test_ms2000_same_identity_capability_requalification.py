from scratch.ms2000_same_identity_capability_requalification import run_ms2000


def test_ms2000_same_identity_capability_requalification():
    result = run_ms2000()
    assert result["status"] == "PASS"
    assert result["same_identity_signatures_preserved"] is True
    assert result["ticket_authority_field"] == "ABSENT"
    assert result["dependent_auto_reactivation"] == "NONE"
    assert result["new_manager_required"] == "NO"
    assert result["self_qualification_authority"] == "NONE"
    assert result["final_invoke"]["status"] == "CAPABILITY_RESULT"
    assert result["forged_signature"] == "REQUALIFICATION_CONTRACT_SIGNATURE_MISMATCH"
    assert result["stale_epoch_replay"] == "REQUALIFICATION_STALE_EPOCH_MISMATCH"
    assert result["negative_evidence"] == "REQUALIFICATION_NOT_ADMISSIBLE:REJECTED"
    assert all("CAPABILITY_REACTIVATION_DEPENDENCY_NOT_CURRENT" in x for x in result["cycle_errors"])
