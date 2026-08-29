from scratch.ms1964_noisy_referent_boundary_hostile import run_noisy_hostile
from scratch.ms1965_passive_calibrated_change_frame import run_passive_calibration
from scratch.ms1966_calibration_currentness_hostile import run_calibration_drift


def test_raw_noisy_observation_breaks_exact_boundary_coherence_but_supplied_threshold_recovers_partition():
    result = run_noisy_hostile()
    assert result['status'] == 'BOUNDARY_CONFIRMED'
    assert result['exact_nomination']['status'] == 'UNKNOWN_INCOMPLETE'
    assert result['supplied_threshold_nomination']['status'] == 'REFERENT_PARTITION_NOMINATED'
    assert result['supplied_threshold_nomination']['groups'] == ((0, 1), (2, 3))
    assert result['noise_model_authority'] == 'NONE'


def test_passive_fixed_state_calibration_recovers_bounded_noisy_world_without_claiming_future_bound():
    result = run_passive_calibration()
    assert result['status'] == 'PASS'
    assert result['calibration_authority'] == 'OBSERVED_BASELINE_BOUND_ONLY'
    assert result['future_noise_bound_authority'] == 'NONE'
    assert result['noise_model_authority'] == 'NONE'
    assert all(run['groups'] == ((0, 1), (2, 3)) for run in result['runs'])


def test_old_passive_calibration_becomes_invalid_under_sensor_noise_drift():
    result = run_calibration_drift()
    assert result['status'] == 'BOUNDARY_CONFIRMED'
    assert result['old_observed_baseline_bound'] == 3
    assert result['post_drift_nomination']['groups'] != ((0, 1), (2, 3))
    assert result['missing_owner'] == 'CALIBRATION_OR_OBSERVATION_FRAME_CURRENTNESS_AND_REQUALIFICATION'
    assert result['noise_model_authority'] == 'NONE'
