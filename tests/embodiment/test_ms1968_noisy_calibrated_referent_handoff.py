from scratch.ms1968_noisy_calibrated_referent_handoff import run_ms1968


def test_separately_current_calibrated_frames_bridge_noisy_sensor_handoff_without_shared_frame_identity():
    result = run_ms1968()
    assert result['status'] == 'PASS'
    assert set(result['old']['groups'][i]['signature'] for i in range(2)) == set(result['overlap']['groups'][i]['signature'] for i in range(2)) == set(result['new']['groups'][i]['signature'] for i in range(2))
    assert result['frame_statuses'] == {
        'CAL-OLD': 'STALE',
        'CAL-OVERLAP': 'STALE',
        'CAL-NEW': 'SHADOW_QUALIFIED',
    }
    assert result['continuity_authority'] == 'OPERATIONAL_REFERENT_CONTINUITY_ONLY'
    assert result['frame_identity_authority'] == 'NONE'
    assert result['numerical_identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['language_authority'] == 'NONE'
