from scratch.lang_active_acquisition_environmental_coupling_audit import run_campaign


def test_acquisition_effect_does_not_generate_opaque_token_presentation():
    r=run_campaign()
    assert r['status']=='STOP_NOVEL_ASSOCIATION_ACQUISITION_AT_EXOGENOUS_TOKEN_PRESENTATION_BOUNDARY'
    assert r['selected_probe_action_id']=='P2'
    assert r['effect_execution_status']=='ACTION_EXECUTED'
    assert r['token_observations_after_effect']==r['token_observations_before_effect']
    assert r['effect_created_token_observation']=='NO'
    assert r['token_observations_after_external_ingress']==r['token_observations_after_effect']+1
    assert r['external_ingress_created_token_observation']=='YES'
    assert r['production_token_kind_mentions']==1
    assert r['production_token_writer_patterns']==0
    assert r['token_presentation_owner']=='EXOGENOUS_INGRESS'
    assert r['novel_pair_active_acquisition_closure']=='NOT_EARNED'
    assert r['remaining_missing_mechanism']=='LAWFUL_ENVIRONMENTAL_TOKEN_COUPLING_TO_ACQUISITION_EVENT'
    assert r['effect_authority_from_token_need']=='NONE'
