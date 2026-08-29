from scratch.ms1976_lag3_owned_history_constructor import run_ms1976


def test_owned_history_bridge_composes_to_lag3_only_when_supplied_ceiling_reaches_lag3():
    result=run_ms1976()
    assert result['status']=='PASS'
    assert result['max_lag_2_candidates']==0
    assert result['atoms']==['L3:P0']
    assert result['lag_depth_used']==3
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['history_window_authority']=='SUPPLIED_BOUNDED_CEILING'
    assert result['semantic_projection_authority']==result['language_authority']=='NONE'
