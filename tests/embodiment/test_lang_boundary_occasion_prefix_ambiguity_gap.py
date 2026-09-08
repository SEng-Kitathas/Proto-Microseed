from scratch.lang_boundary_occasion_prefix_ambiguity_gap import run_gap

def test_same_owned_two_token_prefix_can_lawfully_end_at_2_or_continue_to_3_or_4_without_boundary_signal():
    r=run_gap()
    assert r['status']=='STOP_VALID_COMPOSITION_PREFIX_DOES_NOT_OWN_BOUNDARY_OCCASION'
    assert r['lawful_final_arities']==(2,3,4)
    assert r['same_owned_prefix_supports_multiple_lawful_continuations']=='YES'
    assert r['automatic_boundary_event_after_two_tokens']=='NO'
    assert r['caller_invocation_timing_currently_selects_when_composition_evidence_closes_window']=='YES'
    assert r['valid_prefix_boundary_authority']=='NONE'
    assert r['localized_gap']=='OWNED_NONSEMANTIC_BOUNDARY_OCCASION_DISCRIMINATOR_MISSING'
