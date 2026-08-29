from scratch.ms1957_process_liveness_hostile import run_ambiguous_dispatch, run_known_dead_and_reentry


def test_known_dead_process_invalidates_before_effect_and_compatible_reentry_recovers_history():
    result = run_known_dead_and_reentry()
    assert result['status'] == 'PASS'
    assert result['automatic_reauthorization'] == 'NO'
    assert result['dead_endpoint_result']['status'] == 'NO_EXECUTION'
    assert result['dead_endpoint_result']['reason'] == 'EXTERNAL_ENDPOINT_NOT_CURRENT'
    assert result['stale_relation_after_dead_preflight']['status'] == 'STALE_PREDICTIVE_RELATION'
    assert result['stale_proposal_after_dead_preflight']['status'] == 'UNKNOWN_INCOMPLETE'
    assert result['reentry_relation']['status'] == 'CURRENT_PREDICTIVE_RELATION'
    assert result['reentry_proposal']['status'] == 'CURRENT_REHEARSAL_PROPOSAL'
    assert result['reentry_actual_state'] == 'PROC-LEVEL-2'


def test_ambiguous_process_dispatch_stays_unknown_and_records_no_execution_or_outcome():
    result = run_ambiguous_dispatch()
    assert result['status'] == 'PASS'
    execution = result['execution_result']
    assert execution['status'] == 'UNKNOWN_EXECUTION'
    assert execution['reason'] == 'EXTERNAL_ENDPOINT_DISPATCH_AMBIGUOUS'
    assert result['execution_count_unchanged'] is True
    assert result['outcome_count_unchanged'] is True
    assert result['relation_after_ambiguous_dispatch']['status'] == 'STALE_PREDICTIVE_RELATION'
    assert result['proposal_after_ambiguous_dispatch']['status'] == 'UNKNOWN_INCOMPLETE'
