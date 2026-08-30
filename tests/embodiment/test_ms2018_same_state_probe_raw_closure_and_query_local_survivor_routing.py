from scratch.ms2018_same_state_probe_raw_closure_and_query_local_survivor_routing import run_ms2018


def test_ms2018_same_state_probe_closes_exact_raw_discriminator_and_routes_single_survivor_query_locally():
    r = run_ms2018()
    assert r["status"] == "PASS"
    assert r["p2_actual_next_state_id"] == "s0"
    assert r["p2_calls"] == ["P2"]
    assert r["admitted_status"] == "ADMITTED_OPAQUE_TRANSITION_SAMPLE"
    assert r["prefix_actions"] == ["P0", "P1", "P2"]
    assert r["program_evidence_status"] == "PROGRAM_EVIDENCE_RECORDED"
    assert r["deficit_state_after_program_evidence"] == "REVISIT_REQUIRED"
    assert r["query_local_A_status"] == r["query_local_B_status"] == "CURRENT_PARTITION_SCOPED_RELATION"
    assert r["full_reassociation_status"] == "DEFER_UNKNOWN"
    assert r["full_reassociation_reason"] == "NO_PRIOR_OPERATIONAL_REFERENT_SIGNATURE_CLASS_WITNESS"
    assert r["single_survivor_is_full_identity"] == "NO"
    assert r["truth_authority"] == r["identity_authority"] == r["semantic_reference_authority"] == r["execution_authority"] == "NONE"
