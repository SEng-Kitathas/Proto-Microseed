from scratch.lang_distinct_leaf_b3_ordered_composition import run_campaign


def test_three_distinct_current_grounded_leaves_form_direct_ordered_b3_without_caller_operands():
    r=run_campaign(('R4','T9','W3'))
    assert r['status']=='BOUNDED_DISTINCT_LEAF_B3_ORDERED_COMPOSITION_EARNED'
    assert r['arity']==3
    assert r['operator_owner']=='MICROSEED_NATIVE_B3_ORDERED_COMPOSITION'
    assert r['composition_operator']=='ORDERED_EVIDENCE_TUPLE'
    assert r['xzy_absent_before_test'] is True
    assert r['order_sensitive'] is True
    assert r['restart_rederived_xyz'] is True
    assert r['duplicate_operands']=={'status':'DEFER_UNKNOWN','reason':'THREE_DISTINCT_NATIVE_REFERENT_OPERANDS_REQUIRED'}
    assert r['unseen_operand']['status']=='DEFER_UNKNOWN'
    assert r['unseen_operand']['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED'
    assert r['qz_drift']=={'status':'DEFER_UNKNOWN','reason':'CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED'}
    assert r['frame_drift']=={'status':'DEFER_UNKNOWN','reason':'CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED'}
    assert r['restart_without_fresh_tokens']=={'status':'DEFER_UNKNOWN','reason':'THREE_CURRENT_RUNTIME_OBSERVED_TOKEN_OPERANDS_REQUIRED'}
    assert r['caller_supplied_token_operands']==r['caller_supplied_operand_order']=='NO'
    assert r['caller_supplied_association_ids']==r['caller_supplied_referent_identity']=='NO'
    assert r['caller_supplied_grouping']==r['caller_supplied_output_evidence_id']=='NO'
    assert r['flattening_authority']==r['associativity_authority']=='NONE'
    assert r['semantic_composition_authority']==r['grammar_authority']=='NONE'
    assert r['truth_authority']==r['execution_authority']==r['language_authority']=='NONE'
    assert r['generic_nary_arity_generalization']==r['b4_arity']=='NOT_EARNED'


def test_surface_token_permutation_preserves_grounded_b3_content_identity():
    a=run_campaign(('R4','T9','W3'))
    b=run_campaign(('W3','R4','T9'))
    assert a['xyz_digest_sha256']==b['xyz_digest_sha256']
    assert a['xzy_digest_sha256']==b['xzy_digest_sha256']


def test_six_channel_representation_transforms_preserve_grounded_b3_identity():
    base=run_campaign(('R4','T9','W3'))
    perm=run_campaign(('R4','T9','W3'),lambda row:(row[4],row[5],row[0],row[1],row[2],row[3]))
    inv=run_campaign(('R4','T9','W3'),lambda row:tuple(-x for x in row))
    assert base['xyz_digest_sha256']==perm['xyz_digest_sha256']==inv['xyz_digest_sha256']
    assert base['xzy_digest_sha256']==perm['xzy_digest_sha256']==inv['xzy_digest_sha256']
