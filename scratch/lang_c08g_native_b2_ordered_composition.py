from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import EpistemicStatus, Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld,
    _attach_runtime_surface,
    _close,
)
from scratch.lang_c08f_native_token_referent_binding import (
    _fresh_profiles,
    _pair_episode,
    derive_native_token_referent_bindings,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token

NONE = {
    "semantic_reference_authority": "NONE",
    "truth_authority": "NONE",
    "execution_authority": "NONE",
    "predicate_authority": "NONE",
    "grammar_authority": "NONE",
    "numerical_identity_authority": "NONE",
    "language_authority": "NONE",
}


def _sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def derive_latest_current_native_b2_ordered_composition(
    ms: Microseed,
    *,
    binding_evidence_id: str,
    evidence_id: str,
) -> dict[str, object]:
    """Derive a two-operand ordered composition from observed token chronology.

    The caller supplies no token operands and no operand order.  The latest two opaque
    token observations in the current runtime are the bounded B2 sequence. Each token
    must resolve through a C08F binding to a unique current native referent profile.
    """
    binding_row = ms.evidence.get(str(binding_evidence_id))
    if binding_row is None or (binding_row.get("payload") or {}).get("kind") != "DERIVED_NATIVE_OPAQUE_TOKEN_REFERENT_BINDING_EVIDENCE":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "DURABLE_NATIVE_TOKEN_REFERENT_BINDING_EVIDENCE_REQUIRED"}
    binding_payload = binding_row["payload"]
    binding_map = {
        str(item.get("opaque_token")): str(item.get("operational_referent_signature_sha256"))
        for item in binding_payload.get("bindings", [])
    }
    if len(binding_map) != 2 or len(set(binding_map.values())) != 2:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "EXACT_TWO_NATIVE_REFERENT_BINDINGS_REQUIRED"}

    boot = ms._current_runtime_boot_seq()
    rows = ms.evidence.list()
    current_tokens = [
        (i, row) for i, row in enumerate(rows)
        if (row.get("payload") or {}).get("kind") == "OPAQUE_EXTERNAL_TOKEN_OBSERVATION"
        and int((row.get("payload") or {}).get("runtime_boot_seq", -1)) == boot
    ]
    if len(current_tokens) < 2:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TWO_CURRENT_RUNTIME_OBSERVED_TOKEN_OPERANDS_REQUIRED"}
    selected = current_tokens[-2:]
    tokens = [str((row.get("payload") or {}).get("opaque_token", "")) for _pos, row in selected]
    if any(token not in binding_map for token in tokens):
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "EVERY_OBSERVED_TOKEN_OPERAND_MUST_HAVE_NATIVE_REFERENT_BINDING", "tokens": tokens}
    referent_sigs = [binding_map[token] for token in tokens]
    if len(set(referent_sigs)) != 2:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "INDEPENDENT_NATIVE_REFERENT_OPERANDS_REQUIRED"}

    profile_rows_by_sig: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        payload = row.get("payload") or {}
        if payload.get("kind") != "OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS":
            continue
        if int(payload.get("runtime_boot_seq", -1)) != boot:
            continue
        sig = str(payload.get("operational_referent_signature_sha256", ""))
        profile_rows_by_sig.setdefault(sig, []).append(row)

    components = []
    for (token_pos, token_row), token, referent_sig in zip(selected, tokens, referent_sigs):
        profile_rows = profile_rows_by_sig.get(referent_sig, [])
        if not profile_rows:
            return {
                **NONE,
                "status": "DEFER_UNKNOWN",
                "reason": "CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED",
                "opaque_token": token,
                "referent_signature": referent_sig,
            }
        # Multiple equivalent current witnesses do not create a new referent ambiguity.
        # Use the latest durable evidence witness for the already-earned content identity.
        profile_row = profile_rows[-1]
        records = [
            rec for rec in ms.opaque_evidence_associations.records.values()
            if rec.left_opaque_id == token and rec.right_digest_sha256 == referent_sig
        ]
        if len(records) != 1:
            return {**NONE, "status": "DEFER_UNKNOWN", "reason": "UNIQUE_NATIVE_TOKEN_REFERENT_ASSOCIATION_RECORD_REQUIRED", "opaque_token": token}
        currentness = ms.assess_opaque_evidence_association_currentness(
            records[0].record_id,
            witness_evidence_id=str(profile_row["evidence_id"]),
        )
        if currentness.get("status") != "CURRENTNESS_CONFIRMED":
            return {**NONE, "status": "DEFER_UNKNOWN", "reason": "EVERY_NATIVE_B2_COMPONENT_MUST_BE_CURRENT", "opaque_token": token, "currentness": currentness}
        components.append({
            "ordinal": len(components),
            "opaque_token": token,
            "operational_referent_signature_sha256": referent_sig,
            "token_evidence_ref": [str(token_row["evidence_id"]), str(token_row["sha256"])],
            "profile_evidence_ref": [str(profile_row["evidence_id"]), str(profile_row["sha256"])],
            "association_record_id": records[0].record_id,
            "evidence_list_position": int(token_pos),
            "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
        })

    content = {
        "operator": "ORDERED_EVIDENCE_TUPLE",
        "ordered_operational_referent_signatures": referent_sigs,
        "arity": 2,
        "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
    }
    composition_digest = _sha(content)
    payload = {
        "kind": "OWNED_NATIVE_B2_ORDERED_TOKEN_REFERENT_COMPOSITION_EVIDENCE",
        "composition_content_digest_sha256": composition_digest,
        "components": components,
        "ordered_operational_referent_signatures": referent_sigs,
        "runtime_boot_seq": boot,
        "composition_operator": "ORDERED_EVIDENCE_TUPLE",
        "ordering_basis": "CURRENT_RUNTIME_OPAQUE_TOKEN_EVIDENCE_APPEND_ORDER",
        "operand_selection_basis": "LATEST_TWO_CURRENT_RUNTIME_OPAQUE_TOKEN_OBSERVATIONS",
        "qualification_ancestry": str(binding_payload.get("qualification_ancestry", "UNKNOWN")),
        "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
        "authority_gain": "NONE",
    }
    ref = ms.append_evidence(
        evidence_id,
        payload,
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="DERIVED-NATIVE-B2-ORDERED-EVIDENCE-COMPOSITION",
    )
    return {
        **NONE,
        "status": "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED",
        "composition_evidence_id": ref.evidence_id,
        "composition_evidence_sha256": ref.sha256,
        "composition_content_digest_sha256": composition_digest,
        "components": components,
        "ordered_operational_referent_signatures": referent_sigs,
        "composition_operator": "ORDERED_EVIDENCE_TUPLE",
        "ordering_basis": payload["ordering_basis"],
        "operand_selection_basis": payload["operand_selection_basis"],
        "qualification_ancestry": payload["qualification_ancestry"],
        "identity_scope": payload["identity_scope"],
        "authority_gain": "NONE",
    }


def _build_native_binding(ms: Microseed, world: OpaqueTwoLocusWorld, *, token_x: str, token_y: str):
    profiles = _fresh_profiles(ms, world, tag="B2-BIND-SEED", serial_base=0)
    by_action = {p["exclusive_action_id"]: p for p in profiles["profiles"]}
    sig_x = str(by_action["QX"]["operational_referent_signature_sha256"])
    sig_y = str(by_action["QY"]["operational_referent_signature_sha256"])
    train, hold = [], []
    for i in range(20):
        locus = "X" if i % 2 == 0 else "Y"
        token = token_x if locus == "X" else token_y
        train.append(_pair_episode(ms, world, tag=f"B2-TRAIN-{i}", locus=locus, token=token, index=i, phase="B2TRAIN")["pair_evidence_id"])
    for i in range(10):
        locus = "Y" if i % 2 == 0 else "X"
        token = token_y if locus == "Y" else token_x
        hold.append(_pair_episode(ms, world, tag=f"B2-HOLD-{i}", locus=locus, token=token, index=100 + i, phase="B2HOLD")["pair_evidence_id"])
    bindings = derive_native_token_referent_bindings(
        ms,
        training_pair_evidence_ids=train,
        holdout_pair_evidence_ids=hold,
        evidence_id="E-C08G-BINDING-SET",
    )
    assert bindings["status"] == "NATIVE_OPAQUE_TOKEN_REFERENT_BINDINGS_DERIVED", bindings
    return bindings, by_action, sig_x, sig_y


def _observe_sequence(ms: Microseed, tokens: tuple[str, str], *, phase: str, base_index: int):
    out = []
    for offset, token in enumerate(tokens):
        obs = observe_opaque_token(ms, token, base_index + offset, phase=phase)
        assert obs["status"] == "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE", obs
        out.append(obs)
    return out


def run_campaign(token_x: str = "R4", token_y: str = "T9", sensor_transform=None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08g-native-b2-") as td:
        root = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform

        ms1 = Microseed(root)
        try:
            _attach_runtime_surface(ms1, world, "C08G-R1")
            bindings, profiles1, sig_x, sig_y = _build_native_binding(ms1, world, token_x=token_x, token_y=token_y)
            binding_evidence_id = str(bindings["binding_evidence_id"])
            action_ids_before = set(ms1.capabilities.contracts)

            _observe_sequence(ms1, (token_x, token_y), phase="COMPOSE-XY", base_index=1000)
            xy = derive_latest_current_native_b2_ordered_composition(ms1, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-COMP-XY")
            assert xy["status"] == "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED", xy
            assert xy["ordered_operational_referent_signatures"] == [sig_x, sig_y]

            _observe_sequence(ms1, (token_y, token_x), phase="COMPOSE-YX", base_index=1100)
            yx = derive_latest_current_native_b2_ordered_composition(ms1, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-COMP-YX")
            assert yx["status"] == "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED", yx
            assert yx["ordered_operational_referent_signatures"] == [sig_y, sig_x]
            assert xy["composition_content_digest_sha256"] != yx["composition_content_digest_sha256"]

            _observe_sequence(ms1, (token_x, token_x), phase="COMPOSE-DUP", base_index=1200)
            duplicate = derive_latest_current_native_b2_ordered_composition(ms1, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-COMP-DUP")
            assert duplicate["status"] == "DEFER_UNKNOWN" and duplicate["reason"] == "INDEPENDENT_NATIVE_REFERENT_OPERANDS_REQUIRED"

            _observe_sequence(ms1, (token_x, "UNSEEN"), phase="COMPOSE-UNSEEN", base_index=1300)
            unseen = derive_latest_current_native_b2_ordered_composition(ms1, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-COMP-UNSEEN")
            assert unseen["status"] == "DEFER_UNKNOWN" and unseen["reason"] == "EVERY_OBSERVED_TOKEN_OPERAND_MUST_HAVE_NATIVE_REFERENT_BINDING"

            assert set(ms1.capabilities.contracts) == action_ids_before
            xy_digest = str(xy["composition_content_digest_sha256"])
            yx_digest = str(yx["composition_content_digest_sha256"])
            old_profile_x = str(profiles1["QX"]["evidence_id"])
        finally:
            _close(ms1)

        ms2 = Microseed(root)
        try:
            # Fresh token observations alone cannot make historical referent evidence current.
            _observe_sequence(ms2, (token_x, token_y), phase="RESTART-NO-BODY", base_index=2000)
            stale = derive_latest_current_native_b2_ordered_composition(ms2, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-RESTART-STALE")
            assert stale["status"] == "DEFER_UNKNOWN", stale
            assert stale["reason"] in {"CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED", "EVERY_NATIVE_B2_COMPONENT_MUST_BE_CURRENT"}

            _attach_runtime_surface(ms2, world, "C08G-R2")
            profiles2_raw = _fresh_profiles(ms2, world, tag="B2-R2-SEED", serial_base=3000)
            profiles2 = {p["exclusive_action_id"]: p for p in profiles2_raw["profiles"]}
            assert str(profiles2["QX"]["operational_referent_signature_sha256"]) == sig_x
            assert str(profiles2["QY"]["operational_referent_signature_sha256"]) == sig_y
            assert str(profiles2["QX"]["evidence_id"]) != old_profile_x

            _observe_sequence(ms2, (token_x, token_y), phase="RESTART-XY", base_index=2100)
            xy2 = derive_latest_current_native_b2_ordered_composition(ms2, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-RESTART-XY")
            assert xy2["status"] == "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED", xy2
            assert xy2["composition_content_digest_sha256"] == xy_digest

            _observe_sequence(ms2, (token_y, token_x), phase="RESTART-YX", base_index=2200)
            yx2 = derive_latest_current_native_b2_ordered_composition(ms2, binding_evidence_id=binding_evidence_id, evidence_id="E-C08G-RESTART-YX")
            assert yx2["status"] == "CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED", yx2
            assert yx2["composition_content_digest_sha256"] == yx_digest

            assert not hasattr(ms2, "grammar_registry")
            assert not hasattr(ms2, "predicate_registry")
            assert not hasattr(ms2, "meaning_registry")
            assert not hasattr(ms2, "language_module")
            assert not hasattr(ms2, "faculty_registry")

            return {
                "status": "C08G_NATIVE_B2_ORDERED_COMPOSITION_REEMBODIED",
                "technical_name": "Current-evidence ordered composition of opaque observed-token-resolved operational referent equivalence classes",
                "xy_composition_digest_sha256": xy_digest,
                "yx_composition_digest_sha256": yx_digest,
                "order_sensitive": xy_digest != yx_digest,
                "xy_ordered_referent_signatures": xy["ordered_operational_referent_signatures"],
                "yx_ordered_referent_signatures": yx["ordered_operational_referent_signatures"],
                "duplicate_operands": {"status": duplicate["status"], "reason": duplicate["reason"]},
                "unseen_operand": {"status": unseen["status"], "reason": unseen["reason"]},
                "restart_without_fresh_profiles": {"status": stale["status"], "reason": stale["reason"]},
                "post_restart_xy": xy2["status"],
                "post_restart_yx": yx2["status"],
                "composition_operator": xy["composition_operator"],
                "ordering_basis": xy["ordering_basis"],
                "operand_selection_basis": xy["operand_selection_basis"],
                "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
                "qualification_ancestry": xy["qualification_ancestry"],
                "microseed_delta_required": [],
                "new_microseed_action_contracts_registered": [],
                "caller_supplied_token_operands": "NO",
                "caller_supplied_operand_order": "NO",
                "caller_supplied_grammar_roles": "NO",
                "caller_supplied_referent_identity": "NO",
                "semantic_reference_authority": "NONE",
                "truth_authority": "NONE",
                "execution_authority": "NONE",
                "predicate_authority": "NONE",
                "grammar_authority": "NONE",
                "numerical_identity_authority": "NONE",
                "language_authority": "NONE",
                "not_earned": [
                    "SEMANTIC_PREDICATION",
                    "GRAMMAR",
                    "PROPOSITION",
                    "NUMERICAL_OBJECT_IDENTITY",
                    "SYSTEMATIC_RECOMBINATION",
                    "LANGUAGE_COMPETENCE",
                    "ENDOGENOUS_QUALIFICATION",
                    "GENERIC_CAPABILITY_FACULTY",
                    "CANON_PROMOTION",
                ],
            }
        finally:
            _close(ms2)


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
