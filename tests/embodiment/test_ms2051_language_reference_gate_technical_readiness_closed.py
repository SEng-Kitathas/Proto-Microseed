from scratch.ms2048_language_reference_gate_technical_readiness_audit import run_ms2048


def test_ms2051_language_reference_gate_is_technically_ready_but_operator_controlled_and_still_closed():
    r = run_ms2048(True)
    assert r["status"] == "TECHNICALLY_READY_FOR_OPERATOR_LANGUAGE_GATE_REVIEW"
    assert r["language_facing_evidence"] == "GREEN"
    assert r["grounded_reference_candidate"] == "GROUNDED_OPERATIONAL_TOKEN_REFERENT_BINDING_CANDIDATE_EARNED"
    assert r["many_referent"] == "FOUR_REFERENT_PARTIAL_OBSERVABILITY_SCALE_EARNED"
    assert r["body_counterparty"] == "OPERATIONAL_BODY_COUNTERPARTY_BOUNDARY_EARNED"
    assert r["runtime_language_status"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
    assert r["historical_language_authority"] == "DONOR_ONLY_RESEARCH_ONLY"
    assert r["forbidden_language_manager_attrs_present"] == []
    assert r["semantic_reference_authority"] == "NONE"
    assert r["language_authority"] == "NONE"
    assert r["gate_authority"] == "OPERATOR_ONLY"
    assert r["law"] == "GROUNDING_CANDIDATE != LANGUAGE_GATE_ADMISSION"
