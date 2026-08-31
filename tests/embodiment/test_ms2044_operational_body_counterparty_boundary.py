from scratch.ms2044_operational_body_counterparty_boundary import run_ms2044


def test_ms2044_asymmetric_coupling_break_supports_bounded_operational_body_relation():
    r = run_ms2044()
    assert r["status"] == "OPERATIONAL_BODY_COUNTERPARTY_BOUNDARY_EARNED"
    n = r["normal"]
    assert n["operational_roles_by_evaluator_source_for_test_only"]["B"] == "EFFERENCE_CONTINGENT_OPERATIONAL_BODY_RELATION"
    assert n["operational_roles_by_evaluator_source_for_test_only"]["T"] == "OTHER_OR_PARTIALLY_COUPLED_OPERATIONAL_RELATION"
    assert n["operational_roles_by_evaluator_source_for_test_only"]["C"] == "INDEPENDENTLY_CHANGING_OPERATIONAL_COUNTERPARTY_LIKE_RELATION"
    assert n["owned_effect_ids"] == ["FX-DETACH", "FX-MOVE"]
    assert r["new_self_or_body_manager_required"] == "NO"
    assert r["semantic_self_authority"] == "NONE"
    assert r["language_authority"] == "NONE"


def test_ms2044_perfect_coupling_blocks_body_vs_tool_identity():
    r = run_ms2044()
    x = r["perfect_coupling_hostile"]
    assert x["status"] == "PASS_SYMMETRY_BLOCK"
    assert x["merged_sources_for_test_only"] == ["B", "T"]
    assert len(x["merged_group"]) == 4
    assert x["body_vs_tool_identity"] == "UNIDENTIFIABLE_FROM_LOCAL_EFFERENCE_STRUCTURE_ALONE"
    assert x["required_breaker"] == "ASYMMETRIC_COUPLING_OR_ADDITIONAL_CONTINUITY_EVIDENCE"
    assert x["semantic_self_authority"] == "NONE"
    assert x["numerical_body_identity_authority"] == "NONE"
    assert r["symmetry_law"] == "PERFECT_COUPLING_SYMMETRY_BLOCKS_BODY_VS_TOOL_IDENTITY"
