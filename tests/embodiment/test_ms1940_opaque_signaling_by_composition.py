from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from microseed import (
    Authority,
    CapabilityContract,
    CounterfactualRehearsalConfig,
    EpisodeSchemaContract,
    FeasibilityState,
    Microseed,
    Observation,
    OperationalCoordinationContract,
    OperationalCounterpartyContract,
    OperationalFrameContract,
    QualificationState,
    QueryObligation,
    RecruitmentOption,
    RehearsalTransitionObservation,
    ValueVariableContract,
)


def _close(ms: Microseed) -> None:
    ms.biography.close()
    ms.evidence.conn.close()
    ms.store.conn.close()


def _build(root: Path):
    ms = Microseed(root)
    world = {"emitted": None, "expected": "T0"}

    ms.register_operational_frame(
        OperationalFrameContract(
            "F", "opaque-frame", "f" * 64, Authority.DERIVED_READ_ONLY,
            ("MS1940",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
        )
    )
    ms.register_value_variable(
        ValueVariableContract(
            "V", "opaque-regulatory", 2.0, 3.0, "v" * 64,
            Authority.DERIVED_READ_ONLY, ("MS1940",), "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            assistance_ancestry=(
                "SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE",
                "SUPPLIED_VIABILITY_INTERVAL",
            ),
        )
    )
    ms.observe_value_state("V", 0.0)

    cp = OperationalCounterpartyContract(
        "CP", "opaque-independent-causal-source", "", Authority.DERIVED_READ_ONLY,
        ("MS1940",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_COUNTERPARTY_CURRENTNESS",),
    )
    cp.signature_sha256 = cp.computed_signature_sha256()
    ms.register_operational_counterparty(cp)

    coord = OperationalCoordinationContract(
        "R", "opaque-token-contingent-response-relation", (("CP", 0),), "",
        Authority.DERIVED_READ_ONLY, ("MS1940",), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_COORDINATION_CONTRACT",),
        invariants=("SIGNAL != REFERENCE", "TOKEN_EMITTED != TOKEN_MEANS"),
    )
    coord.signature_sha256 = coord.computed_signature_sha256()
    ms.register_operational_coordination(coord)

    def emit(**_):
        world["emitted"] = "T0"
        return {"opaque_emitted_token": "T0"}

    def observe_counterparty(**_):
        acknowledged = world["emitted"] == world["expected"]
        return {
            "next_state_id": "CP-ACK" if acknowledged else "CP-NOACK",
            "value_id": "V",
            "observed_value": 2.2 if acknowledged else 0.0,
            "opaque_counterparty_response": "ACK" if acknowledged else "NO_ACK",
        }

    ms.register_capability(
        CapabilityContract(
            "SIG-T0", "opaque-effect-token-emission", {}, {"output": "opaque-token"},
            (
                "SIGNAL != REFERENCE",
                "TOKEN_EMITTED != TOKEN_MEANS",
                "NO_SEMANTIC_MESSAGE_AUTHORITY",
            ),
            (), Authority.EFFECT, ("MS1940",), "CURRENT", {},
            query_obligation_id="ACT", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=emit, operational_scope_id="S",
            assistance_ancestry=("SUPPLIED_OPAQUE_SIGNAL_TOKEN",),
        ),
        counterparty_dependencies=(("CP", 0),),
        coordination_dependencies=(("R", 0),),
    )
    ms.register_capability(
        CapabilityContract(
            "OBS-CP", "opaque-counterparty-response-observation", {},
            {"output": "opaque-response"},
            ("NO_REFERENCE_AUTHORITY", "NO_MEANING_AUTHORITY"), (),
            Authority.OBSERVATION_ONLY, ("MS1940",), "CURRENT", {},
            query_obligation_id="OBS-Q", qualification=QualificationState.SHADOW_QUALIFIED,
            handler=observe_counterparty, operational_scope_id="S",
        ),
        counterparty_dependencies=(("CP", 0),),
    )
    ms.register_capability(
        CapabilityContract(
            "OBS-BASIS", "bounded-use-basis", {}, {}, ("NO_TRUTH_AUTHORITY",), (),
            Authority.DERIVED_READ_ONLY, ("MS1940",), "CURRENT", {},
            dependencies=("OBS-CP",), query_obligation_id="BASIS-Q",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_: {"claim": "BOUNDED_USE_ONLY"}, operational_scope_id="S",
        )
    )
    ms.register_episode_schema(
        EpisodeSchemaContract(
            "E", "opaque-episode", "e" * 64, Authority.DERIVED_READ_ONLY,
            ("MS1940",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
            frame_epochs=(("F", 0),), value_epochs=(("V", 0),),
            counterparty_epochs=(("CP", 0),), coordination_epochs=(("R", 0),),
        )
    )
    ms.observe_opaque_control_state(
        Observation(
            "CTRL-S0", "EXT", "opaque-control", "S0",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id="E-CTRL-S0",
    )
    return ms, world


def _rows() -> tuple[RehearsalTransitionObservation, ...]:
    return tuple(
        RehearsalTransitionObservation(
            f"SIG-EV-{i}", "S0", "SIG-T0", "CP-ACK", 2.2, 0,
            "F", 0, "E", 0, None, None, "R", 0,
        )
        for i in range(12)
    )


def _options() -> tuple[RecruitmentOption, ...]:
    return (RecruitmentOption("SIG-T0", FeasibilityState.FEASIBLE, local_cost=0.1),)


def _act_obligation() -> QueryObligation:
    return QueryObligation("ACT", "emit opaque token", Authority.EFFECT, operational_scope_id="S")


def _obs_obligation() -> QueryObligation:
    return QueryObligation("OBS-Q", "observe opaque response", Authority.OBSERVATION_ONLY, operational_scope_id="S")


def _basis_obligation() -> QueryObligation:
    return QueryObligation("BASIS-Q", "bounded use basis", Authority.DERIVED_READ_ONLY, operational_scope_id="S")


def _proposal(ms: Microseed):
    p = ms.nominate_counterfactual_rehearsal(
        _rows(), _options(), start_state_id="S0", value_id="V",
        config=CounterfactualRehearsalConfig(max_horizon=1),
    )
    assert p is not None and p.sequence == ("SIG-T0",)
    return p


def _execute_signal(ms: Microseed):
    p = _proposal(ms)
    ir = ms.nominate_bounded_action_intent(p.proposal_id, _act_obligation())
    assert ir["status"] == "ACTION_INTENT_NOMINATED"
    ex = ms.execute_bounded_action(ir["intent"]["intent_id"], _act_obligation())
    assert ex["status"] == "ACTION_EXECUTED"
    return p, ex


def test_opaque_signal_changes_counterparty_contingent_observation_without_reference_authority():
    with tempfile.TemporaryDirectory(prefix="ms1940-signal-") as td:
        ms, world = _build(Path(td))
        try:
            before = ms.capabilities.invoke("OBS-CP", _obs_obligation())
            p, ex = _execute_signal(ms)
            after = ms.capabilities.invoke("OBS-CP", _obs_obligation())
            assert before["value"]["opaque_counterparty_response"] == "NO_ACK"
            assert after["value"]["opaque_counterparty_response"] == "ACK"
            assert world["emitted"] == "T0"
            assert p.truth_authority == p.execution_authority == p.qualification_authority == "NONE"

            eid = ex["execution"]["execution_id"]
            out = ms.record_bounded_action_outcome_via_observation_basis(
                eid,
                observation_capability_id="OBS-CP", observation_obligation=_obs_obligation(),
                basis_capability_id="OBS-BASIS", basis_obligation=_basis_obligation(),
                evidence_id="E-SIGNAL-OUT", capture_id="CAP-SIGNAL-OUT",
            )
            assert out["status"] == "ACTION_OUTCOME_OBSERVED"
            assert ms.action_closure.current_state.state_id == "CP-ACK"
            assert ms.value_pressure("V")["pressure_magnitude"] == 0.0
        finally:
            _close(ms)


def test_coordination_drift_stales_signal_route_before_execution_and_requires_reason():
    with tempfile.TemporaryDirectory(prefix="ms1940-coord-drift-") as td:
        ms, world = _build(Path(td))
        try:
            p = _proposal(ms)
            with pytest.raises(TypeError):
                ms.change_operational_coordination("R")
            stale = ms.change_operational_coordination("R", reason="OPAQUE_CONVENTION_DRIFT")
            assert "SIG-T0" in stale
            ir = ms.nominate_bounded_action_intent(p.proposal_id, _act_obligation())
            assert ir["status"] == "ABSTAIN"
            assert world["emitted"] is None
        finally:
            _close(ms)


def test_counterparty_drift_invalidates_coordination_and_signal_route():
    with tempfile.TemporaryDirectory(prefix="ms1940-counterparty-drift-") as td:
        ms, world = _build(Path(td))
        try:
            p = _proposal(ms)
            stale = ms.change_operational_counterparty("CP", reason="OPAQUE_COUNTERPARTY_DRIFT")
            assert "SIG-T0" in stale
            assert not ms.coordinations.is_current("R")
            ir = ms.nominate_bounded_action_intent(p.proposal_id, _act_obligation())
            assert ir["status"] == "ABSTAIN"
            assert world["emitted"] is None
        finally:
            _close(ms)


def test_unannounced_convention_mismatch_is_prediction_violation_not_semantic_reinterpretation():
    with tempfile.TemporaryDirectory(prefix="ms1940-mismatch-") as td:
        ms, world = _build(Path(td))
        try:
            world["expected"] = "T1"
            _, ex = _execute_signal(ms)
            eid = ex["execution"]["execution_id"]
            out = ms.record_bounded_action_outcome_via_observation_basis(
                eid,
                observation_capability_id="OBS-CP", observation_obligation=_obs_obligation(),
                basis_capability_id="OBS-BASIS", basis_obligation=_basis_obligation(),
                evidence_id="E-SIGNAL-MISMATCH", capture_id="CAP-SIGNAL-MISMATCH",
            )
            assert out["status"] == "ACTION_OUTCOME_OBSERVED"
            assert ms.action_closure.current_state.state_id == "CP-NOACK"
            assert out["outcome"]["prediction_commitment"]["commitment"] == "NO"
            assert ms.value_pressure("V")["pressure_magnitude"] > 0.0
            # A failed prediction does not autonomously invent a changed convention.
            assert ms.coordinations.is_current("R")
        finally:
            _close(ms)


def test_signaling_does_not_promote_reference_meaning_identity_or_language():
    with tempfile.TemporaryDirectory(prefix="ms1940-authority-") as td:
        ms, _ = _build(Path(td))
        try:
            rr = ms.nominate_referents([[0, 2], [0, 2]])
            assert rr.status == "UNKNOWN_INCOMPLETE"
            assert rr.identity_authority == "NONE"
            assert ms.counterparties.contracts["CP"].semantic_identity_authority == "NONE"
            c = ms.coordinations.contracts["R"]
            assert c.semantic_commitment_authority == "NONE"
            assert c.intention_authority == "NONE"
            assert c.promise_authority == "NONE"
            status = ms.status()
            assert status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
            for key in (
                "semantic_message_authority", "reference_authority",
                "language_authority", "meaning_authority",
            ):
                assert key not in status
        finally:
            _close(ms)
