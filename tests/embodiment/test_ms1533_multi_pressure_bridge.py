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
    OperationalFrameContract,
    QualificationState,
    ValueVariableContract,
)
from microseed.development.discovery import DiscoveryConfig, OperationalTrace
from microseed.runtime.commitment import (
    RelationalCommitment,
    TernaryCommitment,
    conjoin_required_commitments,
)

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


def _frame(frame_id: str = "F") -> OperationalFrameContract:
    return OperationalFrameContract(
        frame_id,
        "opaque-regulatory-frame",
        hashlib.sha256(frame_id.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY,
        ("MS1533-RESEARCH",),
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


def _episode(value_id: str, *, suffix: str = "") -> EpisodeSchemaContract:
    schema_id = f"E-{value_id}{suffix}"
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


def _capability(capability_id: str) -> CapabilityContract:
    return CapabilityContract(
        capability_id,
        "opaque-action",
        {},
        {},
        (),
        (),
        Authority.DERIVED_READ_ONLY,
        ("MS1533-RESEARCH",),
        "CURRENT",
        {},
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def _seeded() -> tuple[tempfile.TemporaryDirectory, Microseed]:
    td = tempfile.TemporaryDirectory(prefix="microseed-ms1533-")
    ms = Microseed(Path(td.name))
    ms.register_operational_frame(_frame())
    for value_id in VALUES:
        ms.register_value_variable(_value(value_id))
        ms.register_episode_schema(_episode(value_id))
    for capability_id in EFFECTS:
        ms.register_capability(_capability(capability_id))

    rng = random.Random(1533)
    noise = (0.32, 0.28, 0.30)
    for capability_id, effect_vector in EFFECTS.items():
        for value_index, value_id in enumerate(VALUES):
            for sample in range(61):
                observed = effect_vector[value_index] + rng.gauss(0.0, noise[value_index])
                ms.record_operational_trace(OperationalTrace(
                    trace_id=f"{capability_id}-{value_id}-{sample}",
                    steps=(capability_id,),
                    step_effects=((observed,),),
                    frame_id="F",
                    episode_schema_id=f"E-{value_id}",
                ))
    return td, ms


def _observe(ms: Microseed, *, energy: float, thermal: float, integrity: float) -> None:
    ms.observe_value_state("ENERGY", energy)
    ms.observe_value_state("THERMAL", thermal)
    ms.observe_value_state("INTEGRITY", integrity)


def test_generic_conjunction_preserves_three_way_premise_licensing() -> None:
    yes = RelationalCommitment("Y", "Y", TernaryCommitment.YES)
    no = RelationalCommitment("N", "N", TernaryCommitment.NO)
    unknown = RelationalCommitment("U", "U", TernaryCommitment.UNKNOWN)

    assert conjoin_required_commitments(
        (yes, yes), commitment_id="YY", target_id="X"
    ).commitment == TernaryCommitment.YES
    assert conjoin_required_commitments(
        (yes, no), commitment_id="YN", target_id="X"
    ).commitment == TernaryCommitment.NO
    assert conjoin_required_commitments(
        (yes, unknown), commitment_id="YU", target_id="X"
    ).commitment == TernaryCommitment.UNKNOWN


def test_value_bound_bridge_can_derive_one_unique_non_authoritative_license() -> None:
    td, ms = _seeded()
    try:
        _observe(ms, energy=3.2, thermal=7.6, integrity=6.0)
        before = len(ms.store.events())
        result = ms.derive_multi_value_action_licenses(
            VALUES,
            config=DiscoveryConfig(min_singleton_samples=5, quantization_step=0.5),
        )
        after = len(ms.store.events())

        assert result["status"] == "UNIQUE_ACTION_LICENSE"
        assert result["licensed_action_ids"] == ["REST"]
        assert result["overall_commitment"]["commitment"] == "YES"
        assert result["authority"] == "NONE"
        assert result["execution_authority"] == "NONE"
        assert result["semantic_value_priority_authority"] == "NONE"
        assert result["persistence"] == "NONE"
        assert result["effect_coordinate_mapping_ancestry"] == "CURRENT_SINGLE_VALUE_EPISODE_BINDING"
        assert before == after
    finally:
        td.cleanup()


def test_multiple_lawful_actions_remain_unknown_instead_of_being_ranked() -> None:
    td, ms = _seeded()
    try:
        _observe(ms, energy=3.2, thermal=5.0, integrity=6.0)
        result = ms.derive_multi_value_action_licenses(VALUES)
        assert result["status"] == "UNKNOWN_ACTION_SELECTION"
        assert result["overall_commitment"]["commitment"] == "UNKNOWN"
        assert len(result["licensed_action_ids"]) >= 2
    finally:
        td.cleanup()


def test_value_order_does_not_create_priority_authority() -> None:
    td, ms = _seeded()
    try:
        _observe(ms, energy=3.2, thermal=7.6, integrity=6.0)
        forward = ms.derive_multi_value_action_licenses(VALUES)
        reverse = ms.derive_multi_value_action_licenses(tuple(reversed(VALUES)))
        assert forward["licensed_action_ids"] == reverse["licensed_action_ids"]
        assert forward["status"] == reverse["status"]
    finally:
        td.cleanup()


def test_capability_invalidation_selectively_removes_old_effect_support() -> None:
    td, ms = _seeded()
    try:
        _observe(ms, energy=3.2, thermal=7.6, integrity=6.0)
        assert ms.derive_multi_value_action_licenses(VALUES)["licensed_action_ids"] == ["REST"]
        ms.invalidate_capability("REST", reason="PROVIDER_DRIFT")
        result = ms.derive_multi_value_action_licenses(VALUES)
        assert not any(key.startswith("REST::") for key in result["effect_witnesses"])
        assert result["overall_commitment"]["commitment"] == "UNKNOWN"
    finally:
        td.cleanup()


def test_multiple_supported_ancestry_shapes_are_not_averaged_into_one_effect() -> None:
    td, ms = _seeded()
    try:
        # Add a second current frame/episode ancestry for REST::ENERGY with a
        # strongly incompatible effect. Both shapes are supported, so the pair
        # must become UNKNOWN rather than being averaged into a flattering law.
        ms.register_operational_frame(_frame("F2"))
        schema = EpisodeSchemaContract(
            "E-ENERGY-ALT",
            "opaque-single-value-effect-binding",
            hashlib.sha256(b"E-ENERGY-ALT").hexdigest(),
            Authority.DERIVED_READ_ONLY,
            ("MS1533-RESEARCH",),
            "CURRENT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            frame_epochs=(("F2", 0),),
            value_epochs=(("ENERGY", 0),),
        )
        ms.register_episode_schema(schema)
        for sample in range(10):
            # record_operational_trace requires the trace frame to match the
            # schema ancestry; use F2 explicitly.
            ms.record_operational_trace(OperationalTrace(
                trace_id=f"REST-ENERGY-ALT-{sample}",
                steps=("REST",),
                step_effects=((3.0,),),
                frame_id="F2",
                episode_schema_id="E-ENERGY-ALT",
            ))
        _observe(ms, energy=3.2, thermal=7.6, integrity=6.0)
        result = ms.derive_multi_value_action_licenses(VALUES)
        assert result["effect_witnesses"]["REST::ENERGY"]["status"] == "UNKNOWN_MULTIPLE_CURRENT_ANCESTRY_SHAPES"
        rest_rows = result["coordinate_commitments"]["REST"]
        assert any(row["commitment"] == "UNKNOWN" for row in rest_rows)
        assert "REST" not in result["licensed_action_ids"]
    finally:
        td.cleanup()


def test_missing_current_value_observation_withholds_that_coordinate() -> None:
    td, ms = _seeded()
    try:
        ms.observe_value_state("ENERGY", 3.2)
        ms.observe_value_state("THERMAL", 7.6)
        result = ms.derive_multi_value_action_licenses(VALUES)
        assert result["overall_commitment"]["commitment"] == "UNKNOWN"
        integrity_rows = [
            row
            for rows in result["coordinate_commitments"].values()
            for row in rows
            if row["target_id"].endswith(":value:INTEGRITY")
        ]
        assert integrity_rows
        assert all(row["commitment"] == "UNKNOWN" for row in integrity_rows)
    finally:
        td.cleanup()


def test_bridge_adds_no_manager_or_persistent_readiness_surface() -> None:
    td, ms = _seeded()
    try:
        assert not hasattr(ms, "arbitration_manager")
        assert not hasattr(ms, "multi_value_registry")
        assert not hasattr(ms, "persist_action_license")
    finally:
        td.cleanup()


def test_transient_license_is_rederived_from_current_value_state() -> None:
    td, ms = _seeded()
    try:
        _observe(ms, energy=3.2, thermal=7.6, integrity=6.0)
        first = ms.derive_multi_value_action_licenses(VALUES)
        assert first["licensed_action_ids"] == ["REST"]

        # Move the live value state without changing the value-contract epoch.
        # The bridge must not preserve the old license as durable authority.
        _observe(ms, energy=6.0, thermal=5.0, integrity=6.0)
        second = ms.derive_multi_value_action_licenses(VALUES)
        assert second["licensed_action_ids"] != ["REST"]
        assert second["overall_commitment"]["commitment"] == "UNKNOWN"
    finally:
        td.cleanup()
