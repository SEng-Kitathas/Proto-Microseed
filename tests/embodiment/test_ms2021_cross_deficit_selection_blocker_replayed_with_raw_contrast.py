from scratch.ms2021_cross_deficit_selection_blocker_replayed_with_raw_contrast import run_ms2021


def test_ms2021_two_raw_contrast_opportunities_are_individually_licensed_but_cross_deficit_choice_unowned():
    r = run_ms2021()
    assert r["status"] == "BLOCKED_AS_DESIGNED"
    assert r["multiple_status"] == "MULTIPLE_CURRENT_OWNED_REFERENT_EPISTEMIC_OPPORTUNITIES"
    assert r["reason"] == "NO_CROSS_DEFICIT_SELECTION_AUTHORITY"
    assert set(r["probe_action_ids"]) == {"P2", "P4"}
    assert r["selection_authority"] == r["execution_authority"] == "NONE"
    assert r["handler_calls"] == []
    assert r["trace_leakage_required"] == "NO"
    assert r["existing_selection_owner"] == "NONE_FOUND"
    assert len(r["opportunities"]) == 2
    for op in r["opportunities"]:
        assert len(set(op["probe_control_state_predictions"])) == 1
        assert op["trace_information"]["commitment"] == "NO"
        assert op["trace_information"]["reason"] == "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
        assert op["contrast_information"]["commitment"] == "YES"
        assert op["contrast_information"]["reason"] == "PROGRAM_CAN_CHANGE_OWNED_OBSERVABLE_CONTRAST"
        assert op["step_commitment"]["commitment"] == "YES"
        assert op["step_commitment"]["reason"] == "EPISTEMIC_PROGRAM_STEP_ALL_LICENSED"
