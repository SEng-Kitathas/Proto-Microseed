from scratch.ms1997_lived_history_to_endogenous_program import MAIN, run_ms1997


def test_ms1997_authenticated_lived_history_forms_three_locus_surface_and_generates_program_without_synthetic_action_records():
    result = run_ms1997()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["new_core_mechanism_required"] == "NO"
    assert result["history_source"] == "AUTHENTICATED_ORDINARY_EFFECT_EXECUTION_PLUS_BOUNDED_OBSERVATION_INGRESS"
    assert result["ordinary_execution_count"] == 12
    assert result["ordinary_outcome_count"] == 12
    assert result["experience_count"] == 12
    assert result["alternative_hypothesis_count"] == 6
    assert result["successor_coupling_count"] == 4
    assert result["three_locus_chain_count"] == 2
    assert result["alternative_model_count"] == 2
    assert result["generated_program"] == list(MAIN)
    assert result["candidate_execution_authority"] == "NONE"
    assert result["candidate_truth_authority"] == "NONE"
    assert result["caller_supplied_endogenous_program"] == "NO"
    assert result["caller_supplied_preferred_action"].startswith("NO__")

    # The hidden causal mode label is evaluator-only, but the training assistance is
    # honestly mode-conditioned and therefore remains an explicit unclosed seam.
    assert result["evaluator_hidden_mode_label_in_durable_organism_evidence"] == "NO"
    assert result["mode_conditioned_training_assistance"] == "YES__EXPLICIT_REMAINING_LIMITATION"

    for episode in result["episodes"]:
        assert episode["selected_actions"] == list(MAIN)
        assert episode["final_value"] == 0.0
        # After the first action, each next intent must be content-bound to the
        # immediately preceding ordinary outcome evidence.
        chain = episode["evidence_chain"]
        assert chain[1][0] == chain[0][1]
        assert chain[2][0] == chain[1][1]
