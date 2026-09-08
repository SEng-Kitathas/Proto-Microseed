from scratch.lang_arity_four_grounded_referents_fixture import fixture,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_boundary_occasion_unique_structural_split_prototype import derive_unique_structural_split_candidate


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def _run(sequence,tokens=('R4','T9','W3','K7'),sensor_transform=None,base=43000):
    td,m,world,seeded=fixture(tokens=tokens,sensor_transform=sensor_transform)
    try:
        _obs(m,sequence,'STRUCT-SPLIT',base)
        return derive_unique_structural_split_candidate(m)
    finally:_close(m);td.cleanup()


def test_duplicate_extension_conflict_with_exactly_one_lawful_two_window_split_yields_candidate():
    r=_run(('R4','T9','R4','K7'))
    assert r['status']=='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE',r
    assert r['candidate']['split_index']==2
    assert r['candidate_count']==1
    assert r['selection_authority']=='CONTENT_UNIQUENESS_ONLY'
    assert r['execution_authority']==r['semantic_grouping_authority']==r['boundary_creation_effect_authority']=='NONE'
    assert r['caller_supplied_split']=='NO'


def test_fully_admissible_arity4_has_no_structural_boundary_candidate():
    r=_run(('R4','T9','W3','K7'),base=44000)
    assert r['status']=='NO_STRUCTURAL_BOUNDARY_OCCASION_REQUIRED',r


def test_overlong_window_with_two_lawful_splits_abstains_as_ambiguous():
    r=_run(('R4','T9','W3','R4','K7'),base=45000)
    assert r['status']=='AMBIGUOUS_STRUCTURAL_BOUNDARY_OCCASION',r
    assert r['candidate_count']==2
    assert r['selection_authority']=='NONE'


def test_no_lawful_split_abstains():
    r=_run(('R4','R4','T9','K7'),base=46000)
    assert r['status']=='NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION',r
    assert r['candidate_count']==0


def test_unique_split_is_invariant_to_token_labels_and_sensor_representation():
    a=_run(('R4','T9','R4','K7'),base=47000)
    b=_run(('K7','R4','K7','W3'),tokens=('K7','R4','T9','W3'),base=48000)
    p=_run(('R4','T9','R4','K7'),sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=49000)
    inv=_run(('R4','T9','R4','K7'),sensor_transform=lambda row:tuple(-x for x in row),base=50000)
    assert a['status']==b['status']==p['status']==inv['status']=='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE'
    assert a['candidate']['split_index']==b['candidate']['split_index']==p['candidate']['split_index']==inv['candidate']['split_index']==2
    assert a['referent_signatures']==b['referent_signatures']==p['referent_signatures']==inv['referent_signatures']
