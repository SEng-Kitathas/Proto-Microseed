from scratch.ms2019_raw_referent_resolution_changes_downstream_action import run_ms2019


def test_ms2019_same_state_raw_response_selects_and_executes_different_downstream_action():
    r = run_ms2019()
    assert r["status"] == "PASS"
    assert r["same_control_state_probe"] == "YES__S0_TO_S0"
    assert r["raw_response_changes_downstream_action"] == "YES"
    assert r["A_response"]["rehearsal_sequence"] == ["A"]
    assert r["B_response"]["rehearsal_sequence"] == ["B"]
    assert r["A_response"]["calls"] == ["P2", "A"]
    assert r["B_response"]["calls"] == ["P2", "B"]
    assert r["A_response"]["downstream_execution_status"] == "ACTION_EXECUTED"
    assert r["B_response"]["downstream_execution_status"] == "ACTION_EXECUTED"
    assert r["A_response"]["resolved_bucket_id"] != r["B_response"]["resolved_bucket_id"]
    assert r["new_policy_owner_required"] == r["new_executor_required"] == "NO"
