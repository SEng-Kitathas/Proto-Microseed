from scratch.ms1950_shadow_substrate_restart_reentry import run_restart


def test_persisted_competence_requires_explicit_current_environment_reattachment_after_restart():
    result = run_restart()
    assert result['status'] == 'PASS'
    assert result['automatic_reauthorization'] == 'NO'
    assert result['after_restart_before_adapter']['live_charge_contract'] is False
    assert result['after_restart_before_adapter']['relation_status']['status'] == 'STALE_PREDICTIVE_RELATION'
    assert result['after_restart_before_adapter']['proposal_status']['status'] == 'UNKNOWN_INCOMPLETE'
    assert result['after_adapter_reattach']['live_charge_contract'] is True
    assert result['after_adapter_reattach']['relation_status']['status'] == 'CURRENT_PREDICTIVE_RELATION'
    assert result['after_adapter_reattach']['proposal_status']['status'] == 'CURRENT_REHEARSAL_PROPOSAL'
    assert result['reentry_execution_outcome'] == 'LEVEL-2'
