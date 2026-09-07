from scratch.lang_arity_negative_token_evidence_hostile import run_hostile

def test_negative_token_evidence_is_rejected_by_b2_b3_and_generic_candidate_after_shared_admissibility_repair():
    r=run_hostile()
    assert r['status']=='NEGATIVE_TOKEN_GUARD_PRESENT'
    assert r['generic_accepted_negative'] is False
    assert r['b3_accepted_negative'] is False
    assert r['b2_accepted_negative'] is False
    assert r['generic_status']==r['b3_status']==r['b2_status']=='DEFER_UNKNOWN'
    assert r['generic_reason']==r['b3_reason']==r['b2_reason']=='NEGATIVE_TOKEN_EVIDENCE_NOT_ADMITTED'
    assert r['negative_token_must_be_operand_authority']=='NO'
