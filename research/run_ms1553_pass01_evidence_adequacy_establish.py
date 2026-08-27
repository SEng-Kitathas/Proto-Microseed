from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed import (
    Authority,
    CapabilityContract,
    EpisodeSchemaContract,
    EpistemicContrastBinding,
    EpistemicContrastRow,
    EpistemicCurrentnessAnchor,
    EpistemicStatus,
    Microseed,
    Observation,
    OperationalFrameContract,
    QualificationState,
    QueryObligation,
    ValueVariableContract,
)
from microseed.development.discovery import DiscoveryConfig, OperationalTrace

VALUE_ID = "ENERGY"
ACTION_ID = "REST"
FRAME_ID = "F"
EPISODE_ID = "E-ENERGY"
SCOPE = "R2"
CFG = DiscoveryConfig(
    min_singleton_samples=5,
    min_consistency=0.80,
    residual_tolerance_l1=0.20,
    quantization_step=0.10,
)


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frame() -> OperationalFrameContract:
    return OperationalFrameContract(
        FRAME_ID,
        "opaque-regulatory-frame",
        h("MS1553:F"),
        Authority.DERIVED_READ_ONLY,
        ("MS1553-PASS01",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
    )


def value_contract() -> ValueVariableContract:
    return ValueVariableContract(
        VALUE_ID,
        "opaque-regulatory",
        4.0,
        8.0,
        h("MS1553:ENERGY:4:8"),
        Authority.DERIVED_READ_ONLY,
        ("MS953-977",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=(
            "SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE",
            "SUPPLIED_VIABILITY_INTERVAL",
        ),
    )


def episode() -> EpisodeSchemaContract:
    return EpisodeSchemaContract(
        EPISODE_ID,
        "opaque-single-value-effect-binding",
        h("MS1553:E-ENERGY"),
        Authority.DERIVED_READ_ONLY,
        ("MS1103-1127",),
        "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=((FRAME_ID, 0),),
        value_epochs=((VALUE_ID, 0),),
    )


def effect_capability(capability_id: str, *, authority: Authority = Authority.EFFECT) -> CapabilityContract:
    return CapabilityContract(
        capability_id,
        "opaque-action" if authority == Authority.EFFECT else "opaque-observation-capability",
        {},
        {},
        (),
        (),
        authority,
        ("MS1553-PASS01",),
        "CURRENT",
        {},
        query_obligation_id="ACT" if authority == Authority.EFFECT else None,
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=(lambda **_: {"action": capability_id}) if authority == Authority.EFFECT else (lambda **_: {"observation": True}),
        operational_scope_id=SCOPE if authority == Authority.EFFECT else None,
    )


def obligation(purpose: str) -> QueryObligation:
    return QueryObligation(
        "ACT",
        purpose,
        required_authority=Authority.EFFECT,
        operational_scope_id=SCOPE,
    )


def seeded_effect_world(*, trace_count: int, prefix: str, include_sensor: bool = False) -> tuple[tempfile.TemporaryDirectory, Microseed]:
    td = tempfile.TemporaryDirectory(prefix=f"microseed-ms1553-{prefix.lower()}-")
    ms = Microseed(Path(td.name))
    ms.register_operational_frame(frame())
    ms.register_value_variable(value_contract())
    ms.register_episode_schema(episode())
    ms.register_capability(effect_capability(ACTION_ID))
    if include_sensor:
        ms.register_capability(effect_capability("SENSE", authority=Authority.DERIVED_READ_ONLY))

    # Deliberately identical observed effects. The shared-root vs independent-root
    # distinction is evaluator-only metadata below because OperationalTrace has no
    # evidence-root field. This is the representation pressure being tested.
    effects = (0.48, 0.52, 0.50, 0.49, 0.51, 0.50, 0.47, 0.53)
    for idx in range(trace_count):
        ms.record_operational_trace(OperationalTrace(
            trace_id=f"{prefix}-TRACE-{idx}",
            steps=(ACTION_ID,),
            step_effects=((effects[idx % len(effects)],),),
            operational_scope_id=SCOPE,
            obligation_id="ACT",
            frame_id=FRAME_ID,
            episode_schema_id=EPISODE_ID,
        ))
    ms.observe_value_state(VALUE_ID, 3.2)
    ms.observe_opaque_control_state(
        Observation(
            f"CTRL-{prefix}",
            "EXT",
            "control",
            f"STATE-{prefix}",
            authority=Authority.OBSERVATION_ONLY,
        ),
        evidence_id=f"E-CTRL-{prefix}",
    )
    return td, ms


def effect_summary(ms: Microseed) -> dict[str, Any]:
    result = ms.derive_multi_value_action_licenses((VALUE_ID,), config=CFG)
    row = result.get("effect_witnesses", {}).get(f"{ACTION_ID}::{VALUE_ID}")
    return {
        "license_status": result.get("status"),
        "licensed_action_ids": result.get("licensed_action_ids"),
        "overall_reason": result.get("overall_commitment", {}).get("reason"),
        "effect_witness": row,
    }


def case_root_independence() -> dict[str, Any]:
    td_a, independent = seeded_effect_world(trace_count=8, prefix="INDEPENDENT")
    td_b, redundant = seeded_effect_world(trace_count=8, prefix="REDUNDANT")
    try:
        a = effect_summary(independent)
        b = effect_summary(redundant)
        comparable = ("status", "effect", "support", "consistency", "capability_epoch", "value_epoch")
        arow = a["effect_witness"] or {}
        brow = b["effect_witness"] or {}
        same_visible_statistics = all(arow.get(k) == brow.get(k) for k in comparable)
        return {
            "case": "A_VS_B_INDEPENDENT_ROOTS_VS_SHARED_ROOT_REPETITION",
            "evaluator_only_root_annotation": {
                "independent_fixture": [f"ROOT-{i}" for i in range(8)],
                "redundant_fixture": ["ROOT-SHARED"] * 8,
                "fed_to_microseed": False,
            },
            "independent": a,
            "redundant": b,
            "same_visible_effect_statistics": same_visible_statistics,
            "same_license_status": a["license_status"] == b["license_status"],
            "finding": (
                "CURRENT_EFFECT_PATH_COUNTS_TRACE_RECURRENCE_BUT_HAS_NO_ROOT_INDEPENDENCE_SEMANTICS"
                if same_visible_statistics and a["license_status"] == b["license_status"]
                else "UNEXPECTED_DIFFERENCE_REQUIRES_REVIEW"
            ),
        }
    finally:
        td_a.cleanup()
        td_b.cleanup()


def case_sparse_discriminating() -> dict[str, Any]:
    td, ms = seeded_effect_world(trace_count=2, prefix="SPARSE")
    try:
        before = effect_summary(ms)
        unknown = ms.append_evidence(
            "E-SPARSE-UNKNOWN",
            {"reason": "current consequence evidence below recurrence qualification"},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1553-PASS01",
        )
        deficit = ms.record_action_limited_unknown(
            deficit_id="D-SPARSE",
            question_key="opaque-consequence-discriminator",
            hypothesis_digest_sha256=h("HSET-SPARSE"),
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=h("MISSING-SPARSE"),
        )
        ms.register_epistemic_projection(
            "P-SPARSE",
            h("PROJECTION-SPARSE"),
            assistance_ancestry=("SUPPLIED_OPAQUE_PROJECTION_FOR_ESTABLISH_PROBE",),
        )
        binding = EpistemicContrastBinding(
            binding_id="B-SPARSE",
            deficit_id=deficit.deficit_id,
            hypothesis_digest_sha256=deficit.hypothesis_digest_sha256,
            rows=(EpistemicContrastRow(
                "P-SPARSE",
                ms.epistemic_projections.records["P-SPARSE"].epoch,
                (("H0", h("OUT-A")), ("H1", h("OUT-B"))),
                None,
            ),),
            assistance_ancestry=("SUPPLIED_BOUNDED_CONTRAST_FOR_ESTABLISH_PROBE",),
        )
        ms.register_epistemic_contrast(binding)
        evidence = ms.append_evidence(
            "E-SPARSE-DISCRIMINATING",
            {
                "epistemic_projection": {
                    "projection_id": "P-SPARSE",
                    "projection_epoch": 0,
                    "outcome_digest_sha256": h("OUT-B"),
                }
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="MS1553-PASS01",
        )
        bearing = ms.assess_epistemic_evidence_bearing(
            "D-SPARSE",
            "B-SPARSE",
            evidence.evidence_id,
        )
        after = effect_summary(ms)
        return {
            "case": "C_SPARSE_BUT_DISCRIMINATING",
            "effect_path_before": before,
            "epistemic_bearing": bearing,
            "deficit_state_after_bearing": ms.epistemic_deficit_status("D-SPARSE")["state"],
            "effect_path_after": after,
            "finding": (
                "DISCRIMINATING_EVIDENCE_CAN_TRIGGER_REVISIT_BUT_DOES_NOT_COMPOSE_INTO_CURRENT_EFFECT_USE"
                if bearing.get("bearing_kind") == "DISCRIMINATES_LIVE_SET"
                and bearing.get("state") == "REVISIT_REQUIRED"
                and after.get("license_status") == "UNKNOWN_ACTION_SELECTION"
                else "UNEXPECTED_SPARSE_DISCRIMINATION_RESULT"
            ),
        }
    finally:
        td.cleanup()


def case_query_dependence() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for label, purpose in (
        ("cheap_reversible", "cheap-reversible-use"),
        ("high_consequence", "irreversible-high-consequence-use"),
    ):
        td, ms = seeded_effect_world(trace_count=8, prefix=f"QUERY-{label.upper()}")
        try:
            nominated = ms.nominate_multi_value_action_intent(
                (VALUE_ID,),
                obligation(purpose),
                config=CFG,
            )
            results[label] = {
                "status": nominated.get("status"),
                "reason": nominated.get("reason"),
                "licensed_action_ids": nominated.get("license", {}).get("licensed_action_ids"),
                "intent_basis_kind": nominated.get("intent", {}).get("basis_kind"),
                "obligation_id": nominated.get("intent", {}).get("obligation_id"),
                "operational_scope_id": nominated.get("intent", {}).get("operational_scope_id"),
                "purpose_supplied_to_query": purpose,
            }
        finally:
            td.cleanup()
    same = all(
        results["cheap_reversible"].get(k) == results["high_consequence"].get(k)
        for k in ("status", "reason", "licensed_action_ids", "intent_basis_kind", "obligation_id", "operational_scope_id")
    )
    return {
        "case": "D_QUERY_DEPENDENT_USE",
        "results": results,
        "same_operational_decision": same,
        "finding": (
            "CONSEQUENCE_LICENSE_IS_NOT_QUERY_ADEQUACY_SENSITIVE_BEYOND_EXISTING_OBLIGATION_ID_SCOPE_AUTHORITY"
            if same else "QUERY_PURPOSE_CHANGED_CURRENT_DECISION"
        ),
    }


def case_stale_observation_ancestry() -> dict[str, Any]:
    td, ms = seeded_effect_world(trace_count=8, prefix="STALE-SENSOR", include_sensor=True)
    try:
        before_effect = effect_summary(ms)
        unknown = ms.append_evidence(
            "E-SENSOR-UNKNOWN",
            {"reason": "bounded consequence-use adequacy unresolved"},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1553-PASS01",
        )
        sensor_epoch = ms.capabilities.epochs["SENSE"]
        ms.record_action_limited_unknown(
            deficit_id="D-SENSOR",
            question_key="opaque-consequence-use-adequacy",
            hypothesis_digest_sha256=h("HSET-SENSOR"),
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=h("MISSING-SENSOR"),
            premise_anchors=(EpistemicCurrentnessAnchor("CAPABILITY_PREMISE", "SENSE", sensor_epoch),),
        )
        before_deficit = ms.epistemic_deficit_status("D-SENSOR")
        invalidation = ms.invalidate_capability("SENSE", reason="HOSTILE_OBSERVATION_PROVIDER_DRIFT")
        after_deficit = ms.epistemic_deficit_status("D-SENSOR")
        after_effect = effect_summary(ms)
        return {
            "case": "E_STALE_OBSERVATION_ANCESTRY",
            "effect_before": before_effect,
            "deficit_before": before_deficit["state"],
            "sensor_invalidation": sorted(invalidation) if isinstance(invalidation, set) else invalidation,
            "deficit_after": after_deficit["state"],
            "deficit_stale_reason": after_deficit.get("stale_reason"),
            "effect_after": after_effect,
            "finding": (
                "PREMISE_ANCHOR_CAN_STALE_EPISTEMIC_PRESSURE_BUT_EFFECT_WITNESS_DOES_NOT_CARRY_OBSERVATION_CAPABILITY_ANCESTRY"
                if after_deficit["state"] == "STALE"
                and before_effect.get("license_status") == after_effect.get("license_status") == "UNIQUE_ACTION_LICENSE"
                else "UNEXPECTED_STALE_ANCESTRY_RESULT"
            ),
        }
    finally:
        td.cleanup()


def main() -> None:
    cases = [
        case_root_independence(),
        case_sparse_discriminating(),
        case_query_dependence(),
        case_stale_observation_ancestry(),
    ]
    out = {
        "schema": "microseed.ms1553.pass01.evidence-adequacy-establish.v1",
        "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
        "pass": 1,
        "ms": 1553,
        "phase": "ESTABLISH_PROBE",
        "discriminator": (
            "CAN_EXISTING_MICROSEED_SURFACES_DISTINGUISH_CURRENT_CONSEQUENCE_EVIDENCE_THAT_IS_"
            "ADEQUATE_REDUNDANT_SPARSE_DISCRIMINATING_QUERY_DEPENDENT_OR_STALE_IN_ANCESTRY_"
            "WITHOUT_NEW_UNCERTAINTY_OR_PAL_ARCHITECTURE"
        ),
        "cases": cases,
        "reconciliation": {
            "already_existing_parts": [
                "CURRENT_EFFECT_RECURRENCE_WITH_SUPPORT_AND_CONSISTENCY",
                "QUERY_OBLIGATION_ID_SCOPE_AUTHORITY_BINDING",
                "ACTION_LIMITED_EPISTEMIC_DEFICIT_LIFECYCLE",
                "OPAQUE_PREMISE_CURRENTNESS_ANCHORS",
                "BOUNDED_DISCRIMINATING_EVIDENCE_BEARING",
                "PROBE_BINDING_AND_REVISIT_REQUIRED_STATE",
            ],
            "not_currently_composed_into_effect_use": [
                "EVIDENCE_ROOT_INDEPENDENCE_OR_REDUNDANCY",
                "SPARSE_DISCRIMINATING_BEARING_AS_EFFECT_USE_SUFFICIENCY",
                "QUERY_RELATIVE_CONSEQUENCE_EVIDENCE_ADEQUACY",
                "OBSERVATION_CAPABILITY_ANCESTRY_ON_CURRENT_EFFECT_WITNESSES",
            ],
            "candidate_pressure": (
                "EXISTING_EPISTEMIC_DEFICIT_AND_BEARING_MACHINERY_CAN_REPRESENT_ACTION_LIMITED_UNKNOWN_"
                "AND_DISCRIMINATING_REVISIT_PRESSURE_BUT_THE_CONSEQUENCE_USE_PATH_LACKS_THE_ANCESTRY_"
                "AND_QUERY_BINDINGS_NEEDED_TO_COMPOSE_IT"
            ),
        },
        "disposition": "NARROWED_SURVIVED_ESTABLISH_PROBE__EXISTING_PARTS_PRESENT_BUT_NOT_COMPOSED_AT_CONSEQUENCE_USE_BOUNDARY__NO_MAINDEV_MUTATION",
        "primitive_earned": False,
        "main_dev_mutation": "NONE",
        "pal_transfer": "NONE__STEP162_USED_AS_HOSTILE_DONOR_PRESSURE_ONLY",
        "nonclaims": [
            "NO_EVIDENCE_ADEQUACY_ESTIMATOR_EARNED",
            "NO_CONFIDENCE_THRESHOLD_EARNED",
            "NO_RISK_HIERARCHY_EARNED",
            "NO_ROOT_INDEPENDENCE_ONTOLOGY_EARNED",
            "NO_WHOLE_ORGANISM_COMPETENCE_CREDIT",
        ],
    }
    output = Path(__file__).with_name("MS1553_PASS01_EVIDENCE_ADEQUACY_ESTABLISH.json")
    output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
