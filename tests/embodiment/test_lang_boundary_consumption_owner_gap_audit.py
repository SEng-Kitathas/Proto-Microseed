from scratch.lang_boundary_consumption_owner_gap_audit import run_audit

def test_historical_structural_boundary_consumer_gap_is_now_embodied_but_negative_commit_remains_recovery_anchor():
    r=run_audit()
    assert r['status']=='CURRENT_STRUCTURAL_BOUNDARY_CONSUMER_OWNER_PRESENT'
    assert r['historical_negative_commit']=='d0e2438f968cf0c0525cbb01f352fad05a8a4b2d'
    assert r['consumer_markers_present']['OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE'] is True
    assert r['consumer_markers_present']['derive_and_record_current_native_segmented'] is False
    assert r['current_consumer_method']=='derive_and_record_current_native_structural_segment_state'
    assert r['bounded_composition_count_before']==r['bounded_composition_count_after_boundary']==0
    assert r['generic_composition_after_boundary_status']=='DEFER_UNKNOWN'
    assert r['generic_composition_after_boundary_reason']=='ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT'
    assert r['historical_localized_missing_mechanism']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_TO_RETROSPECTIVE_SEGMENT_COMPOSITION_STATE_OWNER'
    assert r['ledger_rewrite_authority']==r['caller_grouping_authority']==r['effect_authority']=='NONE'
