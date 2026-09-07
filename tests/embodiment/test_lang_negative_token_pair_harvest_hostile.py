from scratch.lang_negative_token_pair_harvest_hostile import run_hostile

def test_negative_token_observation_is_a_chronology_boundary_but_not_a_harvestable_native_pair_source_after_repair():
    r=run_hostile()
    assert r['status']=='NEGATIVE_TOKEN_HARVEST_GUARD_PRESENT'
    assert r['negative_token_became_pair_source'] is False
    assert r['contaminated_pair_count']==0
    assert r['negative_unpaired']==({'token_evidence_id':'E-NEG-HARVEST-TOKEN-R4','reason':'NEGATIVE_TOKEN_EVIDENCE_NOT_ADMITTED'},)
    assert r['qualification_authority_from_negative_token']=='NONE'
    assert r['repair_scope']=='TOKEN_EVIDENCE_ADMISSIBILITY_OWNER_SHARED_BY_HARVEST_AND_COMPOSITION'
