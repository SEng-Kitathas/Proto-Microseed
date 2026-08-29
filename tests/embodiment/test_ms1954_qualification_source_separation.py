from scratch.ms1954_qualification_source_separation import run_separation


def test_runtime_environment_and_qualification_source_are_separate_roles_with_compatibility_gate():
    result = run_separation()
    assert result['status'] == 'PASS'
    assert result['missing_source'] == {
        'reason': 'EXTERNAL_QUALIFICATION_SOURCE_REQUIRED',
        'outcome_count': 0,
    }
    assert result['mismatched_source'] == {
        'reason': 'QUALIFICATION_SOURCE_ENVIRONMENT_COMPATIBILITY_MISMATCH',
        'outcome_count': 0,
    }
    matched = result['matched_separate_source']
    assert matched['qualification_evidence_count'] == 16
    assert matched['qualification_evidence_sources'] == ['EXTERNAL-QUALIFICATION:QUAL-MATCHED']
    assert matched['provider_ids'] == ['QUAL-MATCHED']
    assert matched['runtime_world_object_is_qualification_world_object'] is False
    assert result['evidence_independence_authority'] == 'NONE'
