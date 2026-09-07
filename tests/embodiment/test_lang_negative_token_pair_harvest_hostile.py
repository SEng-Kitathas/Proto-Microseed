from scratch.lang_negative_token_pair_harvest_hostile import run_hostile

def test_negative_token_observation_is_currently_harvested_as_native_pair_and_must_be_repaired():
    r=run_hostile()
    assert r['status']=='VIOLATION_NEGATIVE_TOKEN_EVIDENCE_HARVESTED_AS_NATIVE_PAIR'
    assert r['negative_token_became_pair_source'] is True
    assert r['contaminated_pair_count']==1
    assert r['qualification_authority_from_negative_token']=='NONE'
    assert r['repair_scope']=='TOKEN_EVIDENCE_ADMISSIBILITY_OWNER_SHARED_BY_HARVEST_AND_COMPOSITION'
