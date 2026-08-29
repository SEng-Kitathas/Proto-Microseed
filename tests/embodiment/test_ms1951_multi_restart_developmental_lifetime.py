from scratch.ms1951_shadow_substrate_multi_restart_lifetime import run_lifetime


def test_repeated_restart_sessions_extend_history_without_automatic_reauthorization():
    result = run_lifetime(sessions=3, executions_per_session=3)
    assert result['status'] == 'PASS'
    assert result['automatic_reauthorization'] == 'NO'
    assert result['baseline_outcomes'] == 12
    assert result['final_outcomes'] == 21
    assert [s['outcome_count'] for s in result['sessions']] == [15, 18, 21]
    assert all(s['pre_relation'] == 'STALE_PREDICTIVE_RELATION' for s in result['sessions'])
    assert all(s['pre_proposal'] == 'UNKNOWN_INCOMPLETE' for s in result['sessions'])
    assert all(s['post_relation'] == 'CURRENT_PREDICTIVE_RELATION' for s in result['sessions'])
    assert all(s['post_proposal'] == 'CURRENT_REHEARSAL_PROPOSAL' for s in result['sessions'])
