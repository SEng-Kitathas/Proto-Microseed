from __future__ import annotations

from scratch.ms1988_depth4_recursive_bucket_genericity import run_ms1988


def test_ms1988_same_evaluator_supports_depth4_opaque_composition_without_core_change():
    result=run_ms1988()
    assert result['status']=='PASS'
    assert result['shallow_source_projection_ids']==['P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-F']
    assert result['shallow_E_rejection']=='SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND'
    assert result['shallow_G_candidates']==0
    assert result['deep_source_projection_ids']==['P-MS1988-A','P-MS1988-B','P-MS1988-C','P-MS1988-D','P-MS1988-E','P-MS1988-F']
    assert result['deep_recursive_depth']==2
    assert result['single_source_G_candidates']==0
    assert result['depth4_positions']==[4,5]
    assert result['validation_accuracy']==1.0
    assert result['lift']>=.49
    assert result['external_holdout_count']==64
    assert result['C_source_projection_count']==4
    assert result['E_source_projection_count']==5
    assert result['G_source_projection_count']==6
    assert result['E_change_staled_G'] is True
    assert result['C_change_staled_E'] is True
    assert result['core_mechanism_change']=='NO'
    assert result['new_projection_search_mechanism']=='NO'
    assert result['new_representation_manager']=='NO'
    assert result['semantic_recursion_authority']==result['semantic_symbol_authority']==result['truth_authority']==result['language_authority']=='NONE'
