from pathlib import Path
import tempfile

from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import OpaqueTwoLocusWorld, _attach_runtime_surface, _close, _fresh_owned_relation
from scratch.lang_c08f_native_token_referent_binding import _pair_episode as _referent_pair_episode
from scratch.lang_c08h_owned_evidence_closure_qualification import _record_pair, run_campaign


def _mapping(qualification_bindings):
    return {str(left): str(right) for left, right in qualification_bindings}


def test_c08h_organism_owned_leave_one_out_qualification_closes_external_split_for_referent_and_relation_associations():
    result = run_campaign()
    assert result["status"] == "C08H_ORGANISM_OWNED_EPISTEMIC_ASSOCIATION_QUALIFICATION_EARNED"
    assert result["qualification_method"] == "LEAVE_ONE_OUT_EXACT_BIJECTIVE_EVIDENCE_CLOSURE"
    assert result["external_train_holdout_partition"] == "NONE"
    assert result["supplied_mapping_answer"] == "NONE"
    assert result["qualification_scope_selection"] == "AUTO_ENUMERATED_FROM_NATIVE_PAIR_WITNESSES"
    assert result["arbitrary_confidence_scalar"] == "NONE"
    assert result["minimum_support_threshold"] == "NONE__REDUNDANCY_IS_FORCED_BY_HELD_OUT_CLOSURE_ITSELF"
    assert result["referent_pair_witness_count"] == result["relation_pair_witness_count"] == 6
    assert result["qualification_survives_restart_as_epistemic_evidence"] == "YES"
    assert result["association_use_requires_fresh_grounded_currentness_after_restart"] == "YES"
    assert set(result["referent_restart_states"].values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
    assert set(result["relation_restart_states"].values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
    assert result["post_restart_referent_currentness"] == ["CURRENTNESS_CONFIRMED", "CURRENTNESS_CONFIRMED"]
    assert result["post_restart_relation_currentness"] == "CURRENTNESS_CONFIRMED"
    assert result["new_contradictory_pair_invalidates_prior_qualification"] == "REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION"
    assert result["contradictory_requalification"] == {"status": "DEFER_UNKNOWN", "reason": "PAIR_EVIDENCE_NOT_EXACT_BIJECTION"}
    assert set(result["invalidated_record_states"].values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
    assert result["qualification_authority"] == "EPISTEMIC_ADEQUACY_EVIDENCE_ONLY"
    assert result["effect_authority"] == result["truth_authority"] == result["semantic_authority"] == result["language_authority"] == "NONE"
    assert "GENERIC_CONFIDENCE_FACULTY" in result["not_earned"]
    assert "ENDOGENOUS_EXPERIMENT_GENERATION" in result["not_earned"]


def test_c08h_single_observation_per_mapping_fails_by_leave_one_out_closure_not_by_confidence_threshold():
    with tempfile.TemporaryDirectory(prefix="lang-c08h-singleton-") as td:
        world = OpaqueTwoLocusWorld()
        ms = Microseed(Path(td))
        try:
            _attach_runtime_surface(ms, world, "C08H-SINGLETON")
            _fresh_owned_relation(ms, world, tag="C08H-SINGLETON-SEED", serial_base=0)
            pair_x = _referent_pair_episode(ms, world, tag="SINGLE-X", locus="X", token="R4", index=0, phase="SINGLE")
            pair_y = _referent_pair_episode(ms, world, tag="SINGLE-Y", locus="Y", token="T9", index=1, phase="SINGLE")
            _record_pair(ms, pair_x["pair_evidence_id"])
            _record_pair(ms, pair_y["pair_evidence_id"])
            result = ms.derive_opaque_evidence_association_qualification(association_scope="NATIVE_TOKEN_REFERENT")
            assert result["status"] == "DEFER_UNKNOWN"
            assert result["reason"] == "LEAVE_ONE_OUT_ASSOCIATION_CLOSURE_FAILED"
            assert "confidence" not in str(result).lower()
            assert result["effect_authority"] == result["semantic_authority"] == result["language_authority"] == "NONE"
        finally:
            _close(ms)


def test_c08h_token_surface_permutation_swaps_only_empirical_left_labels_not_grounded_right_structure():
    base = run_campaign(token_x="R4", token_y="T9", relation_normal_token="K7", relation_reverse_token="M2")
    swapped = run_campaign(token_x="T9", token_y="R4", relation_normal_token="M2", relation_reverse_token="K7")
    base_ref = _mapping(base["referent_bindings"])
    swap_ref = _mapping(swapped["referent_bindings"])
    base_rel = _mapping(base["relation_bindings"])
    swap_rel = _mapping(swapped["relation_bindings"])
    assert set(base_ref.values()) == set(swap_ref.values())
    assert set(base_rel.values()) == set(swap_rel.values())
    assert base_ref["R4"] == swap_ref["T9"]
    assert base_ref["T9"] == swap_ref["R4"]
    assert base_rel["K7"] == swap_rel["M2"]
    assert base_rel["M2"] == swap_rel["K7"]


def test_c08h_sensor_representation_transformations_preserve_owned_qualification_structure():
    base = run_campaign()
    permuted = run_campaign(sensor_transform=lambda row: (row[2], row[3], row[0], row[1]))
    inverted = run_campaign(sensor_transform=lambda row: tuple(-x for x in row))
    assert _mapping(base["referent_bindings"]) == _mapping(permuted["referent_bindings"]) == _mapping(inverted["referent_bindings"])
    assert _mapping(base["relation_bindings"]) == _mapping(permuted["relation_bindings"]) == _mapping(inverted["relation_bindings"])
    assert base["qualification_method"] == permuted["qualification_method"] == inverted["qualification_method"]
    assert base["external_train_holdout_partition"] == permuted["external_train_holdout_partition"] == inverted["external_train_holdout_partition"] == "NONE"
