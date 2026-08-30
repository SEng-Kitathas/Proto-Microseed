from scratch.ms1996_endogenous_program_caller_choice_elimination import run_ms1996


def test_ms1996_owned_history_and_current_effect_registry_generate_program_without_caller_action_choice():
    result = run_ms1996()
    assert result['status'] == 'BOUNDARY_CONFIRMED'
    assert result['new_core_mechanism_required'] == 'NO'
    assert result['caller_supplied_program_sequence'] == 'NO'
    assert result['caller_supplied_preferred_action'] == 'NO'
    assert result['history_insertion_order_selection'] == 'NO'
    assert result['stale_primitive_policy'] == 'REGENERATE_CURRENT_SURFACE_AND_ABSTAIN'

    left, right = result['left'], result['right']
    assert left['status'] == right['status'] == 'PASS'
    assert left['generated_program'] == right['generated_program'] == ['K-17', 'M-23', 'R-41']
    assert left['candidate_id'] == right['candidate_id']
    assert left['candidate_sha256'] == right['candidate_sha256']
    assert left['history_order'] != right['history_order']
    for row in (left, right):
        assert row['caller_supplied_preferred_action_or_program'] == 'NO'
        assert row['intents_added_during_generation_and_arbitration'] == 0
        assert row['executions_added_during_generation_and_arbitration'] == 0
        assert row['priority'] == 'YES'
        assert row['information'] == 'YES'
        assert row['budget_status'] == 'SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED'
        assert row['stale_generated_status'] == 'REPRESENTED_REACHABILITY_INCOMPLETE'
        assert row['stale_admission_status'] == 'ABSTAIN'
        assert row['stale_admission_reason'] == 'CURRENT_GENERATOR_TRANSITION_UNREPRESENTED'
        assert row['proposal_authority'] == 'NONE'
        assert row['execution_authority'] == 'NONE'
        assert row['truth_authority'] == 'NONE'
        assert row['semantic_action_authority'] == 'NONE'
        for handle in ('K-17', 'M-23', 'R-41', 'N-61', 'N-67'):
            assert handle in row['generator_tokens']


def test_ms1996_equal_information_partitions_remain_unselected_without_pick_first_authority():
    result = run_ms1996()
    tie = result['tie']
    assert tie['status'] == 'PASS'
    assert tie['programs'] == [['K-17', 'R-41'], ['K-17', 'R-43']]
    assert tie['arbitration_status'] == 'MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES'
    assert tie['arbitration_reason'] == 'NO_UNIQUE_STRICT_PARTITION_REFINEMENT'
    assert tie['selection_authority'] == 'NONE'
    assert tie['execution_authority'] == 'NONE'
    assert tie['truth_authority'] == 'NONE'
    assert tie['caller_order_selection'] == 'NO'
    assert len(tie['candidate_ids']) == 2
    assert tie['partitions'][0][1] == [[0], [1]]
    assert tie['partitions'][1][1] == [[0], [1]]
