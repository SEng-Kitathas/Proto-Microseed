from pathlib import Path

from scratch.v1_soak_001_novel_world_long_horizon import SoakConfig, run_soak


def test_v1_soak_001_smoke_localizes_terminal_drift_and_recovers_without_global_reset(tmp_path: Path):
    result = run_soak(
        SoakConfig(episodes=80, shift_episode=40, snapshot_every=20, referent_every=20, seed=2053001),
        tmp_path / "soak",
    )
    assert result["status"] == "PASS"
    assert result["shift_drift_episode_pass_count"] == 16
    assert result["final_old_relation_status"] == {
        "K-17": "CURRENT_PREDICTIVE_RELATION",
        "M-23": "CURRENT_PREDICTIVE_RELATION",
        "R-41": "STALE_PREDICTIVE_RELATION",
    }
    assert result["final_active_relation_status"] == {
        "K-17": "CURRENT_PREDICTIVE_RELATION",
        "M-23": "CURRENT_PREDICTIVE_RELATION",
        "R-41": "CURRENT_PREDICTIVE_RELATION",
    }
    assert set(result["final_active_proposal_status"].values()) == {"CURRENT_REHEARSAL_PROPOSAL"}
    assert result["effect_capability_ids"] == ["K-17", "M-23", "R-41"]
    assert result["language_branch_mechanism_present"] == "NO"
    assert result["naked_branch_mechanism_present"] == "NO"
    assert result["semantic_reference_authority"] == "NONE"
    assert result["new_core_manager"] == "NO"
    assert result["restart_count"] >= 3
    assert result["referent_diagnostics"]
    assert any(row.get("class_count", 0) >= 6 for row in result["referent_diagnostics"])
