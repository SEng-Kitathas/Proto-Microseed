from scratch.ms2013_referent_discriminator_requires_post_probe_raw import authenticated_no_post_raw
from scratch.ms2012_referent_probe_authenticated_observation_closure import positive_authenticated

def test_ms2013_authenticated_state_outcome_without_post_probe_raw_cannot_satisfy_referent_discriminator():
    r=authenticated_no_post_raw(); assert r["status"]=="OBSERVED"
    assert r["admitted"]=="ADMITTED_OPAQUE_TRANSITION_SAMPLE"
    assert r["prefix_without_post_raw"]["status"]=="DEFER_UNKNOWN"
    assert r["accepted_without_post_raw"] is False
    assert r["program_evidence"]["status"]=="PROGRAM_EVIDENCE_REJECTED"
    assert r["program_evidence"]["reason"]=="CURRENT_REFERENT_POST_PROBE_RAW_OBSERVATION_REQUIRED"
    assert r["deficit_state"]=="ACTION_LIMITED"

def test_ms2013_post_probe_raw_receipt_preserves_authenticated_positive_closure():
    r=positive_authenticated(); assert r["status"]=="PASS"
    assert r["prefix_actions"]==["P0","P1","P2"]
    assert r["program_evidence"]["status"]=="PROGRAM_EVIDENCE_RECORDED"
    assert r["program_evidence"]["state"]=="REVISIT_REQUIRED"
