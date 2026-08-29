from scratch.ms1969_gap_reappearance_identity_boundary import run_ms1969


def test_reappearance_signature_supports_operational_reassociation_not_individual_persistence():
    result = run_ms1969()
    assert result['status'] == 'BOUNDARY_CONFIRMED'
    continuous = result['continuous_case']
    replaced = result['hidden_substitution_case']
    assert continuous['signature_set'] == replaced['signature_set']
    assert continuous['evaluator_persistence'] is True
    assert replaced['evaluator_persistence'] is False
    assert continuous['pre']['groups'] == replaced['pre']['groups']
    assert continuous['post']['groups'] == replaced['post']['groups']
    assert result['operational_reassociation_authority'] == 'AFFORDANCE_RELATIVE_ONLY'
    assert result['individual_persistence_authority'] == 'NONE'
    assert result['numerical_identity_authority'] == 'NONE'
    assert result['semantic_reference_authority'] == 'NONE'
    assert result['language_authority'] == 'NONE'
