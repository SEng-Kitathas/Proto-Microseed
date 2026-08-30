from scratch.ms2020_deficit_owned_post_probe_rehearsal_reentry import run_ms2020


def test_ms2020_completed_referent_deficit_reenters_rehearsal_without_caller_binding_or_bucket():
    r = run_ms2020()
    assert r["status"] == "PASS"
    assert r["A_response"]["rehearsal_sequence"] == ["A"]
    assert r["B_response"]["rehearsal_sequence"] == ["B"]
    assert r["A_response"]["caller_supplied_binding_id"] == r["A_response"]["caller_supplied_bucket_id"] == "NO"
    assert r["B_response"]["caller_supplied_binding_id"] == r["B_response"]["caller_supplied_bucket_id"] == "NO"
    assert r["A_response"]["deficit_state"] == r["B_response"]["deficit_state"] == "REVISIT_REQUIRED"
    assert r["new_rehearsal_owner_required"] == r["new_referent_manager_required"] == "NO"


def test_ms2020_rehearsal_reentry_requires_completed_current_exact_raw_context():
    r = run_ms2020()
    assert r["precompletion"]["reason"] == "CURRENT_COMPLETED_REFERENT_DEFICIT_REQUIRED"
    assert r["postcompletion_duplicate"]["reason"] == "EXACT_SINGLE_CURRENT_RESOLVED_REFERENT_ROUTING_CONTEXT_REQUIRED"
