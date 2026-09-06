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
    _execute,
    _external_control_state,
    _observe_action_state_s0,
    _raw,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token

NONE = {
    "truth_authority": "NONE",
    "semantic_authority": "NONE",
    "execution_authority": "NONE",
    "language_authority": "NONE",
    "numerical_identity_authority": "NONE",
}


def _sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _fresh_profiles(ms: Microseed, world: OpaqueTwoLocusWorld, *, tag: str, serial_base: int):
    world.set_passive_baseline(0, 0)
    _observe_action_state_s0(ms, f"{tag}-START")
    _raw(ms, f"{tag}-P0")
    for offset, (cid, step) in enumerate((("QX", "X0"), ("QX", "X1"), ("QY", "Y0"), ("QY", "Y1"))):
        _execute(ms, cid, f"{tag}-{step}", serial_base + offset)
        _raw(ms, f"{tag}-P{offset + 1}")
    profiles = ms.record_current_owned_affordance_effect_profiles(
        evidence_id_prefix=f"E-C08F-{tag}-PROFILE",
        max_probe_steps=4,
    )
    assert profiles["status"] == "CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED", profiles
    assert profiles["profile_count"] == 2, profiles
    return profiles


def _localized_passive_referent_event(ms: Microseed, world: OpaqueTwoLocusWorld, *, tag: str, locus: str):
    world.set_passive_baseline(0, 0)
    _external_control_state(ms, f"{tag}-PRE")
    _raw(ms, f"{tag}-PRE")
    if locus == "X":
        world.x += 1
    elif locus == "Y":
        world.y += 1
    else:
        raise ValueError(locus)
    _external_control_state(ms, f"{tag}-POST")
    _raw(ms, f"{tag}-POST")
    passive = ms.derive_current_owned_passive_raw_transition(max_events=16384)
    assert passive["status"] == "CURRENT_OWNED_PASSIVE_RAW_TRANSITION", passive
    before = tuple(passive["before_raw"])
    after = tuple(passive["after_raw"])
    changed = tuple(i for i, (a, b) in enumerate(zip(before, after)) if a != b)
    if not changed:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "PASSIVE_REFERENT_EVENT_MUST_CHANGE_RAW_CONTENT"}
    boot = ms._current_runtime_boot_seq()
    rows = ms.evidence.list()
    profiles = []
    for row in rows:
        payload = row.get("payload") or {}
        if payload.get("kind") != "OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS":
            continue
        if int(payload.get("runtime_boot_seq", -1)) != boot:
            continue
        if tuple(int(x) for x in payload.get("group_channels", ())) == changed:
            profiles.append((row, payload))
    if len(profiles) != 1:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "EXACT_ONE_CURRENT_NATIVE_REFERENT_PROFILE_MUST_MATCH_PASSIVE_CHANGE", "changed_channels": changed, "match_count": len(profiles)}
    row, profile = profiles[0]
    payload = {
        "kind": "OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZATION_WITNESS",
        "operational_referent_signature_sha256": str(profile["operational_referent_signature_sha256"]),
        "profile_evidence_ref": [str(row["evidence_id"]), str(row["sha256"])],
        "passive_raw_evidence_refs": [
            [str(passive["before_raw_evidence_id"]), str(passive["before_raw_evidence_sha256"])],
            [str(passive["after_raw_evidence_id"]), str(passive["after_raw_evidence_sha256"])],
        ],
        "changed_channels": list(changed),
        "runtime_boot_seq": boot,
        "localization_basis": "CURRENT_NATIVE_REFERENT_PROFILE_GROUP_EQUALS_OPAQUE_PASSIVE_CHANGED_CHANNEL_SET",
        "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
        "authority_gain": "NONE",
    }
    ref = ms.append_evidence(
        f"E-C08F-LOC-{tag}", payload, EpistemicStatus.PRESSURE_SUPPORTED,
        source="DERIVED-NATIVE-PASSIVE-REFERENT-LOCALIZATION",
    )
    return {
        **NONE,
        "status": "CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED",
        "localization_evidence_id": ref.evidence_id,
        "localization_evidence_sha256": ref.sha256,
        "operational_referent_signature_sha256": payload["operational_referent_signature_sha256"],
        "profile_evidence_id": str(row["evidence_id"]),
        "profile_evidence_sha256": str(row["sha256"]),
        "runtime_boot_seq": boot,
    }


def _derive_latest_localization_token_pair(ms: Microseed, *, evidence_id: str):
    rows = ms.evidence.list()
    boot = ms._current_runtime_boot_seq()
    token_positions = [i for i, row in enumerate(rows) if (row.get("payload") or {}).get("kind") == "OPAQUE_EXTERNAL_TOKEN_OBSERVATION" and int((row.get("payload") or {}).get("runtime_boot_seq", -1)) == boot]
    if not token_positions:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_RUNTIME_TOKEN_EVIDENCE_REQUIRED"}
    token_pos = token_positions[-1]
    token_row = rows[token_pos]
    loc_positions = [i for i, row in enumerate(rows[:token_pos]) if (row.get("payload") or {}).get("kind") == "OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZATION_WITNESS" and int((row.get("payload") or {}).get("runtime_boot_seq", -1)) == boot]
    if not loc_positions:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_RUNTIME_NATIVE_REFERENT_LOCALIZATION_REQUIRED"}
    loc_pos = loc_positions[-1]
    loc_row = rows[loc_pos]
    for row in rows[loc_pos + 1:token_pos]:
        kind = (row.get("payload") or {}).get("kind")
        if kind in {"OPAQUE_EXTERNAL_TOKEN_OBSERVATION", "OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZATION_WITNESS"}:
            return {**NONE, "status": "DEFER_UNKNOWN", "reason": "REFERENT_TOKEN_CHRONOLOGY_NOT_UNIQUE"}
    loc = loc_row["payload"]
    tok = token_row["payload"]
    payload = {
        "kind": "OWNED_OPAQUE_TOKEN_NATIVE_REFERENT_PAIR_EVIDENCE",
        "opaque_token": str(tok["opaque_token"]),
        "operational_referent_signature_sha256": str(loc["operational_referent_signature_sha256"]),
        "localization_evidence_ref": [str(loc_row["evidence_id"]), str(loc_row["sha256"])],
        "token_evidence_ref": [str(token_row["evidence_id"]), str(token_row["sha256"])],
        "runtime_boot_seq": boot,
        "pairing_basis": "CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY",
        "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
        "authority_gain": "NONE",
    }
    ref = ms.append_evidence(evidence_id, payload, EpistemicStatus.PRESSURE_SUPPORTED, source="DERIVED-NATIVE-REFERENT-TOKEN-CHRONOLOGY")
    return {**NONE, "status": "CURRENT_OWNED_OPAQUE_TOKEN_NATIVE_REFERENT_PAIR_RECORDED", "pair_evidence_id": ref.evidence_id, "pair_evidence_sha256": ref.sha256, "opaque_token": payload["opaque_token"], "operational_referent_signature_sha256": payload["operational_referent_signature_sha256"]}


def derive_native_token_referent_bindings(ms: Microseed, *, training_pair_evidence_ids, holdout_pair_evidence_ids, evidence_id: str):
    train_ids = tuple(str(x) for x in training_pair_evidence_ids)
    hold_ids = tuple(str(x) for x in holdout_pair_evidence_ids)
    if len(train_ids) < 16:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "SUFFICIENT_TRAINING_PAIR_EVIDENCE_REQUIRED"}
    if len(hold_ids) < 8:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "INDEPENDENT_HOLDOUT_PAIR_EVIDENCE_REQUIRED"}

    def load(ids):
        out = []
        for eid in ids:
            row = ms.evidence.get(eid)
            if row is None or row.get("negative"):
                return None, "PAIR_EVIDENCE_NOT_FOUND_OR_NEGATIVE"
            payload = row.get("payload") or {}
            if payload.get("kind") != "OWNED_OPAQUE_TOKEN_NATIVE_REFERENT_PAIR_EVIDENCE":
                return None, "NATIVE_REFERENT_TOKEN_PAIR_EVIDENCE_REQUIRED"
            for key in ("localization_evidence_ref", "token_evidence_ref"):
                ref = payload.get(key)
                if not isinstance(ref, list) or len(ref) != 2:
                    return None, "PAIR_SOURCE_EVIDENCE_REF_REQUIRED"
                source = ms.evidence.get(str(ref[0]))
                if source is None or str(source.get("sha256", "")) != str(ref[1]):
                    return None, "PAIR_SOURCE_EVIDENCE_NOT_EXACT"
            out.append((row, payload))
        return out, None

    train, err = load(train_ids)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TRAIN_" + err}
    hold, err = load(hold_ids)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_" + err}

    def mapping(rows):
        t2r, r2t = {}, {}
        for _row, payload in rows:
            token = str(payload["opaque_token"])
            ref = str(payload["operational_referent_signature_sha256"])
            t2r.setdefault(token, set()).add(ref)
            r2t.setdefault(ref, set()).add(token)
        if len(t2r) != 2 or len(r2t) != 2:
            return None, "EXACTLY_TWO_OPAQUE_TOKENS_AND_TWO_NATIVE_REFERENTS_REQUIRED"
        if any(len(v) != 1 for v in t2r.values()) or any(len(v) != 1 for v in r2t.values()):
            return None, "TOKEN_NATIVE_REFERENT_ASSOCIATION_NOT_BIJECTIVE"
        return {t: next(iter(v)) for t, v in t2r.items()}, None

    tm, err = mapping(train)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TRAIN_" + err}
    hm, err = mapping(hold)
    if err:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_" + err}
    if tm != hm:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "HOLDOUT_TOKEN_NATIVE_REFERENT_ASSOCIATION_DISAGREES"}

    bindings = [{"opaque_token": token, "operational_referent_signature_sha256": tm[token]} for token in sorted(tm)]
    payload = {
        "kind": "DERIVED_NATIVE_OPAQUE_TOKEN_REFERENT_BINDING_EVIDENCE",
        "bindings": bindings,
        "training_pair_evidence_refs": [[row["evidence_id"], row["sha256"]] for row, _ in train],
        "holdout_pair_evidence_refs": [[row["evidence_id"], row["sha256"]] for row, _ in hold],
        "qualification_ancestry": "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY",
        "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
        "authority_gain": "NONE",
    }
    payload["binding_set_id"] = "NATIVE-TOK-REF-" + _sha(payload)[:24]
    ref = ms.append_evidence(evidence_id, payload, EpistemicStatus.PRESSURE_SUPPORTED, source="DERIVED-NATIVE-REFERENT-PAIRED-EXPERIENCE")
    records = []
    for binding in bindings:
        token = str(binding["opaque_token"])
        referent_sig = str(binding["operational_referent_signature_sha256"])
        pair_refs = [(str(row["evidence_id"]), str(row["sha256"])) for row, pair in train + hold if str(pair["opaque_token"]) == token]
        rec = ms.register_opaque_evidence_association(
            left_opaque_id=token,
            right_digest_sha256=referent_sig,
            source_evidence_refs=tuple(pair_refs) + ((ref.evidence_id, ref.sha256),),
            assistance_ancestry=("NATIVE_REFERENT_TOKEN_PAIR_EVIDENCE", "EXTERNAL_RESEARCH_TRAIN_HOLDOUT_PARTITION_ONLY", "NO_TOKEN_MEANING_SUPPLIED", "OPERATIONAL_EQUIVALENCE_CLASS_ONLY"),
        )
        records.append({"opaque_token": token, "operational_referent_signature_sha256": referent_sig, "record_id": rec["record_id"]})
    return {**NONE, "status": "NATIVE_OPAQUE_TOKEN_REFERENT_BINDINGS_DERIVED", "binding_set_id": payload["binding_set_id"], "binding_evidence_id": ref.evidence_id, "binding_evidence_sha256": ref.sha256, "bindings": bindings, "association_records": records, "qualification_ancestry": payload["qualification_ancestry"], "identity_scope": payload["identity_scope"], "authority_gain": "NONE"}


def resolve_native_token_referent(ms: Microseed, *, binding_evidence_id: str, opaque_token: str, current_profile_evidence_id: str):
    brow = ms.evidence.get(binding_evidence_id)
    prow = ms.evidence.get(current_profile_evidence_id)
    if brow is None or (brow.get("payload") or {}).get("kind") != "DERIVED_NATIVE_OPAQUE_TOKEN_REFERENT_BINDING_EVIDENCE":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "DURABLE_NATIVE_TOKEN_REFERENT_BINDING_EVIDENCE_REQUIRED"}
    if prow is None or (prow.get("payload") or {}).get("kind") != "OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "CURRENT_NATIVE_REFERENT_PROFILE_EVIDENCE_REQUIRED"}
    profile = prow["payload"]
    if int(profile.get("runtime_boot_seq", -1)) != ms._current_runtime_boot_seq():
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "FRESH_CURRENT_RUNTIME_OWNED_REFERENT_PROFILE_WITNESS_REQUIRED"}
    matches = [item for item in brow["payload"].get("bindings", []) if str(item.get("opaque_token")) == str(opaque_token)]
    if len(matches) != 1:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "OPAQUE_TOKEN_NOT_GROUNDED_BY_NATIVE_REFERENT_PAIRED_EVIDENCE"}
    expected = str(matches[0]["operational_referent_signature_sha256"])
    observed = str(profile.get("operational_referent_signature_sha256", ""))
    if expected != observed:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TOKEN_BINDING_DOES_NOT_MATCH_CURRENT_NATIVE_REFERENT"}
    records = [rec for rec in ms.opaque_evidence_associations.records.values() if rec.left_opaque_id == str(opaque_token) and rec.right_digest_sha256 == expected]
    if len(records) != 1:
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "UNIQUE_NATIVE_TOKEN_REFERENT_ASSOCIATION_RECORD_REQUIRED"}
    currentness = ms.assess_opaque_evidence_association_currentness(records[0].record_id, witness_evidence_id=current_profile_evidence_id)
    if currentness.get("status") != "CURRENTNESS_CONFIRMED":
        return {**NONE, "status": "DEFER_UNKNOWN", "reason": "TOKEN_NATIVE_REFERENT_ASSOCIATION_NOT_CURRENT", "currentness": currentness}
    return {**NONE, "status": "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT", "opaque_token": str(opaque_token), "operational_referent_signature_sha256": observed, "binding_set_id": str(brow["payload"]["binding_set_id"]), "association_record_id": records[0].record_id, "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY", "authority_gain": "NONE"}


def _pair_episode(ms, world, *, tag, locus, token, index, phase):
    loc = _localized_passive_referent_event(ms, world, tag=tag, locus=locus)
    assert loc["status"] == "CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED", loc
    tok = observe_opaque_token(ms, token, index, phase=phase)
    assert tok["status"] == "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE", tok
    pair = _derive_latest_localization_token_pair(ms, evidence_id=f"E-C08F-PAIR-{phase}-{index}")
    assert pair["status"] == "CURRENT_OWNED_OPAQUE_TOKEN_NATIVE_REFERENT_PAIR_RECORDED", pair
    assert pair["operational_referent_signature_sha256"] == loc["operational_referent_signature_sha256"]
    return pair


def run_campaign(token_x="R4", token_y="T9", sensor_transform=None):
    with tempfile.TemporaryDirectory(prefix="lang-c08f-native-token-referent-") as td:
        root = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform
        ms1 = Microseed(root)
        try:
            _attach_runtime_surface(ms1, world, "C08F-R1")
            profiles1 = _fresh_profiles(ms1, world, tag="R1", serial_base=0)
            by_action1 = {p["exclusive_action_id"]: p for p in profiles1["profiles"]}
            sig_x = str(by_action1["QX"]["operational_referent_signature_sha256"])
            sig_y = str(by_action1["QY"]["operational_referent_signature_sha256"])
            assert sig_x != sig_y
            action_ids_before = set(ms1.capabilities.contracts)
            train, hold = [], []
            for i in range(20):
                locus = "X" if i % 2 == 0 else "Y"
                token = token_x if locus == "X" else token_y
                train.append(_pair_episode(ms1, world, tag=f"TRAIN-{i}", locus=locus, token=token, index=i, phase="TRAIN")["pair_evidence_id"])
            for i in range(10):
                locus = "Y" if i % 2 == 0 else "X"
                token = token_y if locus == "Y" else token_x
                hold.append(_pair_episode(ms1, world, tag=f"HOLD-{i}", locus=locus, token=token, index=100+i, phase="HOLD")["pair_evidence_id"])
            bindings = derive_native_token_referent_bindings(ms1, training_pair_evidence_ids=train, holdout_pair_evidence_ids=hold, evidence_id="E-C08F-BINDING-SET")
            assert bindings["status"] == "NATIVE_OPAQUE_TOKEN_REFERENT_BINDINGS_DERIVED", bindings
            mapping = {x["opaque_token"]: x["operational_referent_signature_sha256"] for x in bindings["bindings"]}
            assert mapping[token_x] == sig_x and mapping[token_y] == sig_y
            rx = resolve_native_token_referent(ms1, binding_evidence_id=bindings["binding_evidence_id"], opaque_token=token_x, current_profile_evidence_id=by_action1["QX"]["evidence_id"])
            ry = resolve_native_token_referent(ms1, binding_evidence_id=bindings["binding_evidence_id"], opaque_token=token_y, current_profile_evidence_id=by_action1["QY"]["evidence_id"])
            assert rx["status"] == ry["status"] == "OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT"
            unseen = resolve_native_token_referent(ms1, binding_evidence_id=bindings["binding_evidence_id"], opaque_token="UNSEEN", current_profile_evidence_id=by_action1["QX"]["evidence_id"])
            wrong = resolve_native_token_referent(ms1, binding_evidence_id=bindings["binding_evidence_id"], opaque_token=token_x, current_profile_evidence_id=by_action1["QY"]["evidence_id"])
            assert unseen["status"] == wrong["status"] == "DEFER_UNKNOWN"

            rev_hold=[]
            for i in range(10):
                locus = "X" if i % 2 == 0 else "Y"
                wrong_token = token_y if locus == "X" else token_x
                rev_hold.append(_pair_episode(ms1, world, tag=f"REV-{i}", locus=locus, token=wrong_token, index=200+i, phase="REV")["pair_evidence_id"])
            reversal=derive_native_token_referent_bindings(ms1,training_pair_evidence_ids=train,holdout_pair_evidence_ids=rev_hold,evidence_id="E-C08F-REVERSAL")
            assert reversal["status"]=="DEFER_UNKNOWN" and reversal["reason"]=="HOLDOUT_TOKEN_NATIVE_REFERENT_ASSOCIATION_DISAGREES"
            ambiguous=list(hold)
            ambiguous[0]=_pair_episode(ms1,world,tag="AMB",locus="X",token=token_y,index=300,phase="AMB")["pair_evidence_id"]
            ambiguity=derive_native_token_referent_bindings(ms1,training_pair_evidence_ids=train,holdout_pair_evidence_ids=ambiguous,evidence_id="E-C08F-AMBIGUITY")
            assert ambiguity["status"]=="DEFER_UNKNOWN"
            binding_evidence_id=str(bindings["binding_evidence_id"])
            record_ids=[r["record_id"] for r in bindings["association_records"]]
            old_profile_x=str(by_action1["QX"]["evidence_id"])
            assert set(ms1.capabilities.contracts)==action_ids_before
        finally:
            _close(ms1)

        ms2=Microseed(root)
        try:
            states={rid:ms2.opaque_evidence_association_status(rid)["status"] for rid in record_ids}
            assert set(states.values())=={"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}
            old=resolve_native_token_referent(ms2,binding_evidence_id=binding_evidence_id,opaque_token=token_x,current_profile_evidence_id=old_profile_x)
            assert old["status"]=="DEFER_UNKNOWN" and old["reason"]=="FRESH_CURRENT_RUNTIME_OWNED_REFERENT_PROFILE_WITNESS_REQUIRED"
            _attach_runtime_surface(ms2,world,"C08F-R2")
            profiles2=_fresh_profiles(ms2,world,tag="R2",serial_base=1000)
            by_action2={p["exclusive_action_id"]:p for p in profiles2["profiles"]}
            assert str(by_action2["QX"]["operational_referent_signature_sha256"])==sig_x
            assert str(by_action2["QY"]["operational_referent_signature_sha256"])==sig_y
            fresh=resolve_native_token_referent(ms2,binding_evidence_id=binding_evidence_id,opaque_token=token_x,current_profile_evidence_id=by_action2["QX"]["evidence_id"])
            wrong2=resolve_native_token_referent(ms2,binding_evidence_id=binding_evidence_id,opaque_token=token_x,current_profile_evidence_id=by_action2["QY"]["evidence_id"])
            assert fresh["status"]=="OPAQUE_TOKEN_RESOLVES_CURRENT_NATIVE_OPERATIONAL_REFERENT"
            assert wrong2["status"]=="DEFER_UNKNOWN"
            return {
                "status":"C08F_NATIVE_OBSERVED_TOKEN_REFERENT_BINDING_REEMBODIED",
                "technical_name":"Evidence-ledger grounding of opaque observed tokens to restart-safe native operational referent equivalence classes",
                "referent_x_signature_sha256":sig_x,"referent_y_signature_sha256":sig_y,
                "bindings":bindings["bindings"],"token_x_resolution":rx["status"],"token_y_resolution":ry["status"],
                "unseen_token":unseen["status"],"wrong_referent":wrong["status"],"holdout_reversal":{"status":reversal["status"],"reason":reversal["reason"]},"ambiguous_holdout":ambiguity["status"],
                "association_states_after_restart":states,"durable_binding_without_fresh_referent":{"status":old["status"],"reason":old["reason"]},
                "post_restart_native_resolution":fresh["status"],"post_restart_wrong_referent":wrong2["status"],
                "identity_scope":"OPERATIONAL_EQUIVALENCE_CLASS_ONLY","numerical_identity_authority":"NONE",
                "caller_supplied_token_meaning":"NO","caller_supplied_referent_class":"NO","pairing_basis":"CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY",
                "qualification_ancestry":bindings["qualification_ancestry"],"new_microseed_action_contracts_registered":[],
                "truth_authority":"NONE","semantic_authority":"NONE","execution_authority":"NONE","language_authority":"NONE",
                "not_earned":["NUMERICAL_OBJECT_IDENTITY","SEMANTIC_REFERENCE","TOKEN_MEANING","SEMANTIC_PREDICATE","LANGUAGE_FACULTY","GENERIC_CAPABILITY_FACULTY","ENDOGENOUS_QUALIFICATION","TAMPER_EVIDENT_LEDGER_SEQUENCE","CANON_PROMOTION"],
            }
        finally:
            _close(ms2)


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
