from scratch.lang_arity_contiguous_token_window_audit import run_audit

def test_contiguous_current_token_suffix_is_observable_bounded_arity_candidate_not_silent_crop():
    r=run_audit()
    assert r['status']=='CONTIGUOUS_CURRENT_TOKEN_SUFFIX_IS_BOUNDED_ARITY_CARRIER_CANDIDATE'
    assert (r['suffix_after_xyz'],r['suffix_after_composition_evidence'],r['suffix_after_two_tokens'])==(3,0,2)
    assert r['suffix_after_represented_boundary_plus_one_token']==1
    assert r['suffix_after_overlong_run']==5
    assert r['represented_non_token_boundary_closes_window']=='YES'
    assert r['unrepresented_pause_creates_boundary']=='NO'
    assert r['silent_truncation_allowed']=='NO'
    assert r['semantic_grouping_authority']=='NONE'
