from scratch.ms1994_multiple_trace_persistence_conflict import run_ms1994


def test_ms1994_multiple_traces_preserve_topology_and_mixed_evidence_without_identity_promotion():
    result = run_ms1994()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["new_core_mechanism_required"] == "NO"

    persistent = result["persistent"]
    unmarked = result["unmarked_replacement"]
    partial = result["partial_copy_replacement"]
    perfect = result["perfect_copy_replacement"]
    nuisance = result["nuisance_replacement"]
    persistent_nuisance = result["persistent_with_unrelated_nuisance"]

    assert persistent["retained_trace_topology"] == ["A1", "A2"]
    assert persistent["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert persistent["evaluator_persistence"] is True

    assert unmarked["retained_trace_topology"] == []
    assert unmarked["operational_persistence_support"] == "REFUTED_FOR_ALL_OBSERVED_TRACES"
    assert unmarked["evaluator_persistence"] is False

    assert partial["retained_trace_topology"] == ["A1"]
    assert partial["per_trace_status"] == {"A1": "RETAINED", "A2": "LOST"}
    assert partial["operational_persistence_support"] == "MIXED_TRACE_EVIDENCE"
    assert partial["evaluator_persistence"] is False

    assert perfect["retained_trace_topology"] == ["A1", "A2"]
    assert perfect["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert perfect["evaluator_persistence"] is False

    assert nuisance["retained_trace_topology"] == []
    assert nuisance["nuisance_changed"] is True
    assert nuisance["operational_persistence_support"] == "REFUTED_FOR_ALL_OBSERVED_TRACES"
    assert nuisance["evaluator_persistence"] is False

    assert persistent_nuisance["retained_trace_topology"] == ["A1", "A2"]
    assert persistent_nuisance["nuisance_changed"] is True
    assert persistent_nuisance["operational_persistence_support"] == "SUPPORTED_BY_ALL_OBSERVED_TRACES"
    assert persistent_nuisance["evaluator_persistence"] is True

    signatures = {
        row["target_signature"]
        for row in (persistent, unmarked, partial, perfect, nuisance, persistent_nuisance)
    }
    assert len(signatures) == 1
    for row in (persistent, unmarked, partial, perfect, nuisance, persistent_nuisance):
        assert row["target_group"] == [0, 1]
        assert row["nuisance_group"] == [2, 3]
        assert row["numerical_identity_authority"] == "NONE"
        assert row["semantic_reference_authority"] == "NONE"
        assert row["language_authority"] == "NONE"

    assert result["operational_persistence_authority"] == "TRACE_TOPOLOGY_RELATIVE_ONLY"
    assert result["partial_conflict_policy"] == "PRESERVE_MIXED_EVIDENCE_NO_MAJORITY_COLLAPSE"
    assert result["remaining_boundary"] == (
        "PERFECT_COPY_WITH_ALL_RETAINED_TRACES_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE"
    )
    assert result["numerical_identity_authority"] == "NONE"
    assert result["semantic_reference_authority"] == "NONE"
    assert result["language_authority"] == "NONE"
