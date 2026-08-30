from scratch.ms2016_owned_observable_contrast_program_information import run_ms2016


def test_ms2016_same_control_state_raw_observable_contrast_can_license_information_without_state_split():
    r = run_ms2016()
    assert r["status"] == "PASS"
    assert r["p2_control_state_predictions"] == ["s0", "s0"]
    assert r["trace_information"]["commitment"] == "NO"
    assert r["trace_information"]["reason"] == "PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE"
    assert r["owned_observable_information"]["commitment"] == "YES"
    assert r["owned_observable_information"]["reason"] == "PROGRAM_CAN_CHANGE_OWNED_OBSERVABLE_CONTRAST"
    assert r["nomination_status"] == "ACTION_INTENT_NOMINATED"
    assert r["nominated_capability_id"] == "P2"
    assert r["handler_calls_at_nomination"] == []
    assert r["representation_owner"] == "EPISTEMIC_CONTRAST_ROW"
    assert r["new_representation_owner_required"] == "NO"
    assert r["new_executor_required"] == "NO"
