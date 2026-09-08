from scratch.lang_action_boundary_recognition_vs_creation_audit import run_audit

def test_action_boundary_owner_recognizes_existing_execution_but_cannot_create_or_select_boundary_actions():
    r=run_audit()
    assert r['status']=='ACTION_EXECUTION_BOUNDARY_RECOGNITION_ONLY'
    assert r['boundary_owner_consumes_existing_store_events']=='YES'
    assert r['boundary_owner_action_creation_calls']==()
    assert r['boundary_action_creation_authority']==r['effect_authority_gain']==r['semantic_grouping_authority']=='NONE'
    assert r['generic_episode_grouping_api_present'] is False
    assert r['episode_schema_registration_external_qualification'] is True
    assert r['historical_endogenous_episode_grouping_status']=='RESEARCH_ONLY'
    assert r['passive_token_only_boundary_ownership']==r['autonomous_boundary_occasion_selection']=='NOT_EARNED'
