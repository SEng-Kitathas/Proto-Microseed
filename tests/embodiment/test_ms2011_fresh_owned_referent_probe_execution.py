from scratch.ms2011_fresh_owned_referent_probe_execution import run_ms2011

def test_ms2011_owned_fresh_rederivation_controls_ordinary_p2_execution_not_caller_context():
    r=run_ms2011();assert r["status"]=="PASS"
    assert r["success"]["execution_status"]=="ACTION_EXECUTED" and r["success"]["calls"]==["P2"]
    assert r["success"]["forged_caller_context_ignored"]=="YES" and r["execution_path"]=="ORDINARY_EXECUTE_BOUNDED_ACTION"

def test_ms2011_fresh_raw_pressure_and_source_drift_block_before_effect():
    r=run_ms2011();assert r["duplicate_raw"]["calls"]==[] and r["pressure_drift"]["calls"]==[] and r["source_forgery"]["calls"]==[]
    assert r["source_forgery"]["reason"]=="PROGRAM_RELATION_ANCESTRY_MISMATCH" and r["source_forgery"]["stage"]=="NOMINATION"
