from scratch.lang_systematic_recombination_owner_gap_audit import run_audit


def test_c08g_rule_exists_only_in_research_helper_not_microseed_owner():
    r=run_audit()
    assert r['status']=='CURRENT_BOUNDED_COMPOSITION_OWNERS_PRESENT'
    assert r['c08g_order_sensitive'] is True
    assert r['production_owned_composition_methods']==[
        'def derive_and_record_current_native_b2_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_b3_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
        'def derive_and_record_current_native_bounded_ordered_composition(',
        'def derive_and_record_current_native_recursive_b2_ordered_composition(',
    ]
    assert r['historically_localized_missing_mechanism']=='MICROSEED_OWNED_BOUNDED_ORDERED_COMPOSITION_OPERATOR'
    assert r['binding_now_embodied']=='YES_BOUNDED_B2_PLUS_DIRECT_B3_PLUS_BOUNDED_ARITY_2_TO_4_PLUS_FIXED_DEPTH_ONE_RECURSIVE'
    assert r['bounded_generalized_arity']=='2_TO_4_ONLY'
    assert r['direct_b3_arity']=='3_ONLY'
    assert r['recursive_depth']=='1_ONLY'
    assert r['generic_unbounded_systematicity']=='NOT_EARNED'
    assert r['new_planner_required']=='NO'
    assert r['grammar_authority']==r['semantic_authority']==r['truth_authority']==r['execution_authority']=='NONE'
