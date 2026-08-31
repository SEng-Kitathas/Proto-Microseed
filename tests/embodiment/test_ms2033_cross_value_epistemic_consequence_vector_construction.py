from scratch.ms2033_cross_value_epistemic_consequence_vector_construction import run_ms2033


def test_ms2033_constructs_complete_current_tradeoff_vectors_without_selection_authority():
    r = run_ms2033()
    assert r["status"] == "COMPOSITIONAL_VECTOR_CONSTRUCTION_EARNED_RESEARCH_ONLY"
    x = r["complete_tradeoff"]
    assert x["status"] == "PASS"
    assert x["p2"]["status"] == "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR"
    assert x["p4"]["status"] == "CURRENT_CROSS_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR"
    assert x["p2"]["worst_residual_by_value"] == {"V": 0.0, "W": 0.5}
    assert x["p4"]["worst_residual_by_value"] == {"V": 0.5, "W": 0.0}
    assert x["tradeoff"] == "P2_BETTER_V__P4_BETTER_W"
    assert x["cross_value_selection_authority"] == "NONE"
    assert x["read_only"] is True
    assert x["handler_calls"] == []


def test_ms2033_missing_coordinate_effect_does_not_zero_fill():
    r = run_ms2033()
    x = r["missing_witness"]
    assert x["status"] == "PASS"
    assert x["result"]["status"] == "DEFER_UNKNOWN"
    assert x["result"]["reason"] == "CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:B:W"
    assert x["zero_fill"] == "NO"
    assert x["handler_calls"] == []


def test_ms2033_conflicting_effect_ancestry_is_not_averaged():
    r = run_ms2033()
    x = r["ambiguous_ancestry"]
    assert x["status"] == "PASS"
    assert x["result"]["status"] == "DEFER_UNKNOWN"
    assert "UNKNOWN_MULTIPLE_CURRENT_ANCESTRY_SHAPES" in x["result"]["reason"]
    assert x["ancestry_averaging"] == "NO"
    assert x["handler_calls"] == []


def test_ms2033_value_drift_rejects_old_effect_witnesses():
    r = run_ms2033()
    x = r["value_drift"]
    assert x["status"] == "PASS"
    assert x["result"]["status"] == "DEFER_UNKNOWN"
    assert x["result"]["reason"] == "VALUE_NOT_CURRENT:W"
    assert x["old_effect_witness_reuse"] == "REJECTED"
    assert r["pareto_comparator_authorized"] == "NO"
    assert r["cross_value_selection_authority"] == "NONE"
