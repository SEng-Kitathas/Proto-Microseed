from pathlib import Path

from scratch.v1_soak_001_novel_world_long_horizon import SoakConfig, run_soak


def test_v1_soak_001_smoke_preserves_currentness_restart_and_referent_ambiguity_boundaries(tmp_path: Path):
    result = run_soak(
        SoakConfig(episodes=80, shift_episode=40, snapshot_every=20, referent_every=20, seed=2053001),
        tmp_path / "soak",
    )
    assert result["status"] == "PASS"
    assert result["unexpected_block_count"] == 0
    assert result["shift_drift_zero_row_pass_count"] == 16
    assert set(result["final_old_relation_status"].values()) == {"STALE_PREDICTIVE_RELATION"}
    assert set(result["final_replacement_relation_status"].values()) == {"CURRENT_PREDICTIVE_RELATION"}
    assert result["effect_capability_ids"] == ["K-17", "M-23", "R-41"]
    assert result["language_branch_mechanism_present"] == "NO"
    assert result["naked_branch_mechanism_present"] == "NO"
    assert result["semantic_reference_authority"] == "NONE"
    assert result["new_core_manager"] == "NO"
    assert result["restart_count"] >= 3
    assert result["referent_diagnostics"]
    assert any(row.get("class_count", 0) >= 6 for row in result["referent_diagnostics"])
