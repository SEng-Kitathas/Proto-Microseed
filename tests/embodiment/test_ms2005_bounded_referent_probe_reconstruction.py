from scratch.ms2005_bounded_referent_probe_reconstruction import run_ms2005, run_ms2005_unique_probe


def test_ms2005_existing_persisted_signature_classes_reconstruct_historical_class_sets_after_restart():
    r=run_ms2005()
    assert r["status"]=="PASS"
    assert r["restart_reconstruction"]=="PASS"
    assert r["new_durable_bucket_class_map_required"]=="NO"
    assert r["identity_authority"]==r["semantic_reference_authority"]=="NONE"


def test_ms2005_probe_informativeness_uses_opaque_response_multisets_and_preserves_ambiguity():
    r=run_ms2005()
    assert r["probe_status"]=="CURRENT_REFERENT_PROBE_AMBIGUOUS"
    assert r["informative_probe_ids"]==["P2","P4"]
    assert r["false_information_from_class_labels_rejected"]=="YES__RESPONSE_MULTISET_ONLY"
    assert r["selection_authority"]==r["execution_authority"]==r["truth_authority"]=="NONE"
    assert r["new_probe_selector_required"]=="NO"


def test_ms2005_order_independent_raw_world_derives_one_unique_informative_probe_without_schedule():
    r=run_ms2005_unique_probe()
    assert r["status"]=="PASS"
    assert r["probe_status"]=="CURRENT_UNIQUE_INFORMATIVE_REFERENT_PROBE"
    assert r["probe_action_id"]=="P2"
    assert r["informative_probe_ids"]==["P2"]
    assert r["caller_supplied_probe_schedule"]=="NO"
    assert r["probe_selection_authority"]==r["execution_authority"]=="NONE"
