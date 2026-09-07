from scratch.lang_distinct_leaf_b3_owner_gap_audit import run_audit


def test_grouped_recursive_b2_does_not_count_as_direct_three_distinct_leaf_arity():
    r=run_audit()
    assert r['status']=='CURRENT_DISTINCT_LEAF_B3_OWNER_PRESENT'
    assert r['existing_grouped_recursive_status']=='BOUNDED_ONE_EDGE_RECURSIVE_B2_COMPOSITION_AS_OPERAND_EARNED'
    assert r['existing_grouped_recursive_depth']==1
    assert r['existing_grouped_recursive_b3_claim']=='NOT_EARNED'
    assert '"arity":3' in r['direct_b3_source_markers']
    assert r['historically_localized_missing_mechanism']=='THREE_DISTINCT_CURRENT_GROUNDED_LEAF_OPERAND_CARRIER_AND_ORDERED_B3_OPERATOR'
    assert r['b3_owner_now_embodied']=='YES_HARD_BOUNDED_ARITY_3_ONLY'
    assert r['grouped_recursive_parent_counts_as_b3']=='NO'
    assert r['flattening_authority']==r['associativity_authority']=='NONE'
    assert r['generic_nary_systematicity']=='NOT_EARNED'
    assert r['semantic_authority']==r['grammar_authority']==r['truth_authority']==r['execution_authority']=='NONE'
