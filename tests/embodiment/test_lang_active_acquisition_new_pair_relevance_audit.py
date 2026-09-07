from scratch.lang_active_acquisition_new_pair_relevance_audit import run_campaign


def test_unpaired_token_does_not_make_generic_referent_probe_token_specific():
    r=run_campaign()
    assert r['status']=='STOP_NEW_PAIR_ACTIVE_ACQUISITION_NOT_TOKEN_CONDITIONED'
    assert r['generic_probe_action_id']=='P2'
    assert r['generic_opportunity_invariant_to_token_identity']=='YES'
    assert r['token_specific_information_bearing_premise']=='ABSENT'
    assert r['active_localization_alone_would_establish_new_pair']=='NO'
    assert r['localized_missing_mechanism']=='TOKEN_CONDITIONED_GROUNDED_ACQUISITION_RELEVANCE_OR_ENVIRONMENTAL_COUPLING'
    assert r['new_pair_registration_authority']==r['effect_authority_from_unknown_token']=='NONE'
    for key in ('token_a','token_b'):
        assert r[key]['opportunity_status']=='CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY'
        assert r[key]['probe_action_id']=='P2'
        assert r[key]['token_value_present_in_opportunity_carriers'] is False
        assert r[key]['token_evidence_present_in_opportunity_carriers'] is False
