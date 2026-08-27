from microseed.development.action_learning import ActionOutcomeExperience, nominate_action_outcome_candidates


def row(i: int, next_state: str) -> ActionOutcomeExperience:
    return ActionOutcomeExperience(
        evidence_id=f'E{i}', execution_id=f'X{i}', start_state_id='s0', capability_id='A',
        actual_next_state_id=next_state, actual_value_effect=0.0, capability_epoch=0,
        frame_epochs=(('F',0),), episode_schema_epochs=(('EP',0),), value_epoch=('V',0),
    )


def test_existing_action_outcome_owner_compresses_one_ancestry_group_to_one_relation_or_abstains_not_competing_models():
    # Exact ambiguity is not emitted as two candidate models; it is withheld.
    split = tuple(row(i, 'left' if i < 8 else 'right') for i in range(16))
    assert nominate_action_outcome_candidates(split) == ()

    # Sufficiently dominant evidence yields one bounded predictive candidate, not a
    # surviving alternative set containing both observed consequences.
    dominant = tuple(row(i, 'left' if i < 13 else 'right') for i in range(16))
    out = nominate_action_outcome_candidates(dominant)
    assert len(out) == 1
    assert out[0].next_state_id == 'left'
    assert out[0].support == 16
    assert out[0].consistency == 13/16
    assert out[0].authority == 'MODEL_OUTPUT_ONLY'
    assert out[0].truth_authority == out[0].qualification_authority == 'NONE'
