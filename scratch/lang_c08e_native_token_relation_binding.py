from __future__ import annotations

import hashlib
import json
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from typing import Iterable

from microseed import EpistemicStatus, Microseed
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld,
    _attach_runtime_surface,
    _close,
    _external_control_state,
    _fresh_owned_relation,
    _raw,
)


NONE = {
    "truth_authority": "NONE",
    "semantic_authority": "NONE",
    "execution_authority": "NONE",
    "language_authority": "NONE",
}


def _sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def observe_opaque_token(ms: Microseed, token: str, index: int, *, phase: str) -> dict[str, object]:
    """Persist an externally observed opaque token as content-bound Microseed evidence."""
    evidence_id = f"E-C08E-TOKEN-{phase}-{index}"
    payload = {
        "kind": "OPAQUE_EXTERNAL_TOKEN_OBSERVATION",
        "capture_id": f"C08E-TOKEN-{phase}-{index}",
        "opaque_token": str(token),
        "runtime_boot_seq": ms._current_runtime_boot_seq(),
        "observation_authority": "OBSERVATION_ONLY",
    }
    ref = ms.append_evidence(
        evidence_id,
        payload,
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="EXTERNAL-WORLD",
    )
    row = ms.evidence.get(evidence_id)
    if row is None or row.get("sha256") != ref.sha256:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TOKEN_EVIDENCE_NOT_CONTENT_BOUND"}
    return {
        **NONE,
        "status": "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE",
        "evidence_id": evidence_id,
        "evidence_sha256": ref.sha256,
        "opaque_token": str(row["payload"]["opaque_token"]),
        "runtime_boot_seq": int(row["payload"]["runtime_boot_seq"]),
    }


def _native_relation_episode(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    tag: str,
    reverse: bool,
) -> dict[str, object]:
    """Produce one fresh native C08D relation witness from a passive world transition."""
    if reverse:
        world.set_passive_baseline(1, 2)
    else:
        world.set_passive_baseline(2, 1)
    _external_control_state(ms, f"{tag}-PRE")
    _raw(ms, f"{tag}-PRE")
    world.apply_passive_xy_to_yx()
    _external_control_state(ms, f"{tag}-POST")
    _raw(ms, f"{tag}-POST")
    relation = ms.derive_and_record_current_owned_affordance_relative_directional_relation(
        evidence_id=f"E-C08E-REL-{tag}",
        max_events=16384,
        max_records=16384,
    )
    assert relation["status"] == "CURRENT_OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_RECORDED", relation
    assert relation["runtime_boot_seq"] == ms._current_runtime_boot_seq(), relation
    return relation


def derive_latest_relation_token_pair(ms: Microseed, *, evidence_id: str) -> dict[str, object]:
    """Bind the latest token observation to the immediately preceding native relation evidence.

    Pair ownership comes from the evidence ledger chronology.  The caller supplies only
    the output evidence id; it does not supply token bytes, relation digest, relation order,
    or a semantic label.
    """
    rows = ms.evidence.list()  # documented append order; row position is evidence chronology
    boot_seq = ms._current_runtime_boot_seq()
    token_positions = [
        i for i, row in enumerate(rows)
        if isinstance(row.get("payload"), dict)
        and row["payload"].get("kind") == "OPAQUE_EXTERNAL_TOKEN_OBSERVATION"
        and int(row["payload"].get("runtime_boot_seq", -1)) == boot_seq
    ]
    if not token_positions:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_RUNTIME_TOKEN_EVIDENCE_REQUIRED"}
    token_pos = token_positions[-1]
    token_row = rows[token_pos]
    relation_positions = [
        i for i, row in enumerate(rows[:token_pos])
        if isinstance(row.get("payload"), dict)
        and row["payload"].get("kind") == "OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_WITNESS"
        and int(row["payload"].get("runtime_boot_seq", -1)) == boot_seq
    ]
    if not relation_positions:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_RUNTIME_NATIVE_RELATION_EVIDENCE_REQUIRED"}
    relation_pos = relation_positions[-1]
    relation_row = rows[relation_pos]

    # No other token/relation evidence may intervene between the selected relation and token.
    between = rows[relation_pos + 1:token_pos]
    for row in between:
        payload = row.get("payload") or {}
        if payload.get("kind") in {
            "OPAQUE_EXTERNAL_TOKEN_OBSERVATION",
            "OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_WITNESS",
        }:
            return {**NONE, "status": "DEFER_UNKNOWN", "reason": "RELATION_TOKEN_CHRONOLOGY_NOT_UNIQUE"}

    relation = relation_row["payload"]
    token = token_row["payload"]
    payload = {
        "kind": "OWNED_OPAQUE_TOKEN_NATIVE_RELATION_PAIR_EVIDENCE",
        "opaque_token": str(token["opaque_token"]),
        "relation_digest_sha256": str(relation["relation_digest_sha256"]),
        "ordered_operational_referent_signatures": list(relation["ordered_operational_referent_signatures"]),
        "relation_evidence_ref": [str(relation_row["evidence_id"]), str(relation_row["sha256"])],
        "token_evidence_ref": [str(token_row["evidence_id"]), str(token_row["sha256"])],
        "runtime_boot_seq": boot_seq,
        "pairing_basis": "CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY",
        "authority_gain": "NONE",
    }
    ref = ms.append_evidence(
        evidence_id,
        payload,
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="DERIVED-NATIVE-RELATION-TOKEN-CHRONOLOGY",
    )
    return {
        **NONE,
        "status": "CURRENT_OWNED_OPAQUE_TOKEN_NATIVE_RELATION_PAIR_RECORDED",
        "pair_evidence_id": ref.evidence_id,
        "pair_evidence_sha256": ref.sha256,
        "opaque_token": payload["opaque_token"],
        "relation_digest_sha256": payload["relation_digest_sha256"],
        "ordered_operational_referent_signatures": payload["ordered_operational_referent_signatures"],
        "runtime_boot_seq": boot_seq,
    }


def derive_native_token_relation_bindings(
    ms: Microseed,
    *,
    training_pair_evidence_ids: Iterable[str],
    holdout_pair_evidence_ids: Iterable[str],
    evidence_id: str,
) -> dict[str, object]:
    """Derive a 2x2 opaque-token/native-relation bijection from exact durable pair evidence."""
    train_ids = tuple(str(x) for x in training_pair_evidence_ids)
    hold_ids = tuple(str(x) for x in holdout_pair_evidence_ids)
    if len(train_ids) < 16:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "SUFFICIENT_TRAINING_PAIR_EVIDENCE_REQUIRED"}
    if len(hold_ids) < 8:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "INDEPENDENT_HOLDOUT_PAIR_EVIDENCE_REQUIRED"}

    def load(ids: tuple[str, ...]):
        loaded = []
        for eid in ids:
            row = ms.evidence.get(eid)
            if row is None or row.get("negative"):
                return None, "PAIR_EVIDENCE_NOT_FOUND_OR_NEGATIVE"
            payload = row.get("payload") or {}
            if payload.get("kind") != "OWNED_OPAQUE_TOKEN_NATIVE_RELATION_PAIR_EVIDENCE":
                return None, "NATIVE_RELATION_TOKEN_PAIR_EVIDENCE_REQUIRED"
            for ref_key in ("relation_evidence_ref", "token_evidence_ref"):
                ref = payload.get(ref_key)
                if not isinstance(ref, list) or len(ref) != 2:
                    return None, "PAIR_SOURCE_EVIDENCE_REF_REQUIRED"
                source = ms.evidence.get(str(ref[0]))
                if source is None or str(source.get("sha256", "")) != str(ref[1]):
                    return None, "PAIR_SOURCE_EVIDENCE_NOT_EXACT"
            loaded.append((row, payload))
        return loaded, None

    train, err = load(train_ids)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TRAIN_" + err}
    hold, err = load(hold_ids)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_" + err}

    def mapping(rows):
        token_to_rel = {}
        rel_to_token = {}
        for _row, payload in rows:
            token = str(payload["opaque_token"])
            rel = str(payload["relation_digest_sha256"])
            token_to_rel.setdefault(token, set()).add(rel)
            rel_to_token.setdefault(rel, set()).add(token)
        if len(token_to_rel) != 2 or len(rel_to_token) != 2:
            return None, "EXACTLY_TWO_OPAQUE_TOKENS_AND_TWO_NATIVE_RELATIONS_REQUIRED"
        if any(len(v) != 1 for v in token_to_rel.values()) or any(len(v) != 1 for v in rel_to_token.values()):
            return None, "TOKEN_NATIVE_RELATION_ASSOCIATION_NOT_BIJECTIVE"
        return {token: next(iter(values)) for token, values in token_to_rel.items()}, None

    train_map, err = mapping(train)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TRAIN_" + err}
    hold_map, err = mapping(hold)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_" + err}
    if train_map != hold_map:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_TOKEN_NATIVE_RELATION_ASSOCIATION_DISAGREES"}

    bindings = [
        {"opaque_token": token, "relation_digest_sha256": train_map[token]}
        for token in sorted(train_map)
    ]
    payload = {
        "kind": "DERIVED_NATIVE_OPAQUE_TOKEN_RELATION_BINDING_EVIDENCE",
        "bindings": bindings,
        "training_pair_evidence_refs": [
            [row["evidence_id"], row["sha256"]] for row, _payload in train
        ],
        "holdout_pair_evidence_refs": [
            [row["evidence_id"], row["sha256"]] for row, _payload in hold
        ],
        "qualification_ancestry": "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY",
        "authority_gain": "NONE",
    }
    binding_set_id = "NATIVE-TOK-REL-" + _sha(payload)[:24]
    payload["binding_set_id"] = binding_set_id
    ref = ms.append_evidence(
        evidence_id,
        payload,
        EpistemicStatus.PRESSURE_SUPPORTED,
        source="DERIVED-NATIVE-PAIRED-EXPERIENCE",
    )
    stored = ms.evidence.get(evidence_id)
    if stored is None or stored.get("sha256") != ref.sha256:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "NATIVE_BINDING_EVIDENCE_NOT_READABLE"}

    association_records = []
    for binding in bindings:
        token = str(binding["opaque_token"])
        relation_digest = str(binding["relation_digest_sha256"])
        token_pair_refs = []
        for row, pair in train + hold:
            if str(pair["opaque_token"]) == token:
                token_pair_refs.append((str(row["evidence_id"]), str(row["sha256"])))
        rec = ms.register_opaque_evidence_association(
            left_opaque_id=token,
            right_digest_sha256=relation_digest,
            source_evidence_refs=tuple(token_pair_refs) + ((ref.evidence_id, ref.sha256),),
            assistance_ancestry=(
                "NATIVE_RELATION_TOKEN_PAIR_EVIDENCE",
                "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY",
                "NO_TOKEN_MEANING_SUPPLIED",
            ),
        )
        association_records.append({
            "opaque_token": token,
            "relation_digest_sha256": relation_digest,
            "record_id": rec["record_id"],
        })

    return {
        **NONE,
        "status": "NATIVE_OPAQUE_TOKEN_RELATION_BINDINGS_DERIVED",
        "binding_set_id": binding_set_id,
        "binding_evidence_id": ref.evidence_id,
        "binding_evidence_sha256": ref.sha256,
        "bindings": bindings,
        "association_records": association_records,
        "qualification_ancestry": payload["qualification_ancestry"],
        "authority_gain": "NONE",
    }


def resolve_native_token_relation(
    ms: Microseed,
    *,
    binding_evidence_id: str,
    opaque_token: str,
    current_relation_evidence_id: str,
) -> dict[str, object]:
    binding_row = ms.evidence.get(str(binding_evidence_id))
    relation_row = ms.evidence.get(str(current_relation_evidence_id))
    if binding_row is None:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "DURABLE_NATIVE_BINDING_EVIDENCE_REQUIRED"}
    binding_payload = binding_row.get("payload") or {}
    if binding_payload.get("kind") != "DERIVED_NATIVE_OPAQUE_TOKEN_RELATION_BINDING_EVIDENCE":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "NATIVE_TOKEN_RELATION_BINDING_EVIDENCE_REQUIRED"}
    if relation_row is None:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_NATIVE_RELATION_EVIDENCE_REQUIRED"}
    relation_payload = relation_row.get("payload") or {}
    if relation_payload.get("kind") != "OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_WITNESS":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_NATIVE_RELATION_EVIDENCE_REQUIRED"}
    if int(relation_payload.get("runtime_boot_seq", -1)) != ms._current_runtime_boot_seq():
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "FRESH_CURRENT_RUNTIME_OWNED_RELATION_WITNESS_REQUIRED"}

    matches = [
        item for item in binding_payload.get("bindings", [])
        if str(item.get("opaque_token")) == str(opaque_token)
    ]
    if len(matches) != 1:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "OPAQUE_TOKEN_NOT_GROUNDED_BY_NATIVE_PAIRED_EVIDENCE"}
    expected = str(matches[0]["relation_digest_sha256"])
    observed = str(relation_payload.get("relation_digest_sha256", ""))
    if expected != observed:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TOKEN_BINDING_DOES_NOT_MATCH_CURRENT_NATIVE_RELATION"}

    records = [
        rec for rec in ms.opaque_evidence_associations.records.values()
        if rec.left_opaque_id == str(opaque_token) and rec.right_digest_sha256 == expected
    ]
    if len(records) != 1:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "UNIQUE_NATIVE_TOKEN_ASSOCIATION_RECORD_REQUIRED"}
    currentness = ms.assess_opaque_evidence_association_currentness(
        records[0].record_id,
        witness_evidence_id=str(current_relation_evidence_id),
    )
    if currentness.get("status") != "CURRENTNESS_CONFIRMED":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TOKEN_NATIVE_RELATION_ASSOCIATION_NOT_CURRENT", "currentness": currentness}
    return {
        **NONE,
        "status": "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION",
        "opaque_token": str(opaque_token),
        "relation_digest_sha256": observed,
        "ordered_operational_referent_signatures": list(relation_payload["ordered_operational_referent_signatures"]),
        "binding_set_id": str(binding_payload["binding_set_id"]),
        "association_record_id": records[0].record_id,
        "authority_gain": "NONE",
    }


def _pair_episode(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    tag: str,
    reverse: bool,
    token: str,
    index: int,
    phase: str,
) -> dict[str, object]:
    relation = _native_relation_episode(ms, world, tag=tag, reverse=reverse)
    token_obs = observe_opaque_token(ms, token, index, phase=phase)
    assert token_obs["status"] == "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE", token_obs
    pair = derive_latest_relation_token_pair(ms, evidence_id=f"E-C08E-PAIR-{phase}-{index}")
    assert pair["status"] == "CURRENT_OWNED_OPAQUE_TOKEN_NATIVE_RELATION_PAIR_RECORDED", pair
    assert pair["relation_digest_sha256"] == relation["relation_digest_sha256"]
    assert pair["opaque_token"] == token
    return pair


def run_campaign(token_a: str = "K7", token_b: str = "M2", sensor_transform=None) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08e-native-token-") as td:
        root = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform

        ms1 = Microseed(root)
        try:
            _attach_runtime_surface(ms1, world, "C08E-R1")
            # Fresh owned action/raw history creates current native affordance profiles.
            first = _fresh_owned_relation(ms1, world, tag="C08E-R1-SEED", serial_base=0)
            normal_digest = str(first["relation"]["relation_digest_sha256"])

            # Establish the opposing relation digest without token labels deciding its identity.
            reverse_probe = _native_relation_episode(ms1, world, tag="C08E-R1-REVERSE-PROBE", reverse=True)
            reverse_digest = str(reverse_probe["relation_digest_sha256"])
            assert reverse_digest != normal_digest

            action_ids_before = set(ms1.capabilities.contracts)
            train_ids = []
            hold_ids = []
            for i in range(20):
                reverse = bool(i % 2)
                token = token_b if reverse else token_a
                pair = _pair_episode(
                    ms1, world,
                    tag=f"TRAIN-{i}", reverse=reverse, token=token, index=i, phase="TRAIN",
                )
                train_ids.append(pair["pair_evidence_id"])
            for i in range(10):
                reverse = not bool(i % 2)
                token = token_b if reverse else token_a
                pair = _pair_episode(
                    ms1, world,
                    tag=f"HOLD-{i}", reverse=reverse, token=token, index=100 + i, phase="HOLD",
                )
                hold_ids.append(pair["pair_evidence_id"])

            bindings = derive_native_token_relation_bindings(
                ms1,
                training_pair_evidence_ids=train_ids,
                holdout_pair_evidence_ids=hold_ids,
                evidence_id="E-C08E-BINDING-SET",
            )
            assert bindings["status"] == "NATIVE_OPAQUE_TOKEN_RELATION_BINDINGS_DERIVED", bindings
            mapping = {item["opaque_token"]: item["relation_digest_sha256"] for item in bindings["bindings"]}
            assert mapping[token_a] == normal_digest
            assert mapping[token_b] == reverse_digest

            fresh_normal = _native_relation_episode(ms1, world, tag="RESOLVE-NORMAL", reverse=False)
            fresh_reverse = _native_relation_episode(ms1, world, tag="RESOLVE-REVERSE", reverse=True)
            resolve_a = resolve_native_token_relation(
                ms1,
                binding_evidence_id=bindings["binding_evidence_id"],
                opaque_token=token_a,
                current_relation_evidence_id=fresh_normal["evidence_id"],
            )
            resolve_b = resolve_native_token_relation(
                ms1,
                binding_evidence_id=bindings["binding_evidence_id"],
                opaque_token=token_b,
                current_relation_evidence_id=fresh_reverse["evidence_id"],
            )
            assert resolve_a["status"] == resolve_b["status"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION"
            unseen = resolve_native_token_relation(
                ms1,
                binding_evidence_id=bindings["binding_evidence_id"],
                opaque_token="UNSEEN",
                current_relation_evidence_id=fresh_normal["evidence_id"],
            )
            assert unseen["status"] == "DEFER_UNKNOWN"
            wrong_relation = resolve_native_token_relation(
                ms1,
                binding_evidence_id=bindings["binding_evidence_id"],
                opaque_token=token_a,
                current_relation_evidence_id=fresh_reverse["evidence_id"],
            )
            assert wrong_relation["status"] == "DEFER_UNKNOWN"

            # Independent holdout convention reversal must fail closed.
            reversed_hold_ids = []
            for i in range(10):
                reverse = bool(i % 2)
                wrong_token = token_a if reverse else token_b
                pair = _pair_episode(
                    ms1, world,
                    tag=f"REVHOLD-{i}", reverse=reverse, token=wrong_token, index=200 + i, phase="REVHOLD",
                )
                reversed_hold_ids.append(pair["pair_evidence_id"])
            reversal = derive_native_token_relation_bindings(
                ms1,
                training_pair_evidence_ids=train_ids,
                holdout_pair_evidence_ids=reversed_hold_ids,
                evidence_id="E-C08E-BINDING-REVERSAL",
            )
            assert reversal["status"] == "DEFER_UNKNOWN"
            assert reversal["reason"] == "HOLDOUT_TOKEN_NATIVE_RELATION_ASSOCIATION_DISAGREES"

            # Ambiguous holdout must fail closed.
            ambiguous_ids = list(hold_ids)
            ambiguous_pair = _pair_episode(
                ms1, world,
                tag="AMBIGUOUS", reverse=False, token=token_b, index=300, phase="AMBIG",
            )
            ambiguous_ids[0] = ambiguous_pair["pair_evidence_id"]
            ambiguity = derive_native_token_relation_bindings(
                ms1,
                training_pair_evidence_ids=train_ids,
                holdout_pair_evidence_ids=ambiguous_ids,
                evidence_id="E-C08E-BINDING-AMBIGUITY",
            )
            assert ambiguity["status"] == "DEFER_UNKNOWN"

            binding_evidence_id = str(bindings["binding_evidence_id"])
            association_record_ids = [item["record_id"] for item in bindings["association_records"]]
            action_ids_after = set(ms1.capabilities.contracts)
            assert action_ids_after == action_ids_before
        finally:
            _close(ms1)

        # Restart: binding bytes persist, but old native relation currentness does not.
        ms2 = Microseed(root)
        try:
            states_after_restart = {
                rid: ms2.opaque_evidence_association_status(rid)["status"]
                for rid in association_record_ids
            }
            assert set(states_after_restart.values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}

            old_resolution = resolve_native_token_relation(
                ms2,
                binding_evidence_id=binding_evidence_id,
                opaque_token=token_a,
                current_relation_evidence_id=fresh_normal["evidence_id"],
            )
            assert old_resolution["status"] == "DEFER_UNKNOWN"
            assert old_resolution["reason"] == "FRESH_CURRENT_RUNTIME_OWNED_RELATION_WITNESS_REQUIRED"

            _attach_runtime_surface(ms2, world, "C08E-R2")
            second = _fresh_owned_relation(ms2, world, tag="C08E-R2-SEED", serial_base=1000)
            fresh_after_restart = second["relation"]
            assert fresh_after_restart["relation_digest_sha256"] == normal_digest
            after_restart = resolve_native_token_relation(
                ms2,
                binding_evidence_id=binding_evidence_id,
                opaque_token=token_a,
                current_relation_evidence_id=fresh_after_restart["evidence_id"],
            )
            assert after_restart["status"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_RELATION", after_restart

            # Fresh opposite relation must not resolve token A; native association remains relation-specific.
            opposite_after_restart = _native_relation_episode(ms2, world, tag="C08E-R2-OPPOSITE", reverse=True)
            wrong_after_restart = resolve_native_token_relation(
                ms2,
                binding_evidence_id=binding_evidence_id,
                opaque_token=token_a,
                current_relation_evidence_id=opposite_after_restart["evidence_id"],
            )
            assert wrong_after_restart["status"] == "DEFER_UNKNOWN"

            assert not hasattr(ms2, "predicate_registry")
            assert not hasattr(ms2, "meaning_registry")
            assert not hasattr(ms2, "language_module")
            assert not hasattr(ms2, "faculty_registry")

            return {
                "status": "C08E_NATIVE_C07_TOKEN_BINDING_REEMBODIED_ON_POSTRESTART_NATIVE_RELATION",
                "technical_name": "Evidence-ledger paired grounding of opaque observed tokens to restart-safe native affordance-relative relation identities",
                "normal_relation_digest_sha256": normal_digest,
                "reverse_relation_digest_sha256": reverse_digest,
                "bindings": bindings["bindings"],
                "association_record_ids": association_record_ids,
                "token_a_resolution": resolve_a["status"],
                "token_b_resolution": resolve_b["status"],
                "unseen_token": unseen["status"],
                "wrong_relation": wrong_relation["status"],
                "holdout_reversal": {"status": reversal["status"], "reason": reversal["reason"]},
                "ambiguous_holdout": ambiguity["status"],
                "association_states_after_restart": states_after_restart,
                "durable_binding_without_fresh_relation": {"status": old_resolution["status"], "reason": old_resolution["reason"]},
                "post_restart_native_resolution": after_restart["status"],
                "post_restart_wrong_relation": wrong_after_restart["status"],
                "microseed_delta_required": [],
                "new_microseed_action_contracts_registered": [],
                "caller_supplied_token_meaning": "NO",
                "caller_supplied_relation_order": "NO",
                "caller_supplied_relation_digest": "NO",
                "pairing_basis": "CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY",
                "qualification_ancestry": bindings["qualification_ancestry"],
                "truth_authority": "NONE",
                "semantic_authority": "NONE",
                "execution_authority": "NONE",
                "language_authority": "NONE",
                "not_earned": [
                    "SEMANTIC_PREDICATE",
                    "TOKEN_MEANING",
                    "PROPOSITION",
                    "TRUTH_BEARER",
                    "LANGUAGE_FACULTY",
                    "GENERIC_CAPABILITY_FACULTY",
                    "ENDOGENOUS_QUALIFICATION",
                    "CANON_PROMOTION",
                ],
            }
        finally:
            _close(ms2)


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
