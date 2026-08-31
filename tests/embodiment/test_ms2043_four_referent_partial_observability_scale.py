from scratch.ms2043_four_referent_partial_observability_scale import run_ms2043


def test_ms2043_four_referent_crossing_occlusion_reassociation_scales_without_tracker():
    r = run_ms2043()
    assert r["status"] == "FOUR_REFERENT_PARTIAL_OBSERVABILITY_SCALE_EARNED"
    p = r["persist"]
    assert p["trace_status"] == {"A": "RETAINED", "B": "RETAINED", "C": "RETAINED", "D": "RETAINED"}
    assert p["occlude_ac_visible_labels"] == ["B", "D"]
    assert p["occlude_bd_visible_labels"] == ["A", "C"]
    assert r["replace_c_unmarked"]["trace_status"]["C"] == "LOST"
    assert r["replace_ac_unmarked"]["trace_status"] == {"A": "LOST", "B": "RETAINED", "C": "LOST", "D": "RETAINED"}
    assert r["perfect_copy_all"]["trace_status"] == p["trace_status"]
    assert r["new_tracker_required"] == "NO"
    assert r["numerical_identity_authority"] == "NONE"
    assert r["semantic_reference_authority"] == "NONE"
    assert r["language_authority"] == "NONE"


def test_ms2043_partial_alias_localizes_ambiguity_instead_of_forcing_four_way_identity():
    r = run_ms2043()
    x = r["alias_cd_post"]
    assert x["post_group_count"] == 3
    assert x["post_unambiguous_labels"] == ["A", "B"]
    assert x["localized_ambiguous_sources"] == ["C", "D"]
    assert x["ambiguous_group_size"] == 4
    assert x["trace_replay"] == "NOT_RUN_FOR_AMBIGUOUS_CD_PARTITION"
    assert r["earned"] == "AFFORDANCE_RELATIVE_REFERENT_PARTITIONING_SCALES_TO_FOUR_REFERENTS_UNDER_CROSSING_STAGGERED_OCCLUSION_AND_APPEARANCE_CHANGE_WHILE_LOCALIZING_AMBIGUITY_INSTEAD_OF_GUESSING"
