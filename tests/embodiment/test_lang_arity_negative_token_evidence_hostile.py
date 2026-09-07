from scratch.lang_arity_negative_token_evidence_hostile import run_hostile

def test_negative_token_evidence_false_green_is_exposed_before_generalized_arity_promotion():
    r=run_hostile()
    assert r['status']=='VIOLATION_NEGATIVE_TOKEN_EVIDENCE_ACCEPTED_AS_COMPOSITION_OPERAND'
    assert r['generic_accepted_negative'] is True
    assert r['b3_accepted_negative'] is True
    assert r['b2_accepted_negative'] is True
    assert r['negative_token_must_be_operand_authority']=='NO'
    assert r['arity_promotion_allowed']=='NO'
