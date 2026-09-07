from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld,
    _attach_runtime_surface,
    _close,
    _fresh_owned_relation,
)
from scratch.lang_c08e_native_token_relation_binding import _pair_episode as _relation_pair_episode
from scratch.lang_c08f_native_token_referent_binding import (
    _fresh_profiles,
    _pair_episode as _referent_pair_episode,
)


def _record_pair(ms: Microseed, pair_evidence_id: str) -> dict[str, object]:
    result = ms.record_opaque_evidence_association_pair_witness(pair_evidence_id=pair_evidence_id)
    assert result["status"] == "OPAQUE_ASSOCIATION_PAIR_WITNESS_RECORDED", result
    assert result["truth_authority"] == result["semantic_authority"] == "NONE"
    assert result["execution_authority"] == result["language_authority"] == "NONE"
    return result


def _referent_pairs(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    token_x: str,
    token_y: str,
    phase: str,
    count: int,
    index_base: int,
) -> tuple[list[str], dict[str, dict[str, object]]]:
    pair_ids: list[str] = []
    for i in range(count):
        locus = "X" if i % 2 == 0 else "Y"
        token = token_x if locus == "X" else token_y
        pair = _referent_pair_episode(
            ms,
            world,
            tag=f"{phase}-{i}",
            locus=locus,
            token=token,
            index=index_base + i,
            phase=phase,
        )
        _record_pair(ms, pair["pair_evidence_id"])
        pair_ids.append(pair["pair_evidence_id"])
    return pair_ids, {}


def _relation_pairs(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    token_normal: str,
    token_reverse: str,
    phase: str,
    count: int,
    index_base: int,
) -> list[str]:
    pair_ids: list[str] = []
    for i in range(count):
        reverse = bool(i % 2)
        token = token_reverse if reverse else token_normal
        pair = _relation_pair_episode(
            ms,
            world,
            tag=f"{phase}-{i}",
            reverse=reverse,
            token=token,
            index=index_base + i,
            phase=phase,
        )
        _record_pair(ms, pair["pair_evidence_id"])
        pair_ids.append(pair["pair_evidence_id"])
    return pair_ids


def _mapping_from_qualification(result: dict[str, object]) -> dict[str, str]:
    qualification = result["qualification"]
    return {str(left): str(right) for left, right in qualification["bindings"]}


def run_campaign(
    token_x: str = "R4",
    token_y: str = "T9",
    relation_normal_token: str = "K7",
    relation_reverse_token: str = "M2",
    sensor_transform=None,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08h-owned-qualification-") as td:
        root = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform

        ms1 = Microseed(root)
        try:
            _attach_runtime_surface(ms1, world, "C08H-R1")
            shared_seed = _fresh_owned_relation(ms1, world, tag="C08H-SHARED-SEED", serial_base=0)
            referent_profiles = shared_seed["profiles"]
            relation_seed = shared_seed
            ref_by_action = {p["exclusive_action_id"]: p for p in referent_profiles["profiles"]}
            sig_x = str(ref_by_action["QX"]["operational_referent_signature_sha256"])
            sig_y = str(ref_by_action["QY"]["operational_referent_signature_sha256"])

            # No TRAIN/HOLD labels or externally supplied mapping. These are simply repeated lived pair observations.
            referent_pair_ids, _ = _referent_pairs(
                ms1,
                world,
                token_x=token_x,
                token_y=token_y,
                phase="REF-PAIR",
                count=6,
                index_base=0,
            )
            # Native relation currentness was earned by the same shared seed; do not duplicate equivalent current profiles.
            normal_digest = str(relation_seed["relation"]["relation_digest_sha256"])
            relation_pair_ids = _relation_pairs(
                ms1,
                world,
                token_normal=relation_normal_token,
                token_reverse=relation_reverse_token,
                phase="REL-PAIR",
                count=6,
                index_base=100,
            )

            # The organism enumerates every pair-evidence scope it currently owns; the caller supplies no scope selector.
            all_q = ms1.derive_all_opaque_evidence_association_qualifications()
            assert all_q["status"] == "ALL_OWNED_OPAQUE_ASSOCIATION_SCOPES_EPISTEMICALLY_QUALIFIED", all_q
            assert all_q["scope_selection"] == "AUTO_ENUMERATED_FROM_NATIVE_PAIR_WITNESSES"
            assert set(all_q["scopes"]) == {"NATIVE_TOKEN_REFERENT", "NATIVE_TOKEN_RELATION"}
            assert all_q["external_train_holdout_partition"] == "NONE"
            assert all_q["supplied_mapping_answer"] == "NONE"
            ref_q = all_q["results"]["NATIVE_TOKEN_REFERENT"]
            rel_q = all_q["results"]["NATIVE_TOKEN_RELATION"]

            ref_map = _mapping_from_qualification(ref_q)
            assert ref_map == {token_x: sig_x, token_y: sig_y}, (ref_map, sig_x, sig_y)
            ref_qid = str(ref_q["qualification"]["qualification_id"])
            ref_registered = ms1.register_qualified_opaque_evidence_associations(qualification_id=ref_qid)
            assert ref_registered["status"] == "QUALIFIED_OPAQUE_EVIDENCE_ASSOCIATIONS_REGISTERED", ref_registered
            assert len(ref_registered["records"]) == 2

            rel_map = _mapping_from_qualification(rel_q)
            assert rel_map[relation_normal_token] == normal_digest
            assert rel_map[relation_reverse_token] != normal_digest
            reverse_digest = rel_map[relation_reverse_token]
            rel_qid = str(rel_q["qualification"]["qualification_id"])
            rel_registered = ms1.register_qualified_opaque_evidence_associations(qualification_id=rel_qid)
            assert rel_registered["status"] == "QUALIFIED_OPAQUE_EVIDENCE_ASSOCIATIONS_REGISTERED", rel_registered
            assert len(rel_registered["records"]) == 2

            # Current qualified associations can be confirmed only by grounded currentness witnesses.
            ref_records = {rec["left_opaque_id"]: rec["record_id"] for rec in ref_registered["records"]}
            ref_x_current = ms1.assess_opaque_evidence_association_currentness(
                ref_records[token_x], witness_evidence_id=str(ref_by_action["QX"]["evidence_id"])
            )
            ref_y_current = ms1.assess_opaque_evidence_association_currentness(
                ref_records[token_y], witness_evidence_id=str(ref_by_action["QY"]["evidence_id"])
            )
            assert ref_x_current["status"] == ref_y_current["status"] == "CURRENTNESS_CONFIRMED"

            rel_records = {rec["left_opaque_id"]: rec["record_id"] for rec in rel_registered["records"]}
            # Find one exact current relation witness for each qualified digest from the pair evidence ancestry.
            relation_witness_by_digest: dict[str, str] = {normal_digest: str(relation_seed["relation"]["evidence_id"])}
            for pair_id in relation_pair_ids:
                pair_row = ms1.evidence.get(pair_id)
                assert pair_row is not None
                pair_payload = pair_row["payload"]
                relation_ref = pair_payload["relation_evidence_ref"]
                relation_row = ms1.evidence.get(str(relation_ref[0]))
                assert relation_row is not None
                relation_witness_by_digest[str(pair_payload["relation_digest_sha256"])] = str(relation_ref[0])
            rel_normal_current = ms1.assess_opaque_evidence_association_currentness(
                rel_records[relation_normal_token], witness_evidence_id=relation_witness_by_digest[normal_digest]
            )
            rel_reverse_current = ms1.assess_opaque_evidence_association_currentness(
                rel_records[relation_reverse_token], witness_evidence_id=relation_witness_by_digest[reverse_digest]
            )
            assert rel_normal_current["status"] == rel_reverse_current["status"] == "CURRENTNESS_CONFIRMED"

            action_ids_before_restart = set(ms1.capabilities.contracts)
            assert not any("QUAL" in cid or "TOKEN" in cid or "LANG" in cid for cid in action_ids_before_restart)
        finally:
            _close(ms1)

        # Restart: adequacy evidence survives; executable body and grounded currentness do not self-restore.
        ms2 = Microseed(root)
        try:
            assert ms2.opaque_evidence_association_qualification_status(ref_qid)["status"] == "CURRENT_EPISTEMIC_ASSOCIATION_ADEQUACY"
            assert ms2.opaque_evidence_association_qualification_status(rel_qid)["status"] == "CURRENT_EPISTEMIC_ASSOCIATION_ADEQUACY"
            ref_restart_states = {rid: ms2.opaque_evidence_association_status(rid)["status"] for rid in ref_records.values()}
            rel_restart_states = {rid: ms2.opaque_evidence_association_status(rid)["status"] for rid in rel_records.values()}
            assert set(ref_restart_states.values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
            assert set(rel_restart_states.values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}

            _attach_runtime_surface(ms2, world, "C08H-R2")
            restarted = _fresh_owned_relation(ms2, world, tag="C08H-R2-SEED", serial_base=3000)
            ref_profiles2 = {p["exclusive_action_id"]: p for p in restarted["profiles"]["profiles"]}
            assert str(ref_profiles2["QX"]["operational_referent_signature_sha256"]) == sig_x
            assert str(ref_profiles2["QY"]["operational_referent_signature_sha256"]) == sig_y
            ref_x_restart = ms2.assess_opaque_evidence_association_currentness(
                ref_records[token_x], witness_evidence_id=str(ref_profiles2["QX"]["evidence_id"])
            )
            ref_y_restart = ms2.assess_opaque_evidence_association_currentness(
                ref_records[token_y], witness_evidence_id=str(ref_profiles2["QY"]["evidence_id"])
            )
            assert ref_x_restart["status"] == ref_y_restart["status"] == "CURRENTNESS_CONFIRMED"
            rel_normal_restart = ms2.assess_opaque_evidence_association_currentness(
                rel_records[relation_normal_token], witness_evidence_id=str(restarted["relation"]["evidence_id"])
            )
            assert rel_normal_restart["status"] == "CURRENTNESS_CONFIRMED"

            # New contradictory lived pair evidence invalidates the old qualification and all records from it.
            contradiction = _referent_pair_episode(
                ms2,
                world,
                tag="C08H-CONTRADICTION",
                locus="X",
                token=token_y,
                index=900,
                phase="CONTRADICTION",
            )
            contradiction_witness = _record_pair(ms2, contradiction["pair_evidence_id"])
            assert set(contradiction_witness["invalidated_qualified_record_ids"]) == set(ref_records.values())
            old_ref_q_after_contradiction = ms2.opaque_evidence_association_qualification_status(ref_qid)
            assert old_ref_q_after_contradiction["status"] == "REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION"
            requalify = ms2.derive_opaque_evidence_association_qualification(association_scope="NATIVE_TOKEN_REFERENT")
            assert requalify["status"] == "DEFER_UNKNOWN"
            assert requalify["reason"] == "PAIR_EVIDENCE_NOT_EXACT_BIJECTION"
            invalidated_states = {rid: ms2.opaque_evidence_association_status(rid)["status"] for rid in ref_records.values()}
            assert set(invalidated_states.values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}

            return {
                "status": "C08H_ORGANISM_OWNED_EPISTEMIC_ASSOCIATION_QUALIFICATION_EARNED",
                "technical_name": "Native leave-one-out exact evidence-closure qualification for opaque operational associations",
                "referent_qualification_id": ref_qid,
                "relation_qualification_id": rel_qid,
                "referent_bindings": ref_q["qualification"]["bindings"],
                "relation_bindings": rel_q["qualification"]["bindings"],
                "referent_pair_witness_count": len(referent_pair_ids),
                "relation_pair_witness_count": len(relation_pair_ids),
                "qualification_method": "LEAVE_ONE_OUT_EXACT_BIJECTIVE_EVIDENCE_CLOSURE",
                "external_train_holdout_partition": "NONE",
                "supplied_mapping_answer": "NONE",
                "qualification_scope_selection": "AUTO_ENUMERATED_FROM_NATIVE_PAIR_WITNESSES",
                "arbitrary_confidence_scalar": "NONE",
                "minimum_support_threshold": "NONE__REDUNDANCY_IS_FORCED_BY_HELD_OUT_CLOSURE_ITSELF",
                "qualification_survives_restart_as_epistemic_evidence": "YES",
                "association_use_requires_fresh_grounded_currentness_after_restart": "YES",
                "referent_restart_states": ref_restart_states,
                "relation_restart_states": rel_restart_states,
                "post_restart_referent_currentness": [ref_x_restart["status"], ref_y_restart["status"]],
                "post_restart_relation_currentness": rel_normal_restart["status"],
                "new_contradictory_pair_invalidates_prior_qualification": old_ref_q_after_contradiction["status"],
                "contradictory_requalification": {"status": requalify["status"], "reason": requalify["reason"]},
                "invalidated_record_states": invalidated_states,
                "qualification_authority": "EPISTEMIC_ADEQUACY_EVIDENCE_ONLY",
                "effect_authority": "NONE",
                "truth_authority": "NONE",
                "semantic_authority": "NONE",
                "language_authority": "NONE",
                "not_earned": [
                    "SEMANTIC_MEANING",
                    "SEMANTIC_PREDICATE",
                    "GRAMMAR",
                    "PROPOSITION",
                    "EFFECT_AUTHORITY",
                    "LANGUAGE_COMPETENCE",
                    "GENERIC_CONFIDENCE_FACULTY",
                    "GENERIC_CAPABILITY_FACULTY",
                    "ENDOGENOUS_EXPERIMENT_GENERATION",
                    "TAMPER_EVIDENT_LEDGER_SEQUENCE",
                    "CANON_PROMOTION",
                ],
            }
        finally:
            _close(ms2)


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
