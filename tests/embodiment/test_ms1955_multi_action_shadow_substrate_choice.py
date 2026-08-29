from scratch.ms1955_multi_action_world_choice import run_choice_reversal


def test_multi_action_shadow_world_selects_better_learned_consequence_not_identifier_order():
    result = run_choice_reversal()
    assert result['status'] == 'PASS'
    assert result['world_a']['winner'] == 'ACT-A'
    assert result['world_b']['winner'] == 'ACT-Z'
    assert result['world_a']['winner_effect'] == result['world_b']['winner_effect'] == 3.2
    for world in (result['world_a'], result['world_b']):
        assert set(world['individual_commitments'].values()) == {
            'BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE'
        }
        assert world['proposal_effect'] == world['actual_value'] == 3.2
        assert world['proposal_final_state'] == world['actual_final_state'] == 'HIGH'
    assert result['semantic_preference_authority'] == 'NONE'
