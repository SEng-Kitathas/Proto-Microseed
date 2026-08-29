from scratch.ms1985_two_learned_bucket_composition_boundary import run_ms1985


def test_two_independently_learned_opaque_buckets_compose_through_existing_projection_search():
    result=run_ms1985()
    assert result['status']=='BOUNDARY_CONFIRMED'
    assert result['source_projection_A_positions']==[0,1]
    assert result['source_projection_B_positions']==[2,3]
    assert result['single_source_bucket_candidates']==0
    assert result['second_stage_positions']==[0,1]
    assert result['second_stage_validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['new_projection_search_mechanism_required']=='NO'
    assert result['missing_owner']=='ENTITY_OWNED_CURRENT_PROJECTION_BUCKET_VECTOR_TO_PROJECTION_SAMPLE'
    assert result['semantic_symbol_authority']==result['semantic_composition_authority']==result['truth_authority']==result['language_authority']=='NONE'
