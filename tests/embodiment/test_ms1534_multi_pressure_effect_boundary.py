from __future__ import annotations

import hashlib
import random
import tempfile
from pathlib import Path

from microseed import (
    Authority,
    CapabilityContract,
    EpisodeSchemaContract,
    Microseed,
    Observation,
    OperationalFrameContract,
    QualificationState,
    QueryObligation,
    ValueVariableContract,
)
from microseed.development.discovery import DiscoveryConfig, OperationalTrace

VALUES = ("ENERGY", "THERMAL", "INTEGRITY")
BOUNDS = {
    "ENERGY": (4.0, 8.0),
    "THERMAL": (3.0, 7.0),
    "INTEGRITY": (4.0, 9.5),
}
EFFECTS = {
    "HARVEST": (1.55, 0.42, -0.28),
    "COOL": (-0.28, -1.48, -0.12),
    "REPAIR": (-0.38, 0.22, 1.42),
    "REST": (0.42, -0.44, 0.34),
}


def _frame() -> OperationalFrameContract:
    return OperationalFrameContract(
        "F",
        "opaque-regulatory-frame",
        hashlib.sha256(b"F").hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS1534-RESEARCH",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def _value(value_id: str) -> ValueVariableContract:
    low, high = BOUNDS[value_id]
    return ValueVariableContract(
        value_id,
        "opaque-regulatory",
        low,
        high,
        hashlib.sha256(f"{value_id}:{low}:{high}".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS953-977",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=(
            "SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE",
            "SUPPLIED_VIABILITY_INTERVAL",
        ),
    )


def _episode(value_id: str) -> EpisodeSchemaContract:
    schema_id = f"E-{value_id}"
    return EpisodeSchemaContract(
        schema_id,
        "opaque-single-value-effect-binding",
        hashlib.sha256(schema_id.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS1103-1127",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=(("F", 0),),
        value_epochs=((value_id, 0),),
    )


def _obligation() -> QueryObligation:
    return QueryObligation(
        "ACT",
        "bounded-hostile-effect",
        required_authority=Authority.EFFECT,
        operational_scope_id="R2",
    )


def _observe_values(
    ms: Microseed,
    *,
    energy: float,
    thermal: float,
    integrity: float,
) -> None:
    ms.observe_value_state("ENERGY", energy)
    ms.observe_value_state("THERMAL", thermal)
    ms.observe_value_state("INTEGRITY", integrity)


def _seeded(*, samples: int = 61) -> tuple[tempfile.TemporaryDirectory, Microseed, list[str]]:
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1534-")
    ms = Microseed(Path(td.name))
    calls: list[str] = []

    ms.register_operational_frame(_frame())
    for value_id in VALUES:
        ms.register_value_variable(_value(value_id))
        ms.register_episode_schema(_episode(value_id))

    for capability_id in EFFECTS:
        ms.register_capability(CapabilityContract(
            capability_id,
            "opaque-action",
            {},
            {},
            (),
            (),
            Authority.EFFECT,
            ("MS1534-RESEARCH",),
            "CURRENT",
            {},
            query_obligation_id="ACT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _capability_id=capability_id, **_: calls.append(_capability_id) or {"action": _capability_id},
            operational_scope_id="R2",
        ))

    rng = random.Random(1534)
    noise = (0.32, 0.28, 0.30)
    for capability_id, effect_vector in EFFECTS.items():
        for value_index, value_id in enumerate(VALUES):
            for sample in range(samples):
                observed = effect_vector[value_index] + rng.gauss(0.0, noise[value_index])
                ms.record_operational_trace(OperationalTrace(
                    trace_id=f"{capability_id}-{value_id}-{sample}",
                    steps=(capability_id,),
                    step_effects=((observed,),),
                    frame_id="F",
                    episode_schema_id=f"E-{value_id}",
                ))

    ms.observe_opaque_control_state(
        Observation(
            "CTRL-0",
            "EXT",
            "control",
            "R2-OPAQUE-STATE",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id="E-CTRL-0",
    )
    return td, ms, calls


def test_unique_multi_pressure_license_reaches_effect_without_single_value_anchor() -> None:
    td, ms, calls = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())

        assert nominated["status"] == "ACTION_INTENT_NOMINATED"
        intent = nominated["intent"]
        assert intent["basis_kind"] == "MULTI_VALUE_LICENSE"
        assert intent["proposal_id"] is None
        assert intent["proposal_digest"] is None
        assert intent["value_epoch"] is None
        assert intent["expected_value_effect"] is None
        assert intent["required_value_epochs"] == [["ENERGY", 0], ["THERMAL", 0], ["INTEGRITY", 0]]
        assert len(intent["action_commitment"]["premise_ids"]) == 3
        assert intent["execution_authority"] == "NONE"

        executed = ms.execute_bounded_action(intent["intent_id"], _obligation())
        assert executed["status"] == "ACTION_EXECUTED"
        assert calls == ["REST"]
        assert executed["execution"]["execution_commitment_id"]
        assert len(executed["execution"]["execution_premise_ids"]) == 3
        assert executed["execution"]["authority"] == "EFFECT"
        assert executed["execution"]["truth_authority"] == "NONE"
    finally:
        td.cleanup()


def test_execution_rederives_multi_pressure_license_after_value_state_changes() -> None:
    td, ms, calls = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
        assert nominated["status"] == "ACTION_INTENT_NOMINATED"

        _observe_values(ms, energy=6.0, thermal=5.0, integrity=6.0)
        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())

        assert executed["status"] == "NO_EXECUTION"
        assert executed["reason"] == "MULTI_VALUE_ACTION_LICENSE_NOT_CURRENT"
        assert calls == []
    finally:
        td.cleanup()


def test_capability_invalidation_blocks_multi_pressure_intent_at_effect_boundary() -> None:
    td, ms, calls = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
        assert nominated["status"] == "ACTION_INTENT_NOMINATED"

        ms.invalidate_capability("REST", reason="HOSTILE_PROVIDER_DRIFT")
        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())

        assert executed["status"] == "NO_EXECUTION"
        assert executed["reason"] == "EFFECT_CAPABILITY_NOT_CURRENT"
        assert calls == []
    finally:
        td.cleanup()


def test_value_epoch_change_blocks_multi_pressure_intent_without_global_reset() -> None:
    td, ms, calls = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
        assert nominated["status"] == "ACTION_INTENT_NOMINATED"

        ms.change_value_variable("THERMAL", reason="VALUE_CONTRACT_CHANGED")
        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())

        assert executed["status"] == "NO_EXECUTION"
        assert executed["reason"] == "MULTI_VALUE_PREMISE_EPOCH_DRIFT"
        assert calls == []
    finally:
        td.cleanup()


def test_nonunique_license_abstains_without_creating_intent_or_calling_handler() -> None:
    td, ms, calls = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=5.0, integrity=6.0)
        before = len(ms.action_closure.intents)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())

        assert nominated["status"] == "ABSTAIN"
        assert nominated["license"]["status"] == "UNKNOWN_ACTION_SELECTION"
        assert len(ms.action_closure.intents) == before
        assert calls == []
    finally:
        td.cleanup()


def test_derivation_parameters_are_carried_across_nomination_execution_gap() -> None:
    td, ms, calls = _seeded(samples=4)
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        config = DiscoveryConfig(min_singleton_samples=4, quantization_step=0.5)
        nominated = ms.nominate_multi_value_action_intent(
            VALUES,
            _obligation(),
            config=config,
        )
        assert nominated["status"] == "ACTION_INTENT_NOMINATED"
        assert ["min_singleton_samples", 4] in nominated["intent"]["derivation_parameters"]

        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())
        assert executed["status"] == "ACTION_EXECUTED"
        assert calls == ["REST"]
    finally:
        td.cleanup()


def test_multi_pressure_execution_rejects_legacy_single_value_outcome_payload() -> None:
    td, ms, _ = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
        executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())
        execution_id = executed["execution"]["execution_id"]

        outcome = ms.record_bounded_action_outcome(
            execution_id,
            Observation(
                "OUT-1",
                "EXT",
                f"action-execution:{execution_id}",
                {
                    "next_state_id": "R2-NEXT",
                    "value_id": "ENERGY",
                    "observed_value": 3.8,
                },
                authority=Authority.OBSERVATION_ONLY,
            ),
            evidence_id="E-OUT-1",
        )

        assert outcome == {
            "status": "OUTCOME_REJECTED",
            "reason": "MULTI_VALUE_OUTCOME_FIELDS_MISSING",
        }
    finally:
        td.cleanup()


def test_multi_pressure_intent_roundtrip_preserves_ancestry_but_not_authority() -> None:
    td, ms, _ = _seeded()
    try:
        _observe_values(ms, energy=3.2, thermal=7.6, integrity=6.0)
        nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
        intent_id = nominated["intent"]["intent_id"]

        # Re-open the same durable history. Registries/handlers are deliberately
        # not restored as executable authority, but intent ancestry must survive.
        reopened = Microseed(Path(td.name))
        intent = reopened.action_closure.intents[intent_id]
        assert intent.basis_kind == "MULTI_VALUE_LICENSE"
        assert intent.proposal_id is None
        assert intent.required_value_epochs == (("ENERGY", 0), ("THERMAL", 0), ("INTEGRITY", 0))
        assert len(intent.action_commitment.premise_ids) == 3
        assert intent.execution_authority == "NONE"
        assert reopened.capabilities.contracts == {}
    finally:
        td.cleanup()
