from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from microseed import (
    Authority,
    CapabilityContract,
    Observation,
    QualificationState,
    QueryObligation,
    RecruitmentOption,
    FeasibilityState,
    RehearsalTransitionObservation,
)
from scratch.ms2008_referent_ambiguity_becomes_decision_bearing import _setup, _close


class OpaqueTwoLocusWorld:
    """Evaluator world only; Microseed receives opaque raw tuples and action outcomes."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.value = -1.0
        self.sensor_transform = lambda row: tuple(row)

    def raw(self):
        row = (self.x, self.x, self.y, self.y)
        return tuple(self.sensor_transform(row))

    def observe(self):
        return {
            "next_state_id": "s0",
            "value_id": "V",
            "observed_value": self.value,
            "raw_tokens": [str(x) for x in self.raw()],
        }

    def apply(self, action: str):
        if action == "QX":
            self.x += 1
        elif action == "QY":
            self.y += 1
        else:
            raise AssertionError(action)
        self.value += 0.25
        return {"receipt": action}

    def set_passive_baseline(self, x: int, y: int):
        self.x = x
        self.y = y

    def apply_passive_xy_to_yx(self):
        # Evaluator-only latent description. Microseed observes only before/after raw content.
        self.x, self.y = self.y, self.x


ACT = QueryObligation("C08C-ACT", "opaque body effect", Authority.EFFECT, operational_scope_id="S")
OBS = QueryObligation("C08C-OBS", "opaque raw observation", Authority.OBSERVATION_ONLY, operational_scope_id="S")
BASIS = QueryObligation("C08C-BASIS", "observation basis", Authority.DERIVED_READ_ONLY, operational_scope_id="S")


def _attach_body(ms, world: OpaqueTwoLocusWorld):
    for cid in ("QX", "QY"):
        ms.register_capability(
            CapabilityContract(
                cid,
                "opaque low-level body action",
                {},
                {},
                (),
                (),
                Authority.EFFECT,
                ("C08C",),
                "CURRENT",
                {},
                query_obligation_id="C08C-ACT",
                qualification=QualificationState.SHADOW_QUALIFIED,
                handler=lambda _cid=cid, **_: world.apply(_cid),
                operational_scope_id="S",
            )
        )
        ms.frames.bind_capability("F", cid)
    ms.register_capability(
        CapabilityContract(
            "C08C-OBS-RAW",
            "opaque raw observation",
            {},
            {},
            (),
            (),
            Authority.OBSERVATION_ONLY,
            ("C08C",),
            "CURRENT",
            {},
            query_obligation_id="C08C-OBS",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: world.observe(),
            operational_scope_id="S",
        )
    )
    ms.register_capability(
        CapabilityContract(
            "C08C-OBS-BASIS",
            "opaque observation basis",
            {},
            {},
            (),
            (),
            Authority.DERIVED_READ_ONLY,
            ("C08C",),
            "CURRENT",
            {},
            dependencies=("C08C-OBS-RAW",),
            query_obligation_id="C08C-BASIS",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"claim": "BOUND"},
            operational_scope_id="S",
        )
    )
    ms.frames.bind_capability("F", "C08C-OBS-RAW")


def _proposal(ms, cid: str, serial: int):
    ms.observe_value_state("V", -1.0)
    rows = tuple(
        RehearsalTransitionObservation(
            f"C08C-SEED-{cid}-{serial}-{i}", "s0", cid, "s0", 0.5, 0, "F", 0, "EP", 0
        )
        for i in range(8)
    )
    proposal = ms.nominate_counterfactual_rehearsal(
        rows,
        (RecruitmentOption(cid, FeasibilityState.FEASIBLE, local_cost=0.1),),
        start_state_id="s0",
        value_id="V",
    )
    assert proposal is not None, (cid, serial)
    return proposal


def _raw(ms, tag: str):
    result = ms.record_bounded_raw_observation_coordinates(
        "C08C-OBS-RAW",
        OBS,
        evidence_id=f"E-C08C-RAW-{tag}",
        capture_id=f"CAP-C08C-RAW-{tag}",
        max_coordinates=8,
    )
    assert result["status"] == "BOUNDED_RAW_OBSERVATION_RECORDED", result
    return result


def _execute(ms, cid: str, tag: str, serial: int):
    proposal = _proposal(ms, cid, serial)
    nomination = ms.nominate_bounded_action_intent(proposal.proposal_id, ACT)
    assert nomination["status"] == "ACTION_INTENT_NOMINATED", nomination
    execution = ms.execute_bounded_action(nomination["intent"]["intent_id"], ACT)
    assert execution["status"] == "ACTION_EXECUTED", execution
    outcome = ms.record_bounded_action_outcome_via_observation_basis(
        execution["execution"]["execution_id"],
        observation_capability_id="C08C-OBS-RAW",
        observation_obligation=OBS,
        basis_capability_id="C08C-OBS-BASIS",
        basis_obligation=BASIS,
        evidence_id=f"E-C08C-OUT-{tag}",
        capture_id=f"CAP-C08C-OUT-{tag}",
    )
    assert outcome["status"] == "ACTION_OUTCOME_OBSERVED", outcome
    return outcome


def _external_control_state(ms, tag: str):
    result = ms.observe_opaque_control_state(
        Observation(
            f"CAP-C08C-STATE-{tag}",
            "EXTERNAL-WORLD",
            "opaque-control-state",
            f"c08c-external-{tag}",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-C08C-STATE-{tag}",
    )
    assert result["status"] == "CURRENT_OPAQUE_CONTROL_STATE", result
    return result


def run_campaign(sensor_transform=None) -> dict[str, object]:
    td, ms, _calls, _bid, _ba, _bb = _setup(False)
    world = OpaqueTwoLocusWorld()
    if sensor_transform is not None:
        world.sensor_transform = sensor_transform
    try:
        _attach_body(ms, world)
        action_ids_before = set(ms.capabilities.contracts)

        # Native owned body history. The harness supplies no channel groups or referent classes.
        _raw(ms, "P0")
        for serial, (cid, tag) in enumerate((("QX", "X0"), ("QX", "X1"), ("QY", "Y0"), ("QY", "Y1"))):
            _execute(ms, cid, tag, serial)
            _raw(ms, f"P{serial + 1}")

        profiles = ms.record_current_owned_affordance_effect_profiles(
            evidence_id_prefix="E-C08C-PROFILE", max_probe_steps=4
        )
        assert profiles["status"] == "CURRENT_OWNED_AFFORDANCE_EFFECT_PROFILES_RECORDED", profiles
        assert profiles["profile_count"] == 2, profiles
        assert {p["exclusive_action_id"] for p in profiles["profiles"]} == {"QX", "QY"}, profiles
        assert all(p["referent_signature_evidence_ref"] for p in profiles["profiles"])

        # Evaluator chooses only world state / event timing. Microseed receives opaque state/raw evidence.
        world.set_passive_baseline(2, 1)
        _external_control_state(ms, "PRE-1")
        before = _raw(ms, "PASSIVE-PRE-1")
        world.apply_passive_xy_to_yx()  # (2,1) -> (1,2)
        _external_control_state(ms, "POST-1")
        after = _raw(ms, "PASSIVE-POST-1")

        passive = ms.derive_current_owned_passive_raw_transition(max_events=4096)
        assert passive["status"] == "CURRENT_OWNED_PASSIVE_RAW_TRANSITION", passive
        assert passive["before_raw_evidence_id"] == before["evidence_id"]
        assert passive["after_raw_evidence_id"] == after["evidence_id"]

        relation = ms.derive_and_record_current_owned_affordance_relative_directional_relation(
            evidence_id="E-C08C-REL-1", max_events=4096, max_records=4096
        )
        assert relation["status"] == "CURRENT_OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_RECORDED", relation
        assert relation["caller_supplied_relation_order"] == "NO"
        assert relation["caller_supplied_relation_digest"] == "NO"
        assert relation["coordinate_arithmetic"] == "NONE"
        assert len(relation["ordered_operational_referent_signatures"]) == 2
        assert {d["orientation"] for d in relation["diagnostic"]} == {
            "REVERSES_LOCAL_GROUNDED_TRANSITION",
            "REPRODUCES_LOCAL_GROUNDED_TRANSITION",
        }

        by_action = {
            p["exclusive_action_id"]: p["operational_referent_signature_sha256"]
            for p in profiles["profiles"]
        }
        # Evaluator-only scoring check; these labels never enter derivation.
        assert relation["ordered_operational_referent_signatures"] == [by_action["QX"], by_action["QY"]]

        # The C08A registry now consumes the owned relation evidence by evidence id only.
        rel_row = ms.evidence.get(relation["evidence_id"])
        assoc = ms.register_opaque_evidence_association(
            left_opaque_id="C08C-OPAQUE-ASSOCIATION-HANDLE",
            right_digest_sha256=relation["relation_digest_sha256"],
            source_evidence_refs=((relation["evidence_id"], rel_row["sha256"]),),
            assistance_ancestry=("C08C-OWNED-RELATION-EVIDENCE", "NO-HARNESS-RELATION-DIGEST"),
        )
        confirmed = ms.assess_opaque_evidence_association_currentness(
            assoc["record_id"], witness_evidence_id=relation["evidence_id"]
        )
        assert confirmed["status"] == "CURRENTNESS_CONFIRMED", confirmed
        assert confirmed["record_state"] == "CURRENT"

        # Reverse the empirical direction. The native digest must change and stale only this association.
        world.set_passive_baseline(1, 2)
        _external_control_state(ms, "PRE-2")
        _raw(ms, "PASSIVE-PRE-2")
        world.apply_passive_xy_to_yx()  # (1,2) -> (2,1)
        _external_control_state(ms, "POST-2")
        _raw(ms, "PASSIVE-POST-2")
        reversed_relation = ms.derive_and_record_current_owned_affordance_relative_directional_relation(
            evidence_id="E-C08C-REL-2", max_events=4096, max_records=4096
        )
        assert reversed_relation["status"] == "CURRENT_OWNED_AFFORDANCE_RELATIVE_DIRECTIONAL_RELATION_RECORDED", reversed_relation
        assert reversed_relation["ordered_operational_referent_signatures"] == [by_action["QY"], by_action["QX"]]
        assert reversed_relation["relation_digest_sha256"] != relation["relation_digest_sha256"]
        drift = ms.assess_opaque_evidence_association_currentness(
            assoc["record_id"], witness_evidence_id=reversed_relation["evidence_id"]
        )
        assert drift["status"] == "DRIFT_WITNESS", drift
        assert drift["record_state"] == "STALE"

        action_ids_after = set(ms.capabilities.contracts)
        assert action_ids_after == action_ids_before
        assert not hasattr(ms, "predicate_registry")
        assert not hasattr(ms, "meaning_registry")
        assert not hasattr(ms, "language_module")
        assert not hasattr(ms, "faculty_registry")

        return {
            "status": "C08C_NATIVE_B1_C06_RELATION_EVIDENCE_OWNER_EARNED_LIVE_RUNTIME",
            "profile_count": profiles["profile_count"],
            "owned_referent_signature_evidence": [
                p["referent_signature_evidence_ref"] for p in profiles["profiles"]
            ],
            "owned_relation_evidence_id": relation["evidence_id"],
            "relation_digest_sha256": relation["relation_digest_sha256"],
            "reversed_relation_digest_sha256": reversed_relation["relation_digest_sha256"],
            "ordered_operational_referent_signatures": relation["ordered_operational_referent_signatures"],
            "reversed_order": reversed_relation["ordered_operational_referent_signatures"],
            "association_currentness_from_owned_relation_evidence": confirmed["status"],
            "empirical_reversal": drift["status"],
            "new_action_contracts_registered": [],
            "caller_supplied_referent_groups": "NO",
            "caller_supplied_relation_order": "NO",
            "caller_supplied_relation_digest": "NO",
            "coordinate_arithmetic": "NONE",
            "semantic_authority": "NONE",
            "truth_authority": "NONE",
            "execution_authority": "NONE",
            "language_authority": "NONE",
            "not_earned": [
                "C07_TOKEN_BINDING_REEMBODIMENT",
                "POST_RESTART_NATIVE_RELATION_REDERIVATION",
                "SEMANTIC_PREDICATE",
                "TOKEN_MEANING",
                "LANGUAGE_FACULTY",
                "GENERIC_CAPABILITY_FACULTY",
                "CANON_PROMOTION",
            ],
        }
    finally:
        _close(ms)
        td.cleanup()


def main():
    print(json.dumps(run_campaign(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
