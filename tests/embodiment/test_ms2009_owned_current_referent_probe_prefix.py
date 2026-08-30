from scratch.ms2009_owned_current_referent_probe_prefix import run_ms2009

def test_ms2009_owned_action_raw_ancestry_reconstructs_current_probe_prefix_across_restart():
    r=run_ms2009(); assert r["status"]=="PASS"
    assert r["opaque_action_sequence"]==["P0","P1"]
    assert len(r["raw_samples"])==3 and r["restart_reconstruction"]=="PASS"
    assert r["caller_supplied_raw_trace"]==r["caller_supplied_action_sequence"]=="NO"

def test_ms2009_duplicate_raw_receipt_and_frame_drift_fail_closed():
    r=run_ms2009(); assert r["duplicate_receipt"]=="DEFER_UNKNOWN" and r["frame_drift"]=="DEFER_UNKNOWN"
    assert r["truth_authority"]==r["selection_authority"]==r["execution_authority"]=="NONE"
