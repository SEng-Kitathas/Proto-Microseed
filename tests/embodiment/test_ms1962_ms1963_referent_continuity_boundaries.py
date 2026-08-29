from scratch.ms1962_organism_continuity_not_referent_identity import run_continuity_hostile
from scratch.ms1963_referent_specific_overlap_continuity import run_overlap_continuity


def test_organism_developmental_continuity_does_not_prove_external_referent_identity():
    result = run_continuity_hostile()
    assert result['status'] == 'PASS'
    assert result['biography_relation'] == 'DESCENDANT_CONTINUATION'
    witness = result['continuity_witness']
    assert witness['branch_semantics'] == 'BRANCH_RELATIVE_DESCENDANT_CONTINUATION'
    assert witness['numerical_identity_authority'] == 'NONE'
    assert result['session_a_alignment'] != result['session_b_alignment']
    assert result['required_breaker'] == 'REFERENT_SPECIFIC_CAUSAL_CONTINUITY_OR_ASYMMETRIC_OVERLAP_EVIDENCE'


def test_referent_specific_overlap_bridges_old_and_new_sensor_representations_operationally():
    result = run_overlap_continuity()
    assert result['status'] == 'PASS'
    assert result['continuity_authority'] == 'OPERATIONAL_REFERENT_CONTINUITY_ONLY'
    assert result['numerical_identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert len(result['bridge']) == 2
    for bridge in result['bridge'].values():
        assert bridge['old_group']
        assert bridge['new_group']
        assert len(bridge['overlap_group']) > len(bridge['old_group'])
