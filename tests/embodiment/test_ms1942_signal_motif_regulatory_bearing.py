from __future__ import annotations

import hashlib
import tempfile
from dataclasses import replace
from pathlib import Path

from microseed import (
    Authority,
    CapabilityContract,
    EpisodeSchemaContract,
    Microseed,
    OperationalCoordinationContract,
    OperationalCounterpartyContract,
    OperationalFrameContract,
    QualificationState,
    ValueVariableContract,
)
from microseed.development.discovery import OperationalTrace

CP = "CP-SIGNAL"
COORD = "COORD-SIGNAL"
FRAME = "F-SIGNAL"
EPISODE = "E-SIGNAL"
VALUE = "V-SIGNAL"
EMIT_A = "EMIT-A"
EMIT_B = "EMIT-B"
RESP_A = "RESP-A"
RESP_B = "RESP-B"
ACTIONS = (EMIT_A, EMIT_B, RESP_A, RESP_B)
SCOPES = ("opaque-scope-0", "opaque-scope-1")


def _cap(cid: str) -> CapabilityContract:
    return CapabilityContract(
        cid,
        "opaque-primitive-operational-action",
        {"kind": "OPAQUE_ACTION"},
        {},
        ("NO_SEMANTIC_TOKEN_AUTHORITY",),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1942",),
        "CURRENT",
        {},
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: None,
    )


def _counterparty() -> OperationalCounterpartyContract:
    c = OperationalCounterpartyContract(
        CP,
        "opaque-independent-causal-counterparty",
        "",
        Authority.DERIVED_READ_ONLY,
        ("MS1053-1077", "MS1942"),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_OPAQUE_COUNTERPARTY_HANDLE",),
        invariants=("NO_SEMANTIC_IDENTITY_AUTHORITY",),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _coordination() -> OperationalCoordinationContract:
    c = OperationalCoordinationContract(
        COORD,
        "opaque-token-response-contingency",
        ((CP, 0),),
        "",
        Authority.DERIVED_READ_ONLY,
        ("MS1078-1102", "MS1942"),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_OPAQUE_COORDINATION_BOUNDARY",),
        invariants=("SIGNAL != REFERENCE", "TOKEN_EMITTED != TOKEN_MEANS"),
    )
    c.signature_sha256 = c.computed_signature_sha256()
    return c


def _value(value_id: str = VALUE, low: float = 4.0, high: float = 8.0) -> ValueVariableContract:
    return ValueVariableContract(
        value_id,
        "opaque-regulatory-variable",
        low,
        high,
        hashlib.sha256(f"{value_id}:{low}:{high}".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS953-977", "MS1942"),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_VIABILITY_INTERVAL"),
        invariants=("NO_SEMANTIC_GOAL_AUTHORITY",),
    )


def _episode(*, value_epochs=((VALUE, 0),)) -> EpisodeSchemaContract:
    return EpisodeSchemaContract(
        EPISODE,
        "opaque-signal-outcome-grouping",
        hashlib.sha256(f"{EPISODE}:{value_epochs}".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS1103-1127", "MS1942"),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_OPAQUE_EPISODE_GROUPING",),
        frame_epochs=((FRAME, 0),),
        value_epochs=tuple(value_epochs),
        counterparty_epochs=((CP, 0),),
        coordination_epochs=((COORD, 0),),
        invariants=("SIGNAL != REFERENCE", "NO_SEMANTIC_JOINT_GOAL_AUTHORITY"),
    )


def _seed(*, multi_value_episode: bool = False):
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1942-")
    m = Microseed(Path(td.name))
    m.register_operational_counterparty(_counterparty())
    m.register_operational_coordination(_coordination())
    m.register_operational_frame(OperationalFrameContract(
        FRAME,
        "opaque-signal-regulatory-frame",
        hashlib.sha256(FRAME.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS878-902", "MS1942"),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        invariants=("NO_SEMANTIC_SIGNAL_OR_ACTION_IDENTITY_AUTHORITY",),
    ))
    m.register_value_variable(_value())
    if multi_value_episode:
        m.register_value_variable(_value("V-OTHER", 0.0, 10.0))
        m.register_episode_schema(_episode(value_epochs=((VALUE, 0), ("V-OTHER", 0))))
    else:
        m.register_episode_schema(_episode())
    for action in ACTIONS:
        m.register_capability(
            _cap(action),
            coordination_dependencies=((COORD, 0),),
            extra_development_dependencies=(EPISODE,),
        )
        m.episodes.bind_capability(EPISODE, action)
    _record_fixture(m)
    return td, m


def _record_fixture(m: Microseed) -> None:
    for action in ACTIONS:
        for i in range(5):
            m.record_operational_trace(OperationalTrace(
                f"SINGLE-{action}-{i}",
                (action,),
                ((0.0,),),
                "singleton-baseline",
                frame_id=FRAME,
                episode_schema_id=EPISODE,
                coordination_ids=(COORD,),
            ))
    pairs = (
        (EMIT_A, RESP_A, 2.0, "MATCH-A"),
        (EMIT_B, RESP_B, 2.0, "MATCH-B"),
        (EMIT_A, RESP_B, -2.0, "CROSS-AB"),
        (EMIT_B, RESP_A, -2.0, "CROSS-BA"),
    )
    for scope in SCOPES:
        for left, right, effect, label in pairs:
            for i in range(8):
                m.record_operational_trace(OperationalTrace(
                    f"{scope}-{label}-{i}",
                    (left, right),
                    ((0.0,), (effect,)),
                    scope,
                    frame_id=FRAME,
                    episode_schema_id=EPISODE,
                    coordination_ids=(COORD,),
                ))


def _candidates(m: Microseed):
    m.discover_capability_candidates()
    return {
        tuple(c.proposed_contract.interface.get("ordered_dependency_sequence", ())): c
        for c in m.capability_candidates.values()
        if len(tuple(c.proposed_contract.interface.get("ordered_dependency_sequence", ()))) == 2
    }


def _close(td, m: Microseed) -> None:
    for obj in (m.biography, m.evidence, m.store):
        try:
            if hasattr(obj, "close"):
                obj.close()
            elif hasattr(obj, "conn"):
                obj.conn.close()
        except Exception:
            pass
    td.cleanup()


def test_matched_and_crossed_motifs_gain_opposite_current_regulatory_bearing_without_semantics():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)
        expected = {
            (EMIT_A, RESP_A): ("YES", "LOWERS_CURRENT_REGULATORY_PRESSURE"),
            (EMIT_B, RESP_B): ("YES", "LOWERS_CURRENT_REGULATORY_PRESSURE"),
            (EMIT_A, RESP_B): ("NO", "WORSENS_CURRENT_REGULATORY_PRESSURE"),
            (EMIT_B, RESP_A): ("NO", "WORSENS_CURRENT_REGULATORY_PRESSURE"),
        }
        assert set(expected) <= set(c)
        for motif, (stance, reason) in expected.items():
            row = m.derive_discovered_candidate_regulatory_bearing(c[motif].candidate_id, VALUE)
            assert row["status"] == "CURRENT_CANDIDATE_REGULATORY_BEARING"
            assert row["commitment"]["commitment"] == stance
            assert row["reason"] == reason
            assert row["authority"] == "NONE" and row["execution_authority"] == "NONE"
            assert row["truth_authority"] == "NONE"
            assert row["semantic_signal_authority"] == "NONE" and row["reference_authority"] == "NONE"
            assert row["selection_authority"] == "NONE" and row["persistence"] == "NONE"
    finally:
        _close(td, m)


def test_candidate_bearing_is_read_only_and_rederived_from_current_value_state():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        before = len(m.store.events())
        first = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        middle = len(m.store.events())
        m.observe_value_state(VALUE, 5.0)
        after_observation = len(m.store.events())
        second = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        after = len(m.store.events())
        assert first["commitment"]["commitment"] == "YES"
        assert second["commitment"]["commitment"] == "YES"
        assert first["pressure_magnitude"] == 1.0 and second["pressure_magnitude"] == 0.0
        assert middle == before
        assert after == after_observation
        assert not hasattr(m, "signal_policy_registry") and not hasattr(m, "signal_meaning_registry")
    finally:
        _close(td, m)


def test_coordination_drift_invalidates_signal_motif_regulatory_bearing_transitively():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        assert m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)["commitment"]["commitment"] == "YES"
        m.change_operational_coordination(COORD, reason="MS1942_COORDINATION_DRIFT")
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE"
        assert row["commitment"] is None
        assert "NOT_CURRENT" in row["reason"]
    finally:
        _close(td, m)


def test_value_or_episode_drift_withholds_signal_motif_regulatory_bearing():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        m.change_value_variable(VALUE, reason="MS1942_VALUE_DRIFT")
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE" and row["commitment"] is None
    finally:
        _close(td, m)

    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        m.change_episode_schema(EPISODE, reason="MS1942_EPISODE_DRIFT")
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE" and row["commitment"] is None
    finally:
        _close(td, m)


def test_multi_value_episode_abstains_instead_of_inventing_signal_referent():
    td, m = _seed(multi_value_episode=True)
    try:
        m.observe_value_state(VALUE, 3.0)
        m.observe_value_state("V-OTHER", 5.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE"
        assert row["reason"] == "EXACT_SINGLE_VALUE_BINDING_REQUIRED"
        assert row["commitment"] is None
        assert row["semantic_signal_authority"] == "NONE" and row["reference_authority"] == "NONE"
    finally:
        _close(td, m)


def test_candidate_subject_binding_rejects_nonfirst_source_trace_ancestry_drift_even_when_trace_is_individually_current():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        # Replace a non-first exact source row with a trace that is still current
        # but no longer carries the candidate's coordination ancestry. The
        # candidate subject must be re-resolved across every source trace.
        trace_id = c.source_trace_ids[-1]
        original = m.operational_traces[trace_id]
        m.operational_traces[trace_id] = replace(
            original,
            coordination_ids=(),
            coordination_epochs=(),
        )
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE"
        assert row["reason"] == "SOURCE_TRACE_COORDINATION_EPOCHS_SUBJECT_MISMATCH"
        assert row["commitment"] is None
        assert row["semantic_signal_authority"] == "NONE"
        assert row["reference_authority"] == "NONE"
    finally:
        _close(td, m)


def test_candidate_subject_binding_rejects_missing_source_trace_instead_of_recomputing_some_other_subject():
    td, m = _seed()
    try:
        m.observe_value_state(VALUE, 3.0)
        c = _candidates(m)[(EMIT_A, RESP_A)]
        m.capability_candidates[c.candidate_id] = replace(c, source_trace_ids=("MISSING-TRACE",))
        row = m.derive_discovered_candidate_regulatory_bearing(c.candidate_id, VALUE)
        assert row["status"] == "UNKNOWN_INCOMPLETE"
        assert row["reason"] == "SOURCE_TRACE_MISSING:MISSING-TRACE"
        assert row["commitment"] is None
    finally:
        _close(td, m)


def test_ms1942_status_preserves_prelingual_reference_and_policy_ceiling():
    td, m = _seed()
    try:
        status = m.status()
        assert status["language"] == "DEFERRED_PRELINGUAL_COGNITION_ACTIVE"
        assert status["discovered_coordination_motif_regulatory_bearing"].startswith("READ_ONLY_CURRENT_VALUE_BOUND_PROJECTION")
        assert status["signal_policy_authority"] == "NONE"
        assert status["signal_reference_authority"] == "NONE"
        assert status["counterparty_semantic_identity_authority"] == "NONE"
        assert status["coordination_semantic_commitment_authority"] == "NONE"
        assert not hasattr(m, "signal_meaning") and not hasattr(m, "reference_token")
    finally:
        _close(td, m)
