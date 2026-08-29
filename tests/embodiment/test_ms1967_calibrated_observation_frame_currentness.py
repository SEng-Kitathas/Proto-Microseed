from scratch.ms1967_calibrated_observation_frame_currentness import run_ms1967


def test_existing_operational_frame_currentness_owns_bounded_calibration_lifecycle():
    result = run_ms1967()
    assert result['status'] == 'PASS'
    assert result['low_frame']['observed_bound'] == 3.0
    assert result['low_result']['status'] == 'REFERENT_PARTITION_NOMINATED'
    assert result['low_result']['groups'] == ((0, 1), (2, 3))
    stale = result['post_drift_old_frame']
    assert stale['result']['status'] == 'UNKNOWN_INCOMPLETE'
    assert stale['result']['reason'] == 'CALIBRATION_FRAME_NOT_CURRENT_FOR_SENSOR_REGIME'
    assert stale['qualification'] == 'STALE'
    assert stale['currentness'] == 'STALE'
    assert stale['epoch_now'] == 1
    assert result['fresh_high_frame']['observed_bound'] == 15.0
    assert result['fresh_high_result']['frame_current'] is True
    assert result['fresh_high_result']['groups'] == ((0,), (1,), (2, 3))
    assert result['requalification_form'] == 'NEW_CONTENT_BOUND_FRAME_ARTIFACT_NOT_IN_PLACE_RESURRECTION'
    assert result['noise_model_authority'] == 'NONE'
    assert result['future_noise_bound_authority'] == 'NONE'
    assert result['identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
