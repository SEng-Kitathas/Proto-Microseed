from scratch.lang_boundary_consumption_owner_gap_audit import run_audit

def test_current_structural_boundary_witness_has_no_segment_state_consumer_owner():
    r=run_audit()
    assert r['status']=='STOP_STRUCTURAL_BOUNDARY_WITNESS_CONSUMER_OWNER_MISSING'
    assert not any(r['consumer_markers_present'].values())
    assert r['bounded_composition_count_before']==r['bounded_composition_count_after_boundary']==0
    assert r['generic_composition_after_boundary_status']=='DEFER_UNKNOWN'
    assert r['generic_composition_after_boundary_reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM'
    assert r['localized_missing_mechanism']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_TO_RETROSPECTIVE_SEGMENT_COMPOSITION_STATE_OWNER'
    assert r['ledger_rewrite_authority']==r['caller_grouping_authority']==r['effect_authority']=='NONE'
