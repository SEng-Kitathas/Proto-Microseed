from scratch.lang_boundary_occasion_bookkeeping_gap import run_gap

def test_optional_internal_currentness_bookkeeping_does_not_become_token_grouping_boundary():
    r=run_gap()
    assert r['status']=='STOP_INTERNAL_BOOKKEEPING_EVENT_CANNOT_OWN_TOKEN_GROUPING_BOUNDARY'
    assert r['plain']['derived_arity']==r['with_bookkeeping']['derived_arity']==4
    assert r['plain']['digest']==r['with_bookkeeping']['digest']
    assert r['same_external_token_sequence']==r['bookkeeping_optional_without_world_change']=='YES'
    assert r['with_bookkeeping']['bookkeeping_kind']=='OPAQUE_EVIDENCE_ASSOCIATION_CURRENTNESS_WITNESS'
    assert r['bookkeeping_grouping_authority']=='NONE'
    assert r['localized_gap']=='NO_LAWFUL_PASSIVE_TOKEN_ONLY_BOUNDARY_OCCASION_PRESENT'
