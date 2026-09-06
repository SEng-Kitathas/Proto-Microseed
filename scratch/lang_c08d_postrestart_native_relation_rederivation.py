from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority,
    EpisodeSchemaContract,
    Microseed,
    OperationalFrameContract,
    Observation,
    QualificationState,
    ValueVariableContract,
)
from scratch.lang_c08c_native_owned_affordance_relation import (
    OpaqueTwoLocusWorld,
    _attach_body,
    _execute,
    _external_control_state,
    _raw,
)


EXPECTED_BODY_CAPABILITIES = {
    "QX",
    "QY",
    "C08C-OBS-RAW",
    "C08C-OBS-BASIS",
}


def _close(ms: Microseed) -> None:
    ms.biography.close()
    ms.evidence.conn.close()
    ms.store.conn.close()


def _observe_action_state_s0(ms: Microseed, tag: str) -> dict[str, object]:
    result = ms.observe_opaque_control_state(
        Observation(
            f"CAP-C08D-S0-{tag}",
            "EXTERNAL-WORLD",
            "opaque-control-state",
            "s0",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-C08D-S0-{tag}",
    )
    assert result["status"] == "CURRENT_OPAQUE_CONTROL_STATE", result
    return result


def _attach_runtime_surface(ms: Microseed, world: OpaqueTwoLocusWorld, tag: str) -> dict[str, object]:
    """Explicitly reattach the supplied low-level body/runtime interface.

    This is body provision, not learned cognition. No durable event is interpreted as
    permission to recreate handlers. The same bounded interface is supplied anew to the
    restarted process, after which fresh organism-owned evidence is still required.
    """
    assert not EXPECTED_BODY_CAPABILITIES.intersection(ms.capabilities.contracts), ms.capabilities.contracts
    assert "F" not in ms.frames.frames
    assert "V" not in ms.values.contracts
    assert "EP" not in ms.episodes.schemas

    ms.register_operational_frame(
        OperationalFrameContract(
            "F",
            "opaque",
            "f" * 64,
            Authority.DERIVED_READ_ONLY,
            ("C08D-SUPPLIED-BODY",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
        )
    )
    ms.register_value_variable(
        ValueVariableContract(
            "V",
            "reg",
            0,
            10,
            "v" * 64,
            Authority.REFERENCE_ONLY,
            ("C08D-SUPPLIED-BODY",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
        )
    )
    ms.observe_value_state("V", -1.0)
    ms.register_episode_schema(
        EpisodeSchemaContract(
            "EP",
            "opaque-episode",
            "e" * 64,
            Authority.DERIVED_READ_ONLY,
            ("C08D-SUPPLIED-BODY",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            frame_epochs=(("F", 0),),
            value_epochs=(("V", 0),),
        )
    )
    _attach_body(ms, world)
    _observe_action_state_s0(ms, f"{tag}-ATTACH")
    return {
        "status": "SUPPLIED_LOW_LEVEL_BODY_INTERFACE_ATTACHED",
        "body_capability_ids": sorted(EXPECTED_BODY_CAPABILITIES),
        "frame_epoch": ["F", ms.frames.epochs["F"]],
        "value_epoch": ["V", ms.values.epochs["V"]],
        "episode_epoch": ["EP", ms.episodes.epochs["EP"]],
        "execution_authority_from_history": "NONE",
        "relation_answer_supplied": "NO",
        "referent_structure_supplied": "NO",
    }


def _fresh_owned_relation(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    tag: str,
    serial_base: int,
) -> dict[str, object]:
    world.set_passive_baseline(0, 0)
    _observe_action_state_s0(ms, f"{tag}-TRAIN-START")
    _raw(ms, f"{tag}-P0")
    sequence = (("QX", "X0"), ("QX", "X1"), ("QY", "Y0"), ("QY", "Y1"))
    for offset, (cid, step) in enumerate(sequence):
        _execute(ms, cid, f"{tag}-{step}", serial_base + offset)
        _raw(ms, f"{tag}-P{offset + 1}")

    profiles = ms.record_current_owned_affordance_effect_profiles(
        evidence_id_prefix=f"E-C08D-{tag}-PROFILE",
        max_probe_steps=4,
    )
    assert profiles["status"] == "CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED", profiles
    assert profiles["profile_count"] == 2, profiles

    world.set_passive_baseline(2, 1)
    _external_control_state(ms, f"{tag}-PASSIVE-PRE")
    _raw(ms, f"{tag}-PASSIVE-PRE")
    world.apply_passive_xy_to_yx()
    _external_control_state(ms, f"{tag}-PASSIVE-POST")
    _raw(ms, f"{tag}-PASSIVE-POST")

    relation = ms.derive_and_record_current_owned_affordance_relative_directional_relation(
        evidence_id=f"E-C08D-{tag}-RELATION",
        max_events=8192,
        max_records=8192,
    )
    assert relation["status"] == "CURRENT_OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_RECORDED", relation
    assert relation["caller_supplied_relation_order"] == "NO"
    assert relation["caller_supplied_relation_digest"] == "NO"
    assert relation["coordinate_arithmetic"] == "NONE"
    boot_seq = ms._current_runtime_boot_seq()
    assert relation["runtime_boot_seq"] == boot_seq
    assert all(p["runtime_boot_seq"] == boot_seq for p in profiles["profiles"])
    return {"profiles": profiles, "relation": relation, "runtime_boot_seq": boot_seq}


def run_campaign(sensor_transform=None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08d-postrestart-native-") as td:
        state_dir = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform

        ms1 = Microseed(state_dir)
        try:
            attach1 = _attach_runtime_surface(ms1, world, "R1")
            first = _fresh_owned_relation(ms1, world, tag="R1", serial_base=0)
            relation1 = first["relation"]
            rel1_row = ms1.evidence.get(relation1["evidence_id"])
            assert rel1_row is not None
            assoc = ms1.register_opaque_evidence_association(
                left_opaque_id="C08D-OPAQUE-RELATION-HANDLE",
                right_digest_sha256=relation1["relation_digest_sha256"],
                source_evidence_refs=((relation1["evidence_id"], rel1_row["sha256"]),),
                assistance_ancestry=(
                    "INITIAL_NATIVE_RELATION_EVIDENCE",
                    "SUPPLIED_LOW_LEVEL_BODY_INTERFACE_ONLY",
                    "NO_HARNESS_RELATION_DIGEST",
                ),
            )
            live1 = ms1.assess_opaque_evidence_association_currentness(
                assoc["record_id"], witness_evidence_id=relation1["evidence_id"]
            )
            assert live1["status"] == "CURRENTNESS_CONFIRMED", live1
            assert live1["record_state"] == "CURRENT"
            boot1 = first["runtime_boot_seq"]
            rel1_digest = relation1["relation_digest_sha256"]
            rel1_evidence_id = relation1["evidence_id"]
        finally:
            _close(ms1)

        # Restart: history replays, executable body contracts/handlers do not.
        ms2 = Microseed(state_dir)
        try:
            boot2 = ms2._current_runtime_boot_seq()
            assert boot2 > boot1, (boot1, boot2)
            body_before_reattach = sorted(EXPECTED_BODY_CAPABILITIES.intersection(ms2.capabilities.contracts))
            assert body_before_reattach == [], body_before_reattach
            assert "F" not in ms2.frames.frames
            assert "V" not in ms2.values.contracts
            assert "EP" not in ms2.episodes.schemas

            assoc_after_restart = ms2.opaque_evidence_association_status(assoc["record_id"])
            assert assoc_after_restart["status"] == "REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION", assoc_after_restart

            # Historical native relation evidence is evidence, not fresh currentness.
            historical_witness = ms2.assess_opaque_evidence_association_currentness(
                assoc["record_id"], witness_evidence_id=rel1_evidence_id
            )
            assert historical_witness["status"] == "UNKNOWN_INCOMPLETE", historical_witness
            assert historical_witness["reason"] == "FRESH_CURRENT_RUNTIME_OWNED_RELATION_WITNESS_REQUIRED"

            pre_reattach_relation = ms2.derive_and_record_current_owned_affordance_relative_directional_relation(
                evidence_id="E-C08D-PRE-REATTACH-RELATION",
                max_events=8192,
                max_records=8192,
            )
            assert pre_reattach_relation["status"] == "DEFER_UNKNOWN", pre_reattach_relation

            attach2 = _attach_runtime_surface(ms2, world, "R2")
            assert set(ms2.capabilities.contracts) == EXPECTED_BODY_CAPABILITIES, sorted(ms2.capabilities.contracts)

            # Reattaching the same body still does not make pre-restart experience fresh.
            old_prefix_after_reattach = ms2.record_current_owned_affordance_effect_profiles(
                evidence_id_prefix="E-C08D-REATTACHED-BUT-NOT-FRESH",
                max_probe_steps=4,
            )
            assert old_prefix_after_reattach["status"] == "DEFER_UNKNOWN", old_prefix_after_reattach
            assert old_prefix_after_reattach["reason"] in {
                "FRESH_POST_BOOT_RAW_PROBE_EVIDENCE_REQUIRED",
                "FRESH_POST_BOOT_ACTION_EXECUTION_REQUIRED",
                "CURRENT_OWNED_PROBE_PREFIX_REQUIRED",
            }, old_prefix_after_reattach

            # Fresh post-restart lived interaction must rebuild the grounded relation.
            second = _fresh_owned_relation(ms2, world, tag="R2", serial_base=100)
            relation2 = second["relation"]
            assert second["runtime_boot_seq"] == boot2
            assert relation2["relation_digest_sha256"] == rel1_digest, (rel1_digest, relation2)
            assert relation2["evidence_id"] != rel1_evidence_id
            assert relation2["runtime_boot_seq"] != boot1

            revalidated = ms2.assess_opaque_evidence_association_currentness(
                assoc["record_id"], witness_evidence_id=relation2["evidence_id"]
            )
            assert revalidated["status"] == "CURRENTNESS_CONFIRMED", revalidated
            assert revalidated["record_state"] == "CURRENT"

            # Fresh empirical reversal still stales the same association.
            world.set_passive_baseline(1, 2)
            _external_control_state(ms2, "R2-REVERSE-PRE")
            _raw(ms2, "R2-REVERSE-PRE")
            world.apply_passive_xy_to_yx()
            _external_control_state(ms2, "R2-REVERSE-POST")
            _raw(ms2, "R2-REVERSE-POST")
            reversed_relation = ms2.derive_and_record_current_owned_affordance_relative_directional_relation(
                evidence_id="E-C08D-R2-REVERSED-RELATION",
                max_events=8192,
                max_records=8192,
            )
            assert reversed_relation["status"] == "CURRENT_OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_RECORDED", reversed_relation
            assert reversed_relation["relation_digest_sha256"] != rel1_digest
            drift = ms2.assess_opaque_evidence_association_currentness(
                assoc["record_id"], witness_evidence_id=reversed_relation["evidence_id"]
            )
            assert drift["status"] == "DRIFT_WITNESS", drift
            assert drift["record_state"] == "STALE"

            return {
                "status": "C08D_POST_RESTART_NATIVE_RELATION_REDERIVATION_EARNED",
                "first_runtime_boot_seq": boot1,
                "second_runtime_boot_seq": boot2,
                "body_capabilities_before_reattach": body_before_reattach,
                "first_attachment": attach1,
                "second_attachment": attach2,
                "association_after_restart": assoc_after_restart["status"],
                "historical_relation_witness_after_restart": {
                    "status": historical_witness["status"],
                    "reason": historical_witness["reason"],
                },
                "reattached_without_fresh_evidence": {
                    "status": old_prefix_after_reattach["status"],
                    "reason": old_prefix_after_reattach["reason"],
                },
                "relation_digest_before_restart": rel1_digest,
                "relation_digest_after_fresh_restart_evidence": relation2["relation_digest_sha256"],
                "relation_digest_stable_across_restart": relation2["relation_digest_sha256"] == rel1_digest,
                "fresh_relation_evidence_id": relation2["evidence_id"],
                "fresh_relation_runtime_boot_seq": relation2["runtime_boot_seq"],
                "post_restart_revalidation": revalidated["status"],
                "reversed_relation_digest_sha256": reversed_relation["relation_digest_sha256"],
                "empirical_reversal": drift["status"],
                "durable_history_reauthorized_body": "NO",
                "body_reattachment": "EXPLICIT_SUPPLIED_LOW_LEVEL_BODY_INTERFACE",
                "fresh_post_restart_organism_owned_evidence_required": "YES",
                "caller_supplied_referent_groups": "NO",
                "caller_supplied_relation_order": "NO",
                "caller_supplied_relation_digest": "NO",
                "coordinate_arithmetic": "NONE",
                "semantic_authority": "NONE",
                "truth_authority": "NONE",
                "execution_authority_from_history": "NONE",
                "language_authority": "NONE",
                "not_earned": [
                    "C07_TOKEN_BINDING_REEMBODIMENT",
                    "SEMANTIC_PREDICATE",
                    "TOKEN_MEANING",
                    "LANGUAGE_FACULTY",
                    "GENERIC_CAPABILITY_FACULTY",
                    "CANON_PROMOTION",
                ],
            }
        finally:
            _close(ms2)


def main() -> None:
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
