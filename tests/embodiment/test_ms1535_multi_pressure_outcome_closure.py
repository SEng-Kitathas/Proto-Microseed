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
from microseed.development.discovery import OperationalTrace

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


def _obligation() -> QueryObligation:
    return QueryObligation("ACT", "bounded-hostile-effect", required_authority=Authority.EFFECT, operational_scope_id="R2")


def _seeded() -> tuple[tempfile.TemporaryDirectory, Microseed, list[str]]:
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1535-")
    ms = Microseed(Path(td.name))
    calls: list[str] = []
    ms.register_operational_frame(OperationalFrameContract(
        "F", "opaque-regulatory-frame", hashlib.sha256(b"F").hexdigest(), Authority.DERIVED_READ_ONLY,
        ("MS1535-RESEARCH",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
    ))
    for value_id in VALUES:
        low, high = BOUNDS[value_id]
        ms.register_value_variable(ValueVariableContract(
            value_id, "opaque-regulatory", low, high, hashlib.sha256(f"{value_id}:{low}:{high}".encode()).hexdigest(),
            Authority.DERIVED_READ_ONLY, ("MS953-977",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_VIABILITY_INTERVAL"),
        ))
        schema_id = f"E-{value_id}"
        ms.register_episode_schema(EpisodeSchemaContract(
            schema_id, "opaque-single-value-effect-binding", hashlib.sha256(schema_id.encode()).hexdigest(),
            Authority.DERIVED_READ_ONLY, ("MS1103-1127",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
            frame_epochs=(("F", 0),), value_epochs=((value_id, 0),),
        ))
    for capability_id in EFFECTS:
        ms.register_capability(CapabilityContract(
            capability_id, "opaque-action", {}, {}, (), (), Authority.EFFECT, ("MS1535-RESEARCH",), "CURRENT", {},
            query_obligation_id="ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _capability_id=capability_id, **_: calls.append(_capability_id) or {"action": _capability_id},
            operational_scope_id="R2",
        ))
    rng = random.Random(1535)
    noise = (0.32, 0.28, 0.30)
    for capability_id, effect_vector in EFFECTS.items():
        for value_index, value_id in enumerate(VALUES):
            for sample in range(61):
                observed = effect_vector[value_index] + rng.gauss(0.0, noise[value_index])
                ms.record_operational_trace(OperationalTrace(
                    trace_id=f"{capability_id}-{value_id}-{sample}", steps=(capability_id,), step_effects=((observed,),),
                    frame_id="F", episode_schema_id=f"E-{value_id}",
                ))
    return td, ms, calls


def _prepare(ms: Microseed, suffix: str) -> str:
    ms.observe_value_state("ENERGY", 3.2)
    ms.observe_value_state("THERMAL", 7.6)
    ms.observe_value_state("INTEGRITY", 6.0)
    ms.observe_opaque_control_state(
        Observation(f"CTRL-{suffix}", "EXT", "control", "R2-OPAQUE-STATE", authority=Authority.OBSERVATION_ONLY),
        evidence_id=f"E-CTRL-{suffix}",
    )
    nominated = ms.nominate_multi_value_action_intent(VALUES, _obligation())
    assert nominated["status"] == "ACTION_INTENT_NOMINATED"
    executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], _obligation())
    assert executed["status"] == "ACTION_EXECUTED"
    return executed["execution"]["execution_id"]


def _outcome(ms: Microseed, execution_id: str, suffix: str, values: dict[str, float]) -> dict:
    return ms.record_bounded_action_outcome(
        execution_id,
        Observation(
            f"OUT-{suffix}", "EXT", f"action-execution:{execution_id}",
            {"next_state_id": "R2-NEXT", "observed_values": values}, authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-OUT-{suffix}",
    )


def test_one_execution_closes_as_one_vector_outcome_without_duplicate_execution_inflation() -> None:
    td, ms, calls = _seeded()
    try:
        execution_id = _prepare(ms, "ONE")
        result = _outcome(ms, execution_id, "ONE", {"ENERGY": 3.65, "THERMAL": 7.15, "INTEGRITY": 6.33})
        assert result["status"] == "ACTION_OUTCOME_OBSERVED"
        assert calls == ["REST"]
        assert len(ms.action_closure.outcomes) == 1
        outcome = result["outcome"]
        assert outcome["execution_id"] == execution_id
        assert outcome["value_id"] is None
        assert outcome["observed_value"] is None
        assert outcome["actual_value_effect"] is None
        assert [row["value_id"] for row in outcome["value_outcomes"]] == list(VALUES)
        assert all(row["truth_authority"] == "NONE" for row in outcome["value_outcomes"])
        assert outcome["prediction_commitment"]["commitment"] == "UNKNOWN"
        assert outcome["prediction_commitment"]["reason"] == "MULTI_VALUE_PREDICTION_MATCH_NOT_CLAIMED"
    finally:
        td.cleanup()


def test_missing_coordinate_remains_local_without_fabricating_complete_vector() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "MISS")
        result = _outcome(ms, execution_id, "MISS", {"ENERGY": 3.65, "THERMAL": 7.15})
        assert result["status"] == "ACTION_OUTCOME_OBSERVED"
        assert result["missing_value_ids"] == ["INTEGRITY"]
        rows = result["outcome"]["value_outcomes"]
        assert {row["value_id"] for row in rows} == {"ENERGY", "THERMAL"}
        assert len(ms._action_outcome_experiences()) == 2
    finally:
        td.cleanup()


def test_unbound_coordinate_is_rejected_instead_of_expanding_outcome_scope() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "EXTRA")
        result = _outcome(ms, execution_id, "EXTRA", {"ENERGY": 3.65, "ALIEN": 1.0})
        assert result == {"status": "OUTCOME_REJECTED", "reason": "MULTI_VALUE_OUTCOME_UNBOUND_VALUE"}
        assert len(ms.action_closure.outcomes) == 0
    finally:
        td.cleanup()


def test_vector_coordinates_project_into_existing_scalar_learning_rows_with_shared_execution_identity() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "LEARN")
        result = _outcome(ms, execution_id, "LEARN", {"ENERGY": 3.65, "THERMAL": 7.15, "INTEGRITY": 6.33})
        assert result["status"] == "ACTION_OUTCOME_OBSERVED"
        rows = ms._action_outcome_experiences()
        assert len(rows) == 3
        assert {row.execution_id for row in rows} == {execution_id}
        assert {row.value_epoch[0] for row in rows} == set(VALUES)
        assert all(row.frame_epochs == (("F", 0),) for row in rows)
        assert {row.episode_schema_epochs[0][0] for row in rows} == {"E-ENERGY", "E-THERMAL", "E-INTEGRITY"}
    finally:
        td.cleanup()


def test_vector_outcome_does_not_use_intended_or_predicted_effect_as_learning_label() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "ACTUAL")
        result = _outcome(ms, execution_id, "ACTUAL", {"ENERGY": 4.15, "THERMAL": 6.9, "INTEGRITY": 5.4})
        effects = {row["value_id"]: row["actual_value_effect"] for row in result["outcome"]["value_outcomes"]}
        assert effects == {"ENERGY": 0.95, "INTEGRITY": -0.6, "THERMAL": -0.7}
        rows = {row.value_epoch[0]: row.actual_value_effect for row in ms._action_outcome_experiences()}
        assert rows == effects
    finally:
        td.cleanup()


def test_one_execution_still_accepts_only_one_durable_outcome_record() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "DUP")
        assert _outcome(ms, execution_id, "DUP1", {"ENERGY": 3.65})["status"] == "ACTION_OUTCOME_OBSERVED"
        second = _outcome(ms, execution_id, "DUP2", {"THERMAL": 7.15})
        assert second == {"status": "OUTCOME_REJECTED", "reason": "EXECUTION_ALREADY_HAS_OUTCOME"}
        assert len(ms.action_closure.outcomes) == 1
    finally:
        td.cleanup()


def test_repeated_vector_experience_nominates_existing_scalar_relations_per_coordinate() -> None:
    td, ms, _ = _seeded()
    try:
        for index in range(8):
            execution_id = _prepare(ms, f"R{index}")
            _outcome(ms, execution_id, f"R{index}", {"ENERGY": 3.65, "THERMAL": 7.15, "INTEGRITY": 6.33})
        candidates = ms.nominate_action_outcome_predictive_candidates(min_support=8, min_consistency=.78)
        rest = [candidate for candidate in candidates if candidate.capability_id == "REST"]
        assert len(rest) == 3
        assert {candidate.value_epoch[0] for candidate in rest} == set(VALUES)
        assert all(candidate.support == 8 for candidate in rest)
        assert all(candidate.authority == "MODEL_OUTPUT_ONLY" for candidate in rest)
    finally:
        td.cleanup()


def test_missing_current_learning_ancestry_preserves_outcome_but_withholds_learning_row() -> None:
    td, ms, _ = _seeded()
    try:
        execution_id = _prepare(ms, "ANCESTRY")
        # The physical action already happened. Remove one effect-evidence ancestry
        # surface before outcome closure; actual observation must survive, but the
        # unsupported coordinate must not be laundered into learning.
        ms.change_episode_schema("E-INTEGRITY", reason="HOSTILE_EPISODE_DRIFT")
        result = _outcome(ms, execution_id, "ANCESTRY", {"ENERGY": 3.65, "THERMAL": 7.15, "INTEGRITY": 6.33})
        assert result["status"] == "ACTION_OUTCOME_OBSERVED"
        rows = {row["value_id"]: row for row in result["outcome"]["value_outcomes"]}
        assert rows["INTEGRITY"]["learning_ancestry_status"] == "UNKNOWN_CURRENT_EFFECT_ANCESTRY"
        learned = {row.value_epoch[0] for row in ms._action_outcome_experiences()}
        assert learned == {"ENERGY", "THERMAL"}
    finally:
        td.cleanup()
