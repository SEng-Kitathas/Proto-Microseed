from scratch.ms2012_referent_probe_authenticated_observation_closure import positive_authenticated, forged_unadmitted

def test_ms2012_authenticated_referent_probe_observation_closes_trial_collapses_live_set_and_requests_revisit():
    r=positive_authenticated(); assert r["status"]=="PASS"
    assert r["admitted_status"]=="ADMITTED_OPAQUE_TRANSITION_SAMPLE"
    assert r["prefix_actions"]==["P0","P1","P2"] and r["resolved_bucket_id"]==r["expected_bucket_id"]
    assert r["program_evidence"]["status"]=="PROGRAM_EVIDENCE_RECORDED" and r["program_evidence"]["state"]=="REVISIT_REQUIRED"
    assert r["truth_authority"]==r["answer_authority"]==r["execution_authority"]=="NONE"

def test_ms2012_forged_observation_cannot_become_referent_program_evidence():
    r=forged_unadmitted(); assert r["status"]=="OBSERVED"
    assert r["admitted"]["reason"]=="AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED"
    assert r["forged_program_evidence_accepted"] is False
    assert r["program_evidence"]["status"]=="PROGRAM_EVIDENCE_REJECTED"
    assert r["program_evidence"]["reason"]=="AUTHENTICATED_PROGRAM_STEP_OBSERVATION_REQUIRED"
    assert r["deficit_state"]=="ACTION_LIMITED"
