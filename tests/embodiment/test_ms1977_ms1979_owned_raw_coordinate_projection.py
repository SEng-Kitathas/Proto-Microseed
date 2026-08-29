from scratch.ms1977_raw_coordinate_projection_boundary import run_ms1977
from scratch.ms1978_owned_raw_coordinate_projection import run_ms1978
from scratch.ms1979_raw_observation_receipt_currentness import run_ms1979


def test_supplied_raw_coordinates_localize_missing_owned_raw_ingress_not_projection_search():
    result=run_ms1977()
    assert result['status']=='BOUNDARY_CONFIRMED'
    assert result['single_coordinate_candidates']==0
    assert result['input_positions']==[0,1]
    assert result['validation_accuracy']==1.0
    assert result['ordinary_outcome_evidence_preserves_raw_tokens']=='NO'
    assert result['missing_owner']=='BOUNDED_DURABLE_OWNED_RAW_OBSERVATION_COORDINATE_INGRESS'
    assert result['raw_coordinate_authority']=='HARNESS_SUPPLIED_ASSISTANCE'


def test_owned_raw_receipts_feed_existing_projection_search_without_semantic_authority():
    result=run_ms1978()
    assert result['status']=='PASS'
    assert result['owned_sample_count']==48
    assert result['history_basis']=='AUTHENTICATED_RAW_OBSERVATION_PLUS_ACTION_OUTCOME_JOIN'
    assert result['single_coordinate_candidates']==0
    assert result['input_positions']==[0,1]
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['new_projection_search_mechanism_added']=='NO'
    assert result['raw_coordinate_semantic_authority']==result['semantic_projection_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_raw_receipts_are_bounded_current_evidence_and_do_not_gain_duplicate_or_restart_authority():
    result=run_ms1979()
    assert result['status']=='PASS'
    assert result['cases']['coordinate_limit']['evidence_persisted'] is False
    assert result['cases']['duplicate_receipt']['sample_count']==0
    assert any(reason=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CONTROL_STATE_REQUIRED' for _,reason in result['cases']['duplicate_receipt']['sample_rejections'])
    assert result['cases']['frame_drift']['before_samples']==1
    assert result['cases']['frame_drift']['after_samples']==0
    assert result['cases']['restart_no_attach']['sample_count']==0
    assert result['cases']['compatible_reattachment']['sample_count']==1
    assert result['automatic_duplicate_arbitration']=='NO'
    assert result['automatic_restart_authority']=='NO'
    assert result['semantic_coordinate_authority']==result['truth_authority']==result['language_authority']=='NONE'
