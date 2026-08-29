from scratch.ms1972_process_backed_representation_alias_growth import run_ms1972


def test_process_backed_alias_history_grows_generic_externally_qualified_refinement():
    result = run_ms1972()
    assert result['status'] == 'PASS'
    assert result['context_outcomes'] == (('r', 's2', 2), ('s0', 'sx', 2))
    assert result['projection']['current'] is True
    assert result['projection']['projection_origin'] == 'ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED'
    assert result['projection']['projection_id'] == 'P-MS1972'
    assert len(result['history']) == 4
    assert {row['context'] for row in result['history']} == {'s0', 'r'}
    assert {row['endpoint'] for row in result['history']} == {'sx', 's2'}
    assert len(result['heldout_rows']) == 8
    assert result['history_acquisition_assistance'] == 'EXTERNALLY_EQUIPPED_REHEARSAL_SEEDS_FROM_SEPARATE_PROCESS_PROBES'
    assert result['truth_authority'] == 'NONE'
    assert result['hidden_state_authority'] == 'NONE'
    assert result['semantic_category_authority'] == 'NONE'
    assert result['language_authority'] == 'NONE'
