from scratch.lang_recursive_b2_composition_as_operand import run_campaign


def test_two_current_b2_children_become_one_fixed_depth_recursive_parent_without_caller_grouping():
    r=run_campaign('R4','T9')
    assert r['status']=='BOUNDED_ONE_EDGE_RECURSIVE_B2_COMPOSITION_AS_OPERAND_EARNED'
    assert r['composition_depth']==1
    assert r['operator_owner']=='MICROSEED_NATIVE_RECURSIVE_B2_COMPOSITION'
    assert r['composition_operator']=='RECURSIVE_ORDERED_EVIDENCE_TUPLE'
    assert r['one_child_status']=={'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'}
    assert r['duplicate_same_content_child_status']=={'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'}
    assert r['forged_child_status']=={'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'}
    assert r['post_child_drift_status']=={'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'}
    assert r['restart_without_fresh_children']=={'status':'DEFER_UNKNOWN','reason':'TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'}
    assert r['order_sensitive'] is True
    assert r['restart_rederived_same_parent'] is True
    assert r['caller_supplied_child_ids']==r['caller_supplied_child_order']=='NO'
    assert r['caller_supplied_grouping']==r['caller_supplied_leaf_operands']=='NO'
    assert r['flattening_authority']==r['associativity_authority']=='NONE'
    assert r['semantic_composition_authority']==r['grammar_authority']=='NONE'
    assert r['truth_authority']==r['execution_authority']==r['language_authority']=='NONE'
    assert r['distinct_leaf_b3_arity_generalization']==r['generic_recursive_depth']==r['unbounded_systematicity']=='NOT_EARNED'


def test_surface_token_permutation_preserves_recursive_grounded_parent_identity():
    a=run_campaign('R4','T9')
    b=run_campaign('T9','R4')
    assert a['parent_xy_yx_digest_sha256']==b['parent_xy_yx_digest_sha256']
    assert a['reverse_yx_xy_digest_sha256']==b['reverse_yx_xy_digest_sha256']


def test_sensor_transformations_preserve_recursive_grounded_parent_identity():
    base=run_campaign('R4','T9')
    perm=run_campaign('R4','T9',lambda row:(row[2],row[3],row[0],row[1]))
    inv=run_campaign('R4','T9',lambda row:tuple(-x for x in row))
    assert base['parent_xy_yx_digest_sha256']==perm['parent_xy_yx_digest_sha256']==inv['parent_xy_yx_digest_sha256']
    assert base['reverse_yx_xy_digest_sha256']==perm['reverse_yx_xy_digest_sha256']==inv['reverse_yx_xy_digest_sha256']
