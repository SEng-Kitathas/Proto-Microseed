from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import Microseed
from scratch.lang_c08c_native_owned_affordance_relation import _external_control_state, _raw
from scratch.lang_c08d_postrestart_native_relation_rederivation import (
    OpaqueTwoLocusWorld,
    _attach_runtime_surface,
    _close,
    _fresh_owned_relation,
)
from scratch.lang_c08e_native_token_relation_binding import _native_relation_episode, observe_opaque_token


def _passive_referent_exposure(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    tag: str,
    locus: str,
    token: str,
    index: int,
    phase: str,
) -> dict[str, object]:
    """External world presents a passive referent event and opaque token.

    The harness owns only the exogenous event/token presentation. Microseed must derive
    the referent localization itself; no pair evidence or pair witness is created here.
    """
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
    localized = ms.derive_and_record_current_owned_passive_operational_referent_localization(
        max_events=16384,
        max_records=16384,
    )
    assert localized["status"] == "CURRENT_OWNED_PASSIVE_OPERATIONAL_REFERENT_LOCALIZED", localized
    observed = observe_opaque_token(ms, token, index, phase=phase)
    assert observed["status"] == "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE", observed
    return {"localization": localized, "token_observation": observed}


def _relation_exposure(
    ms: Microseed,
    world: OpaqueTwoLocusWorld,
    *,
    tag: str,
    reverse: bool,
    token: str,
    index: int,
    phase: str,
) -> dict[str, object]:
    """External world presents one relation event and opaque token; no pair is supplied."""
    relation = _native_relation_episode(ms, world, tag=tag, reverse=reverse)
    observed = observe_opaque_token(ms, token, index, phase=phase)
    assert observed["status"] == "OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE", observed
    return {"relation": relation, "token_observation": observed}


def _qualification_mapping(lifecycle: dict[str, object], scope: str) -> dict[str, str]:
    result = lifecycle["qualifications"]["results"][scope]
    qualification = result["qualification"]
    return {str(left): str(right) for left, right in qualification["bindings"]}


def _registration_records(lifecycle: dict[str, object], scope: str) -> dict[str, str]:
    result = lifecycle["registrations"][scope]
    return {str(rec["left_opaque_id"]): str(rec["record_id"]) for rec in result["records"]}


def run_campaign(
    token_x: str = "R4",
    token_y: str = "T9",
    relation_normal_token: str = "K7",
    relation_reverse_token: str = "M2",
    sensor_transform=None,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="lang-c08i-native-pair-harvest-") as td:
        root = Path(td)
        world = OpaqueTwoLocusWorld()
        if sensor_transform is not None:
            world.sensor_transform = sensor_transform

        ms1 = Microseed(root)
        try:
            _attach_runtime_surface(ms1, world, "C08I-R1")
            shared_seed = _fresh_owned_relation(ms1, world, tag="C08I-SHARED-SEED", serial_base=0)
            profiles = {p["exclusive_action_id"]: p for p in shared_seed["profiles"]["profiles"]}
            sig_x = str(profiles["QX"]["operational_referent_signature_sha256"])
            sig_y = str(profiles["QY"]["operational_referent_signature_sha256"])
            normal_digest = str(shared_seed["relation"]["relation_digest_sha256"])
            action_ids_before = set(ms1.capabilities.contracts)

            referent_exposures = []
            for i in range(6):
                locus = "X" if i % 2 == 0 else "Y"
                token = token_x if locus == "X" else token_y
                referent_exposures.append(_passive_referent_exposure(
                    ms1, world, tag=f"C08I-REF-{i}", locus=locus, token=token,
                    index=i, phase="C08I-REF",
                ))

            relation_exposures = []
            for i in range(6):
                reverse = bool(i % 2)
                token = relation_reverse_token if reverse else relation_normal_token
                relation_exposures.append(_relation_exposure(
                    ms1, world, tag=f"C08I-REL-{i}", reverse=reverse, token=token,
                    index=100 + i, phase="C08I-REL",
                ))

            pre_pair_rows = [
                row for row in ms1.evidence.list()
                if (row.get("payload") or {}).get("kind") in {
                    "OWNED_OPAQUE_TOKEN_NATIVE_REFERENT_PAIR_EVIDENCE",
                    "OWNED_OPAQUE_TOKEN_NATIVE_RELATION_PAIR_EVIDENCE",
                }
            ]
            assert pre_pair_rows == [], pre_pair_rows
            assert ms1.opaque_evidence_associations.pair_witnesses == {}

            lifecycle = ms1.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=16384)
            assert lifecycle["status"] == "HARVESTED_NATIVE_OPAQUE_ASSOCIATIONS_EPISTEMICALLY_QUALIFIED_AND_REGISTERED", lifecycle
            harvest = lifecycle["harvest"]
            assert harvest["harvested_pair_count"] == 12, harvest
            assert harvest["caller_supplied_pair_ids"] == "NO"
            assert harvest["caller_supplied_association_scope"] == "NO"
            assert lifecycle["caller_supplied_mapping_answer"] == "NO"
            assert lifecycle["caller_supplied_qualification_id"] == "NO"
            assert set(lifecycle["qualifications"]["scopes"]) == {"NATIVE_TOKEN_REFERENT", "NATIVE_TOKEN_RELATION"}
            assert set(lifecycle["registrations"]) == {"NATIVE_TOKEN_REFERENT", "NATIVE_TOKEN_RELATION"}

            ref_map = _qualification_mapping(lifecycle, "NATIVE_TOKEN_REFERENT")
            rel_map = _qualification_mapping(lifecycle, "NATIVE_TOKEN_RELATION")
            assert ref_map == {token_x: sig_x, token_y: sig_y}, (ref_map, sig_x, sig_y)
            assert rel_map[relation_normal_token] == normal_digest
            reverse_digest = rel_map[relation_reverse_token]
            assert reverse_digest != normal_digest

            ref_records = _registration_records(lifecycle, "NATIVE_TOKEN_REFERENT")
            rel_records = _registration_records(lifecycle, "NATIVE_TOKEN_RELATION")
            assert len(ref_records) == len(rel_records) == 2

            assert ms1.assess_opaque_evidence_association_currentness(
                ref_records[token_x], witness_evidence_id=str(profiles["QX"]["evidence_id"])
            )["status"] == "CURRENTNESS_CONFIRMED"
            assert ms1.assess_opaque_evidence_association_currentness(
                ref_records[token_y], witness_evidence_id=str(profiles["QY"]["evidence_id"])
            )["status"] == "CURRENTNESS_CONFIRMED"

            relation_witness_by_digest = {normal_digest: str(shared_seed["relation"]["evidence_id"])}
            for exposure in relation_exposures:
                rel = exposure["relation"]
                relation_witness_by_digest[str(rel["relation_digest_sha256"])] = str(rel["evidence_id"])
            assert ms1.assess_opaque_evidence_association_currentness(
                rel_records[relation_normal_token], witness_evidence_id=relation_witness_by_digest[normal_digest]
            )["status"] == "CURRENTNESS_CONFIRMED"
            assert ms1.assess_opaque_evidence_association_currentness(
                rel_records[relation_reverse_token], witness_evidence_id=relation_witness_by_digest[reverse_digest]
            )["status"] == "CURRENTNESS_CONFIRMED"

            # A truncated evidence view cannot be used to infer chronology.
            budget = ms1.harvest_current_opaque_evidence_association_pairs(max_records=max(1, ms1.evidence.count() - 1))
            assert budget["status"] == "SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED", budget

            # Idempotent replay of the same complete current evidence does not create new pair identities.
            before_count = ms1.evidence.count()
            repeat = ms1.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=16384)
            assert repeat["status"] == "HARVESTED_NATIVE_OPAQUE_ASSOCIATIONS_EPISTEMICALLY_QUALIFIED_AND_REGISTERED", repeat
            assert ms1.evidence.count() == before_count, (before_count, ms1.evidence.count())
            assert set(ms1.capabilities.contracts) == action_ids_before

            ref_qid = str(lifecycle["qualifications"]["results"]["NATIVE_TOKEN_REFERENT"]["qualification"]["qualification_id"])
            rel_qid = str(lifecycle["qualifications"]["results"]["NATIVE_TOKEN_RELATION"]["qualification"]["qualification_id"])
        finally:
            _close(ms1)

        ms2 = Microseed(root)
        try:
            assert ms2.opaque_evidence_association_qualification_status(ref_qid)["status"] == "CURRENT_EPISTEMIC_ASSOCIATION_ADEQUACY"
            assert ms2.opaque_evidence_association_qualification_status(rel_qid)["status"] == "CURRENT_EPISTEMIC_ASSOCIATION_ADEQUACY"
            no_current = ms2.harvest_current_opaque_evidence_association_pairs(max_records=16384)
            assert no_current["status"] == "DEFER_UNKNOWN"
            assert no_current["reason"] == "CURRENT_RUNTIME_OPAQUE_TOKEN_EVIDENCE_REQUIRED"

            _attach_runtime_surface(ms2, world, "C08I-R2")
            restarted = _fresh_owned_relation(ms2, world, tag="C08I-R2-SEED", serial_base=3000)
            profiles2 = {p["exclusive_action_id"]: p for p in restarted["profiles"]["profiles"]}
            assert str(profiles2["QX"]["operational_referent_signature_sha256"]) == sig_x
            assert str(profiles2["QY"]["operational_referent_signature_sha256"]) == sig_y
            assert ms2.assess_opaque_evidence_association_currentness(
                ref_records[token_x], witness_evidence_id=str(profiles2["QX"]["evidence_id"])
            )["status"] == "CURRENTNESS_CONFIRMED"

            # One contradictory new lived co-occurrence is auto-harvested and invalidates prior adequacy.
            _passive_referent_exposure(
                ms2, world, tag="C08I-CONTRADICTION", locus="X", token=token_y,
                index=900, phase="C08I-CONTRADICTION",
            )
            contradiction = ms2.harvest_qualify_and_register_current_opaque_evidence_associations(max_records=16384)
            assert contradiction["status"] == "PAIR_EVIDENCE_HARVESTED_QUALIFICATION_INCOMPLETE", contradiction
            ref_result = contradiction["qualifications"]["results"]["NATIVE_TOKEN_REFERENT"]
            assert ref_result["status"] == "DEFER_UNKNOWN"
            assert ref_result["reason"] == "PAIR_EVIDENCE_NOT_EXACT_BIJECTION"
            assert ms2.opaque_evidence_association_qualification_status(ref_qid)["status"] == "REVALIDATION_REQUIRED_EPISTEMIC_ASSOCIATION_QUALIFICATION"
            assert set(ms2.opaque_evidence_association_status(rid)["status"] for rid in ref_records.values()) == {"REVALIDATION_REQUIRED_OPAQUE_EVIDENCE_ASSOCIATION"}

            return {
                "status": "C08I_NATIVE_OPAQUE_ASSOCIATION_PAIR_HARVEST_EARNED",
                "technical_name": "Bounded organism-owned harvesting of current opaque token/grounded-source chronology into native association evidence",
                "harvested_pair_count": harvest["harvested_pair_count"],
                "harvested_scopes": list(lifecycle["qualifications"]["scopes"]),
                "referent_bindings": sorted(ref_map.items()),
                "relation_bindings": sorted(rel_map.items()),
                "referent_qualification_id": ref_qid,
                "relation_qualification_id": rel_qid,
                "budget_hostile": {"status": budget["status"], "reason": budget["reason"]},
                "restart_without_current_token": {"status": no_current["status"], "reason": no_current["reason"]},
                "contradiction": {"status": contradiction["status"], "referent_reason": ref_result["reason"]},
                "caller_supplied_pair_evidence_ids": "NO",
                "caller_supplied_association_scope": "NO",
                "caller_supplied_mapping_answer": "NO",
                "caller_supplied_qualification_id": "NO",
                "caller_supplied_referent_class": "NO",
                "external_train_holdout_partition": "NONE",
                "pairing_basis": "AUTO_HARVESTED_CURRENT_RUNTIME_EVIDENCE_LEDGER_CHRONOLOGY",
                "identity_scope": "OPERATIONAL_EQUIVALENCE_CLASS_ONLY",
                "qualification_authority": "EPISTEMIC_ADEQUACY_EVIDENCE_ONLY",
                "experience_generation": "EXOGENOUS_PASSIVE_EVENT_AND_OPAQUE_TOKEN_PRESENTATION_REMAIN",
                "new_microseed_action_contracts_registered": [],
                "truth_authority": "NONE",
                "semantic_authority": "NONE",
                "execution_authority": "NONE",
                "language_authority": "NONE",
                "not_earned": [
                    "ENDOGENOUS_ENVIRONMENT_EVENT_GENERATION",
                    "ENDOGENOUS_OPAQUE_TOKEN_GENERATION",
                    "ACTIVE_EXPERIMENT_SELECTION_FOR_MISSING_ASSOCIATION_EVIDENCE",
                    "SEMANTIC_MEANING",
                    "SEMANTIC_PREDICATE",
                    "GRAMMAR",
                    "LANGUAGE_COMPETENCE",
                    "GENERIC_CAPABILITY_FACULTY",
                    "TAMPER_EVIDENT_LEDGER_SEQUENCE",
                    "CANON_PROMOTION",
                ],
            }
        finally:
            _close(ms2)


if __name__ == "__main__":
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))
