from scratch.ms1953_delayed_outcome_settlement_hostile import run_hostile, run_delayed_reality


def test_delayed_world_uses_settled_outcome_for_action_closure_without_erasing_immediate_pending_state():
    boundary = run_hostile()
    assert boundary['status'] == 'PASS'
    assert boundary['immediate_world_observation']['next_state_id'] == 'PENDING'
    assert boundary['immediate_world_observation']['observed_value'] == 0.0
    assert boundary['settled_world_observation']['next_state_id'] == 'LEVEL-2'
    assert boundary['settled_world_observation']['observed_value'] == 2.4
    assert boundary['adapter_seed_state'] == 'LEVEL-2'
    assert boundary['adapter_seed_effect'] == 2.4
    assert boundary['commitment']['commitment'] == 'YES'


def test_delayed_world_actual_history_qualification_and_zero_row_reuse_use_settled_outcome():
    result = run_delayed_reality()
    assert result['status'] == 'PASS'
    assert result['predicted_final_state'] == result['actual_final_state'] == 'LEVEL-2'
    assert result['predicted_value_effect'] == result['actual_observed_value'] == 2.4
    assert result['commitment_reason'] == 'BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE'
