from scratch.frontier_e_identity_developmental_history import run_frontier_e_developmental_history


def test_matched_current_surface_can_retain_different_authenticated_developmental_history_without_identity_primitive():
    r = run_frontier_e_developmental_history()
    assert r["status"] == "PASS"
    assert r["current_surface_equal"] is True
    assert r["historyful"]["step_count"] == 2
    assert r["historyful"]["opaque_action_sequence"] == ["P0", "P1"]
    assert r["fresh_current"]["step_count"] == 0
    assert r["fresh_current"]["opaque_action_sequence"] == []
    assert r["historyful"]["raw_samples"][-1] == r["fresh_current"]["raw_samples"][-1]
    assert r["identity_primitive_added"] == "NO"
    assert r["caller_supplied_history_label"] == "NO"


def test_developmental_history_difference_is_read_only_and_does_not_promote_identity_or_execution_authority():
    r = run_frontier_e_developmental_history()
    assert r["history_sensitive_read_only_difference"] is True
    assert r["numerical_identity_required"] == "NOT_SHOWN"
    for key in (
        "semantic_coordinate_authority",
        "semantic_referent_authority",
        "truth_authority",
        "selection_authority",
        "execution_authority",
    ):
        assert r[key] == "NONE"
    assert "DOES_NOT_ESTABLISH_NUMERICAL_IDENTITY_OR_SELFHOOD" in r["claim_ceiling"]


def test_current_surface_equality_excludes_history_database_size_and_evidence_ids_from_the_match_contract():
    r = run_frontier_e_developmental_history()
    surface = r["current_surface"]
    assert set(surface) == {
        "control_state_id",
        "control_state_authority",
        "capability_epochs",
        "frame_epochs",
        "episode_epochs",
        "value_snapshot",
        "current_raw_sample",
    }
    assert surface["control_state_id"] == "s2"
    assert surface["current_raw_sample"] == ["1", "1", "1", "1"]
    assert "evidence_id" not in surface
    assert "identity" not in str(surface).lower()
