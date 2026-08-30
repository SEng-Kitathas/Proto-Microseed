from scratch.ms1995_crossing_occlusion_reassociation import run_ms1995


def test_ms1995_crossing_occlusion_and_appearance_change_preserve_operational_reassociation_without_identity_guessing():
    result = run_ms1995()
    assert result["status"] == "BOUNDARY_CONFIRMED"
    assert result["new_core_mechanism_required"] == "NO"

    persistent = result["persistent"]
    replace_a = result["replace_a_unmarked"]
    replace_b = result["replace_b_unmarked"]
    perfect = result["perfect_copy_both"]
    aliased = result["aliased_post"]

    assert persistent["trace_status"] == {"A": "RETAINED", "B": "RETAINED"}
    assert replace_a["trace_status"] == {"A": "LOST", "B": "RETAINED"}
    assert replace_b["trace_status"] == {"A": "RETAINED", "B": "LOST"}
    assert perfect["trace_status"] == {"A": "RETAINED", "B": "RETAINED"}

    sig_a = persistent["sig_a"]
    sig_b = persistent["sig_b"]
    assert persistent["pre_groups_by_signature"][sig_a] == [0, 1]
    assert persistent["pre_groups_by_signature"][sig_b] == [2, 3]
    assert persistent["cross_groups_by_signature"][sig_a] == [0, 3]
    assert persistent["cross_groups_by_signature"][sig_b] == [1, 2]
    assert persistent["post_groups_by_signature"][sig_a] == [2, 3]
    assert persistent["post_groups_by_signature"][sig_b] == [0, 1]

    assert persistent["occlusion_nomination_status"] == "UNKNOWN_INCOMPLETE"
    assert persistent["post_reassociation"] == (
        "AFFORDANCE_SIGNATURE_MATCHED_AFTER_CROSSING_OCCLUSION_AND_APPEARANCE_CHANGE"
    )

    assert replace_a["trace_reapply_changed_positions"]["A"] == [2, 3]
    assert replace_a["trace_reapply_changed_positions"]["B"] == []
    assert replace_b["trace_reapply_changed_positions"]["A"] == []
    assert replace_b["trace_reapply_changed_positions"]["B"] == [0, 1]

    # Perfect-copy replacement preserves every organism-visible signature/trace result.
    for key in (
        "sig_a",
        "sig_b",
        "pre_groups_by_signature",
        "cross_groups_by_signature",
        "post_groups_by_signature",
        "trace_status",
    ):
        assert persistent[key] == perfect[key]
    assert persistent["evaluator_generations_before_gap"] == persistent["evaluator_generations_after_gap"]
    assert perfect["evaluator_generations_before_gap"] != perfect["evaluator_generations_after_gap"]

    # Symmetric/aliased action evidence must not be guessed through.
    assert aliased["post_reassociation"] == "UNKNOWN_INCOMPLETE"
    assert aliased["trace_test_status"] == "NOT_RUN_WITHOUT_UNIQUE_POST_REFERENT_PARTITION"
    assert aliased["post"]["nomination_status"] == "UNKNOWN_INCOMPLETE"

    assert result["crossing_authority"] == "OPERATIONAL_REASSOCIATION_ONLY"
    assert result["occlusion_authority"] == "DEFER_DURING_INSUFFICIENT_VISIBLE_PARTITION_EVIDENCE"
    assert result["ambiguous_evidence_policy"] == "UNKNOWN_INCOMPLETE_NO_GUESS"
    assert result["numerical_identity_authority"] == "NONE"
    assert result["semantic_reference_authority"] == "NONE"
    assert result["language_authority"] == "NONE"
