from scratch.ms2007_partial_referent_ambiguity_from_owned_history import run_ms2007

def test_ms2007_partial_current_trace_derives_live_ambiguity_without_supplied_bucket_pair():
    r=run_ms2007(); assert r["status"]=="PASS"
    assert len(r["partial_survivors"])==2
    assert r["unique_probe_action_id"]=="P2"
    assert r["caller_supplied_alternative_buckets"]=="NO"
    assert r["selection_authority"]==r["execution_authority"]=="NONE"

def test_ms2007_actual_p2_raw_response_collapses_surviving_historical_set():
    r=run_ms2007(); assert r["post_probe_resolved_bucket"] in r["qualified_buckets"]
    assert r["identity_authority"]==r["semantic_reference_authority"]==r["truth_authority"]=="NONE"
