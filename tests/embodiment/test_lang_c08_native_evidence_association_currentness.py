from scratch.lang_c08_native_evidence_association_currentness import run_campaign


def test_c08_native_record_preserves_history_requires_restart_revalidation_and_stales_selectively():
    r=run_campaign()
    assert r["status"]=="STOP_C08_PARTIAL_NATIVE_MECHANISM__FULL_CURRENTNESS_NOT_EARNED"
    assert r["native_record_lifecycle"]=="PASS"
    assert r["selective_drift"]["affected"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"
    assert r["selective_drift"]["unrelated"]=="CURRENT_OPAQUE_EVIDENCE_ASSOCIATION"
    assert r["restart"]["drifted"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"
    assert r["restart"]["nonstale"]=="REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"
    assert r["late_green_does_not_reactivate_stale"]=="STALE_OPAQUE_EVIDENCE_ASSOCIATION"
    assert r["new_action_contracts_registered"]==[]


def test_c08_refuses_to_call_externally_authored_currentness_digest_organism_owned_currentness():
    r=run_campaign()
    assert r["localized_missing_mechanism"]=="NATIVE_C06_B1_RELATION_CURRENTNESS_EVIDENCE_OWNER"
    assert "EXTERNAL_RESEARCH_HARNESS" in r["reason_full_c08_not_earned"]
    assert "ORGANISM_OWNED_C06_RELATION_CURRENTNESS" in r["not_earned"]
    assert "GENERIC_CAPABILITY" in r["not_earned"]
