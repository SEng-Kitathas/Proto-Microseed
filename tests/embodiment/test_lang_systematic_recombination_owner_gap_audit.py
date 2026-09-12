from scratch.lang_systematic_recombination_owner_gap_audit import run_audit


def test_current_composition_owner_inventory_remains_explicit_and_bounded():
    r=run_audit()
    assert r['status']=='CURRENT_BOUNDED_COMPOSITION_OWNERS_PRESENT'
    assert r['c08g_order_sensitive'] is True
    assert r['production_owned_composition_methods']==[
        'def derive_and_record_current_native_b2_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_b3_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_bounded_ordered_composition(',
        'def _native_structural_segment_state_content_from_boundary(',
        'def _validate_current_native_structural_segment_state(',
        'def derive_and_record_current_native_structural_segment_state(',
        'def _native_structural_segment_b2_child_carriers(',
        'def _validate_current_native_structural_segment_b2_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_b2_recursive_composition(',
        'def _native_structural_segment_bounded_child_carriers(',
        'def _validate_current_native_structural_segment_bounded_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_bounded_recursive_composition(',
        'def _native_depth_one_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_two_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_two_recursive_composition(',
        'def _native_depth_two_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_three_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_three_recursive_composition(',
        'def _native_depth_three_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_four_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_four_recursive_composition(',
        'def _native_depth_four_structural_segment_parent_child_carrier(',
        'def _validate_current_native_structural_segment_depth_five_recursive_composition_state(',
        'def derive_and_record_current_native_structural_segment_depth_five_recursive_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_recursive_b2_ordered_composition(',
    ]
    assert r['historically_localized_missing_mechanism']=='MICROSEED_OWNED_BOUNDED_ORDERED_COMPOSITION_OPERATOR'
    assert r['binding_now_embodied']=='YES_BOUNDED_B2_PLUS_DIRECT_B3_PLUS_BOUNDED_ARITY_2_TO_4_PLUS_FIXED_DEPTH_ONE_SEGMENT_REUSE_PLUS_ONE_EXPLICIT_DEPTH_TWO_EDGE_PLUS_ONE_EXPLICIT_MIXED_DEPTH_THREE_EDGE_PLUS_ONE_EXPLICIT_MIXED_DEPTH_FOUR_EDGE_PLUS_ONE_EXPLICIT_MIXED_DEPTH_FIVE_EDGE'
    assert r['structural_segment_operand_scope']=='BOUNDED_DEPTH_ONE_TO_DEPTH_TWO_PLUS_MIXED_DEPTH_THREE_PLUS_MIXED_DEPTH_FOUR_PLUS_MIXED_DEPTH_FIVE_WITH_FULL_ANCESTRY_EXCLUSION'
    assert r['generic_unbounded_structural_segment_operand']=='NOT_EARNED'
    assert r['bounded_generalized_arity']=='2_TO_4_ONLY'
    assert r['direct_b3_arity']=='3_ONLY'
    assert r['recursive_depth']=='5_FIXED_MIXED_EDGE_ONLY'
    assert r['generic_unbounded_systematicity']=='NOT_EARNED'
    assert r['generic_recursive_closure']=='NOT_EARNED'
    assert r['depth_three_reuse']=='ONE_EXPLICIT_MIXED_DEPTH_EDGE_ONLY'
    assert r['depth_four_reuse']=='ONE_EXPLICIT_MIXED_DEPTH_EDGE_ONLY'
    assert r['depth_five_reuse']=='ONE_EXPLICIT_MIXED_DEPTH_EDGE_ONLY'
    assert r['new_planner_required']=='NO'
    assert r['grammar_authority']==r['semantic_authority']==r['truth_authority']==r['execution_authority']=='NONE'
