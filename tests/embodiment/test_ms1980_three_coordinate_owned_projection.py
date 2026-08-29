from scratch.ms1980_three_coordinate_owned_projection import run_ms1980


def test_owned_raw_projection_support_grows_to_three_coordinates_only_when_lower_arity_is_insufficient():
    result=run_ms1980()
    assert result['status']=='PASS'
    assert result['owned_sample_count']==64
    assert result['max_subset_2_candidates']==0
    assert result['input_positions']==[0,1,2]
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['new_projection_search_mechanism_added']=='NO'
    assert result['support_ceiling_authority']=='SUPPLIED_BOUNDED_SEARCH_GRAMMAR'
    assert result['semantic_coordinate_authority']==result['semantic_projection_authority']==result['truth_authority']==result['language_authority']=='NONE'
