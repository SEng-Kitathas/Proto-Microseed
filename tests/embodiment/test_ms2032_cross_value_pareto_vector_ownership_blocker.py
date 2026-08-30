from scratch.ms2032_cross_value_pareto_vector_ownership_blocker import run_ms2032


def test_ms2032_cross_value_pareto_vector_ownership_blocker_is_reproduced_without_new_authority():
    r = run_ms2032()
    assert r["status"] == "SUBSTANTIVE_BLOCKER_REPRODUCED"
    assert r["owned_opportunity_single_coordinate"]["complete_cross_value_opportunity_vector_owned"] == "NO"
    assert r["same_value_selector_cross_value_refusal"]["commitment"]["reason"] == "EXACT_SAME_VALUE_COORDINATE_REQUIRED"
    assert r["multi_value_immediate_effect_boundary"]["reason"] == "MULTIPLE_LAWFUL_ACTIONS_NO_RANKING_AUTHORITY"
    assert r["cross_value_laundering_rejected"]["cross_value_relation_laundering"] == "REJECTED"
    assert r["pareto_comparison_surface_owned"] == "NO"
    assert r["cross_value_selection_authority"] == "NONE"
    assert r["new_scheduler_required"] == "NO_EVIDENCE"
    assert r["scalar_utility_required"] == "NO_EVIDENCE"
