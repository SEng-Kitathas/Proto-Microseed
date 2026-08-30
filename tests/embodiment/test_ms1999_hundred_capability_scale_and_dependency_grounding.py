from scratch.ms1999_hundred_capability_scale_and_dependency_grounding import (
    MAIN,
    run_dependency_grounding_arm,
    run_dependency_topology_arm,
    run_hundred_effect_arm,
    run_hundred_tie_arm,
)


def test_ms1999_hundred_effect_program_construction_survives_order_budget_and_local_drift():
    left = run_hundred_effect_arm(("P1", "P2", "N1", "N2"))
    right = run_hundred_effect_arm(("N2", "P2", "N1", "P1"))
    assert left["effect_capability_count"] == right["effect_capability_count"] == 100
    assert left["generated_program"] == right["generated_program"] == list(MAIN)
    assert left["candidate_id"] == right["candidate_id"]
    assert left["candidate_sha256"] == right["candidate_sha256"]
    assert left["budget_status"] == right["budget_status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED"
    assert left["local_stale_count"] == right["local_stale_count"] == 2
    assert left["stale_admission_status"] == right["stale_admission_status"] == "ABSTAIN"
    assert left["same_identity_requalification_path"] == right["same_identity_requalification_path"] == "MISSING"
    assert left["execution_authority"] == right["execution_authority"] == "NONE"


def test_ms1999_hundred_effect_equal_information_tie_preserves_ambiguity():
    result = run_hundred_tie_arm()
    assert result["effect_capability_count"] == 100
    assert result["arbitration_status"] == "MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES"
    assert result["arbitration_reason"] == "NO_UNIQUE_STRICT_PARTITION_REFINEMENT"
    assert result["selection_authority"] == result["execution_authority"] == result["truth_authority"] == "NONE"
    assert result["caller_order_selection"] == "NO"


def test_ms1999_dependency_closure_preserves_deferred_structure_but_blocks_missing_stale_and_cycles_from_authority():
    result = run_dependency_grounding_arm()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["missing_dependency_structural_registration"] == "ALLOWED"
    assert result["missing_dependency_use"] == "UNKNOWN_INCOMPLETE"
    assert result["missing_dependency_use_authority"] == "NONE"
    assert result["deferred_dependency_before"] == "UNKNOWN_INCOMPLETE"
    assert result["deferred_dependency_after"] == "CAPABILITY_RESULT"
    assert result["cycle_structural_representation"] == "ALLOWED"
    assert result["cycle_a_reason"].startswith("DEPENDENCY_CYCLE_UNQUALIFIED:")
    assert result["cycle_b_reason"].startswith("DEPENDENCY_CYCLE_UNQUALIFIED:")
    assert result["cycle_execution_authority"] == "NONE"
    assert result["unclosed_effects_in_endogenous_action_alphabet"] == []
    assert "CANDIDATE_DEPENDENCY_CLOSURE_INCOMPLETE" in result["missing_dependency_candidate_admission"]
    assert "CANDIDATE_DEPENDENCY_CLOSURE_INCOMPLETE" in result["stale_dependency_candidate_admission"]
    assert result["dependency_epoch_set_mismatch"] == "ValueError:CANDIDATE_DEPENDENCY_EPOCH_SET_MISMATCH"
    assert result["new_manager_required"] == "NO"


def test_ms1999_locality_and_iterative_deep_closure_do_not_claim_requalification():
    result = run_dependency_topology_arm()
    assert result["status"] == "PASS_LOCALITY_AND_ITERATIVE_CLOSURE_ONLY"
    assert result["branch_graph_capability_count"] == 100
    assert result["branch_root_stale_count"] == 10
    assert result["leaf_stale_count"] == 1
    assert result["shared_graph_capability_count"] == result["shared_root_stale_count"] == 101
    assert result["deep_chain_capability_count"] == 1500
    assert result["deep_chain_closure_visited_count"] == 1500
    assert result["deep_chain_max_depth"] == 1500
    assert result["actual_requalification_closure"] == "NOT_AVAILABLE__SAME_IDENTITY_CAPABILITY_REQUALIFICATION_PATH_MISSING"
