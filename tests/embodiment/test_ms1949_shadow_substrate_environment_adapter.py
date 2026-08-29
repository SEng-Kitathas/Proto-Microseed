from scratch.ms1949_shadow_substrate_adapter import ChargeWorld, ParityWorld, run_world


def test_one_shadow_adapter_shape_drives_distinct_worlds_through_actual_learning_and_zero_row_rehearsal():
    charge = run_world(ChargeWorld())
    parity = run_world(ParityWorld())
    assert charge['adapter_type'] == parity['adapter_type'] == 'ShadowEnvironmentAdapter'
    assert charge['predicted_final_state'] == charge['actual_final_state'] == 'LEVEL-2'
    assert parity['predicted_final_state'] == parity['actual_final_state'] == 'ODD'
    assert charge['predicted_value_effect'] == parity['predicted_value_effect'] == 2.4
    assert charge['commitment_reason'] == parity['commitment_reason'] == 'BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE'
    assert charge['language'] == parity['language'] == 'DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
