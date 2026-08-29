from scratch.ms1970_affordance_split_not_genealogy import run_ms1970


def test_affordance_decomposition_does_not_establish_genealogical_split_or_identity_inheritance():
    result = run_ms1970()
    assert result['status'] == 'BOUNDARY_CONFIRMED'
    split = result['genuine_split_case']
    replacement = result['hidden_replacement_case']
    assert split['parent'] == replacement['parent']
    assert split['children'] == replacement['children']
    assert split['parent_response'] == split['union_response']
    assert replacement['parent_response'] == replacement['union_response']
    assert split['union_response'] == replacement['union_response']
    assert split['evaluator_lineage']['mode'] == 'SPLIT'
    assert replacement['evaluator_lineage']['mode'] == 'REPLACEMENT'
    assert result['affordance_decomposition_authority'] == 'OPERATIONAL_RELATION_ONLY'
    assert result['genealogy_authority'] == 'NONE'
    assert result['numerical_identity_inheritance_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['language_authority'] == 'NONE'
