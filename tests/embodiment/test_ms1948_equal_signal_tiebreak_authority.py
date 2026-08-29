from scratch.ms1948_equal_signal_tiebreak_dual_arm import run_world


def test_equal_modeled_signal_options_use_reproducible_id_arbitration_not_physical_token_preference():
    world_a = run_world({'SIG-A': 'T0', 'SIG-Z': 'T1'}, 'REG-A')
    world_b = run_world({'SIG-Z': 'T0', 'SIG-A': 'T1'}, 'REG-B')

    assert world_a['winner_capability'] == world_b['winner_capability'] == 'SIG-A'
    assert world_a['winner_physical_token'] == 'T0'
    assert world_b['winner_physical_token'] == 'T1'

    for world in (world_a, world_b):
        assert set(world['single_commitments']) == {'SIG-A', 'SIG-Z'}
        assert set(world['single_commitments'].values()) == {
            'BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE'
        }
        assert world['coordination_subject_unchanged'] is True
        assert world['language'] == 'DEFERRED_PRELINGUAL_COGNITION_ACTIVE'
