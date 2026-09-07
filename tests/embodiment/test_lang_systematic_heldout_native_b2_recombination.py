from scratch.lang_systematic_heldout_native_b2_recombination import run_campaign


def test_owned_b2_operator_recombines_known_current_components_into_heldout_order_without_prior_composition_evidence():
    r=run_campaign('R4','T9')
    assert r['status']=='BOUNDED_SYSTEMATIC_NATIVE_B2_HELDOUT_RECOMBINATION_EARNED'
    assert r['training_compositions']==['XY'] and r['heldout_composition']=='YX'
    assert r['heldout_yx_absent_before_test'] is True
    assert r['heldout_yx_rederived_after_restart'] is True
    assert r['order_sensitive'] is True
    assert r['operator_owner']=='MICROSEED_NATIVE_B2_ORDERED_COMPOSITION'
    assert r['composition_operator']=='ORDERED_EVIDENCE_TUPLE'
    assert r['duplicate_operands']=={'status':'DEFER_UNKNOWN','reason':'INDEPENDENT_NATIVE_REFERENT_OPERANDS_REQUIRED'}
    assert r['unseen_operand']['status']=='DEFER_UNKNOWN'
    assert r['unseen_operand']['reason']=='UNIQUE_CURRENT_NATIVE_TOKEN_REFERENT_ASSOCIATION_REQUIRED'
    assert r['restart_without_current_tokens']=={'status':'DEFER_UNKNOWN','reason':'TWO_CURRENT_RUNTIME_OBSERVED_TOKEN_OPERANDS_REQUIRED'}
    assert r['contradictory_pair_pressure']=={'status':'PAIR_EVIDENCE_HARVESTED_QUALIFICATION_INCOMPLETE','reason':'PAIR_EVIDENCE_NOT_EXACT_BIJECTION'}
    assert r['post_contradiction_composition']['status']=='DEFER_UNKNOWN'
    assert r['caller_supplied_token_operands']==r['caller_supplied_operand_order']=='NO'
    assert r['caller_supplied_association_ids']==r['caller_supplied_output_evidence_id']=='NO'
    assert r['semantic_reference_authority']==r['predicate_authority']==r['grammar_authority']=='NONE'
    assert r['truth_authority']==r['execution_authority']==r['language_authority']=='NONE'
    assert r['generic_unbounded_systematicity']==r['arity_generalization']==r['semantic_compositionality']=='NOT_EARNED'


def test_surface_token_permutation_preserves_grounded_heldout_composition_identity():
    a=run_campaign('R4','T9')
    b=run_campaign('T9','R4')
    assert a['xy_composition_digest_sha256']==b['xy_composition_digest_sha256']
    assert a['heldout_yx_composition_digest_sha256']==b['heldout_yx_composition_digest_sha256']


def test_sensor_representation_transformations_preserve_heldout_composition_identity():
    base=run_campaign('R4','T9')
    permuted=run_campaign('R4','T9',lambda row:(row[2],row[3],row[0],row[1]))
    inverted=run_campaign('R4','T9',lambda row:tuple(-x for x in row))
    assert base['xy_composition_digest_sha256']==permuted['xy_composition_digest_sha256']==inverted['xy_composition_digest_sha256']
    assert base['heldout_yx_composition_digest_sha256']==permuted['heldout_yx_composition_digest_sha256']==inverted['heldout_yx_composition_digest_sha256']
