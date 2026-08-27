from microseed.development.epistemic import EpistemicContrastBinding, EpistemicContrastRow


def test_epistemic_contrast_owns_opaque_alternative_partition_but_not_action_transition_model_content():
    row = EpistemicContrastRow(
        'P', 0, (('h1', 'a'*64), ('h2', 'b'*64)), condition_signature_sha256='c'*64,
    )
    binding = EpistemicContrastBinding(
        'B', 'D', 'd'*64, (row,), binding_origin='SUPPLIED_AND_PROVENANCED',
    )
    payload = row.serializable()
    assert set(payload) == {
        'projection_id', 'projection_epoch', 'candidate_outcome_digests', 'condition_signature_sha256'
    }
    # The existing owner can preserve candidate alternatives and their opaque
    # predicted-outcome partition, but has no state/action/next-state/value model
    # content from which EpistemicDecisionBearingContext.relation_sets can be built.
    for forbidden in ('state_id', 'capability_id', 'next_state_id', 'value_effect', 'relation_set'):
        assert forbidden not in payload
    assert binding.binding_origin == 'SUPPLIED_AND_PROVENANCED'
    assert binding.raw_projection_discovery_authority == 'NONE'
    assert binding.truth_authority == binding.semantic_question_authority == 'NONE'
