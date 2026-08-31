from scratch.ms2047_v1_candidate_simplification_and_authority_audit import run_ms2047


def test_ms2047_post_ms2035_production_delta_is_bounded_to_existing_owners():
    r = run_ms2047()
    assert r["status"] == "V1_CANDIDATE_SHAPE_AUDIT_PASS"
    assert r["core_delta"]["new_core_files"] == []
    assert r["core_delta"]["changed_core_paths"] == [
        "microseed/development/epistemic_action.py",
        "microseed/development/epistemic_priority.py",
        "microseed/development/value.py",
        "microseed/runtime/entity.py",
    ]
    assert r["runtime_audit"]["forbidden_cross_cutting_attrs_present"] == []
    assert all(not hits for hits in r["forbidden_token_hits"].values())


def test_ms2047_selection_authority_remains_separate_from_execution_and_language():
    r = run_ms2047()
    assert r["tradeoff_surface"] == {
        "status": "NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION",
        "selection_authority": "NONE",
        "execution_authority": "NONE",
    }
    assert r["dominance_surface"]["status"] == "CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION"
    assert r["dominance_surface"]["selection_authority"] == "STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY"
    assert r["dominance_surface"]["execution_authority"] == "NONE"
    assert r["runtime_audit"]["language_status"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    assert r["canonical_promotion_authority"] == "OPERATOR_ONLY"
    assert r["promotion_law"] == "TECHNICAL_READINESS_FOR_PROMOTION_REVIEW != CANONICAL_PROMOTION_AUTHORITY"
