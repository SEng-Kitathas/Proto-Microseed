from scratch.ms2017_effect_time_owned_observable_contrast_reauthorization import run_ms2017


def test_ms2017_effect_time_rederives_owned_contrast_and_ignores_forged_caller_context():
    r = run_ms2017()
    assert r["status"] == "PASS"
    assert r["success"]["execution_status"] == "ACTION_EXECUTED"
    assert r["success"]["calls"] == ["P2"]
    assert r["success"]["forged_caller_context_ignored"] == "YES"
    assert r["execution_path"] == "ORDINARY_EXECUTE_BOUNDED_ACTION"
    assert r["new_executor_required"] == "NO"


def test_ms2017_owned_prefix_ambiguity_after_nomination_blocks_before_effect():
    r = run_ms2017()
    assert r["duplicate_raw"]["status"] == "PASS"
    assert r["duplicate_raw"]["reason"] == "CURRENT_OWNED_REFERENT_DECISION_SURFACE_REQUIRED_AT_EXECUTION"
    assert r["duplicate_raw"]["calls"] == []
