from scratch.ms1956_process_isolated_environment import run_process_world


def test_shadow_substrate_operates_across_serialized_process_boundary():
    result = run_process_world()
    assert result['status'] == 'PASS'
    assert result['shared_python_object_state'] == 'NO'
    assert result['predicted_final_state'] == result['actual_final_state'] == 'PROC-LEVEL-2'
    assert result['distinct_qualification_processes'] == 16
    assert result['qualification_sample_pids']
    assert all(pid != result['live_world_pid'] for pid in result['qualification_sample_pids'])
