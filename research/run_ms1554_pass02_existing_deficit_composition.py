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
    EpistemicCurrentnessAnchor,
    EpistemicStatus,
    Microseed,
    QualificationState,
)


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def qualified_probe(capability_id: str) -> CapabilityContract:
    return CapabilityContract(
        capability_id,
        "opaque-diagnostic-probe",
        {}, {}, (), (),
        Authority.DERIVED_READ_ONLY,
        ("MS1554-PASS02",),
        "CURRENT",
        {},
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {"observed": True},
    )


def setup() -> tuple[tempfile.TemporaryDirectory, Microseed]:
    # Reuse the actual Pass-1 setup helpers rather than clone production setup logic.
    from research.run_ms1553_pass01_evidence_adequacy_establish import seeded_effect_world
    td, ms = seeded_effect_world(trace_count=8, prefix="PASS02", include_sensor=True)
    ms.register_capability(qualified_probe("PROBE"))
    return td, ms


def nominate_use_local_deficit(ms: Microseed, *, deficit_id: str, use_label: str) -> dict[str, Any]:
    """Research adapter only: nominate one existing EpistemicDeficitRecord.

    The adapter deliberately does not decide whether evidence is sufficient. The
    experiment supplies that unresolved disposition so Pass 2 can test whether
    the *existing lifecycle* can carry the problem without new runtime state.
    """
    effect = ms.derive_multi_value_action_licenses(("ENERGY",))["effect_witnesses"]["REST::ENERGY"]
    unknown = ms.append_evidence(
        f"E-{deficit_id}-UNKNOWN",
        {
            "use_label": use_label,
            "effect_trace_ids": effect["source_trace_ids"],
            "effect_support": effect["support"],
            "effect_consistency": effect["consistency"],
            "research_disposition": "USE_ADEQUACY_UNRESOLVED_EXTERNALLY_NOMINATED_FOR_PASS02",
        },
        EpistemicStatus.UNKNOWN_INCOMPLETE,
        source="MS1554-PASS02",
    )
    anchors = (
        EpistemicCurrentnessAnchor("FRAME", "F", ms.frames.epochs["F"]),
        EpistemicCurrentnessAnchor("EPISODE", "E-ENERGY", ms.episodes.epochs["E-ENERGY"]),
        EpistemicCurrentnessAnchor("VALUE", "ENERGY", ms.values.epochs["ENERGY"]),
        EpistemicCurrentnessAnchor("CAPABILITY_PREMISE", "REST", ms.capabilities.epochs["REST"]),
        EpistemicCurrentnessAnchor("CAPABILITY_PREMISE", "SENSE", ms.capabilities.epochs["SENSE"]),
    )
    qsig = h(json.dumps({
        "obligation_id": "ACT",
        "scope": "R2",
        "capability_id": "REST",
        "value_id": "ENERGY",
        "use_label": use_label,
        "effect_trace_ids": effect["source_trace_ids"],
    }, sort_keys=True, separators=(",", ":")))
    rec = ms.record_action_limited_unknown(
        deficit_id=deficit_id,
        question_key=f"use-adequacy:{qsig}",
        hypothesis_digest_sha256=h(f"bounded-use-hypotheses:{qsig}"),
        unknown_evidence_id=unknown.evidence_id,
        missing_discriminator_signature_sha256=h(f"missing-use-discriminator:{qsig}"),
        premise_anchors=anchors,
        assistance_ancestry=("PASS02_EXTERNAL_DEFICIT_NOMINATION_ONLY",),
    )
    return rec.serializable()


def main() -> None:
    td, ms = setup()
    try:
        cheap = nominate_use_local_deficit(ms, deficit_id="D-CHEAP", use_label="CHEAP_REVERSIBLE")
        costly = nominate_use_local_deficit(ms, deficit_id="D-COSTLY", use_label="HIGH_CONSEQUENCE")

        distinct_query_local_records = (
            cheap["question_key"] != costly["question_key"]
            and cheap["missing_discriminator_signature_sha256"] != costly["missing_discriminator_signature_sha256"]
        )
        authority_ceiling = all(
            row["truth_authority"] == "NONE" and row["semantic_question_authority"] == "NONE"
            for row in (cheap, costly)
        )

        bound = ms.bind_probe_capability("D-COSTLY", "PROBE")
        probe_available_not_resolved = bound["state"] == "PROBE_AVAILABLE"

        probe_ev = ms.append_evidence(
            "E-PASS02-PROBE",
            {"actual_probe_result": "OPAQUE-DISCRIMINATING-RESULT"},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXT-PROBE",
        )
        after_probe = ms.record_epistemic_probe_evidence("D-COSTLY", probe_ev.evidence_id)
        revisit_not_resolved = after_probe["state"] == "REVISIT_REQUIRED"

        # Probe loss should reopen action limitation while preserving the question.
        ms.invalidate_capability("PROBE", reason="PASS02_PROBE_PROVIDER_LOST")
        reopened = ms.epistemic_deficit_status("D-COSTLY")
        probe_loss_reopens = reopened["state"] == "ACTION_LIMITED"

        # Rebind a new probe, then stale a question premise. Premise drift should
        # stale the deficit rather than merely reopen it.
        ms.register_capability(qualified_probe("PROBE2"))
        ms.bind_probe_capability("D-COSTLY", "PROBE2")
        ms.change_value_variable("ENERGY", reason="PASS02_VALUE_CONTRACT_DRIFT")
        stale = ms.epistemic_deficit_status("D-COSTLY")
        premise_drift_stales = stale["state"] == "STALE"

        out = {
            "schema": "microseed.ms1554.pass02.existing-deficit-composition.v1",
            "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
            "pass": 2,
            "ms": 1554,
            "phase": "BUILD_DERIVE__REPRESENTATIONAL_LIFECYCLE_QUARRY",
            "discriminator": (
                "ONCE_A_QUERY_LOCAL_CONSEQUENCE_USE_DEFICIT_IS_NOMINATED_CAN_EXISTING_"
                "EPISTEMIC_DEFICIT_CURRENTNESS_PROBE_AND_REVISIT_MACHINERY_CARRY_IT_"
                "WITHOUT_NEW_UNCERTAINTY_STATE_OR_TRUTH_AUTHORITY"
            ),
            "results": {
                "distinct_query_local_records": distinct_query_local_records,
                "authority_ceiling_preserved": authority_ceiling,
                "probe_available_not_resolution": probe_available_not_resolved,
                "probe_evidence_requests_revisit_not_answer": revisit_not_resolved,
                "probe_loss_reopens_action_limited": probe_loss_reopens,
                "question_premise_drift_stales_deficit": premise_drift_stales,
                "cheap_record": cheap,
                "costly_initial_record": costly,
                "costly_after_probe": after_probe,
                "costly_after_probe_loss": reopened,
                "costly_after_value_drift": stale,
            },
            "surviving_localization": (
                "EXISTING_EPISTEMIC_DEFICIT_LIFECYCLE_CAN_CARRY_QUERY_LOCAL_CONSEQUENCE_USE_UNKNOWN_"
                "ONCE_NOMINATED__MISSING_SEAM_IS_RECOGNITION_ADMISSION_AND_LAWFUL_DISCRIMINATOR_BINDING"
            ),
            "assistance_debt": [
                "PASS02_EXTERNALLY_NOMINATES_THAT_USE_ADEQUACY_IS_UNRESOLVED",
                "PASS02_SUPPLIES_THE_PROBE_CAPABILITY_BINDING",
                "PASS02_DOES_NOT_CREDIT_MICROSEED_WITH_DEFICIT_RECOGNITION_OR_PROBE_SELECTION",
            ],
            "disposition": (
                "NARROWED_SURVIVED__EXISTING_DEFICIT_LIFECYCLE_SUFFICIENT_AFTER_NOMINATION__"
                "RECOGNITION_AND_DISCRIMINATOR_BINDING_REMAIN_OPEN__NO_MAINDEV_MUTATION"
            ),
            "primitive_earned": False,
            "main_dev_mutation": "NONE",
            "nonclaims": [
                "NO_AUTOMATIC_USE_ADEQUACY_RECOGNITION",
                "NO_PROBE_SELECTION_CREDIT",
                "NO_EVIDENCE_SUFFICIENCY_ESTIMATOR",
                "NO_QUERY_RISK_SEMANTICS",
                "NO_PAL_ARCHITECTURE_IMPORT",
            ],
        }
        path = Path(__file__).with_name("MS1554_PASS02_EXISTING_DEFICIT_COMPOSITION.json")
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(out, indent=2, sort_keys=True))
    finally:
        td.cleanup()


if __name__ == "__main__":
    main()
