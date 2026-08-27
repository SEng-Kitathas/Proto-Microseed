from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed import (
    Authority,
    CapabilityContract,
    EpistemicContrastBinding,
    EpistemicContrastRow,
    EpistemicStatus,
    Microseed,
    QualificationState,
    QueryObligation,
)
from microseed.cognition.hypothesis import Hypothesis


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def probe_contract(cid: str, result: str) -> CapabilityContract:
    return CapabilityContract(
        cid,
        "bounded-diagnostic-observation",
        {}, {}, (), (),
        Authority.DERIVED_READ_ONLY,
        ("MS1559-PASS07",),
        "CURRENT",
        {},
        query_obligation_id="Q-PROBE",
        qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_: {"probe_outcome": result},
        operational_scope_id="R2-DIAGNOSTIC",
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="microseed-ms1559-") as td:
        ms = Microseed(Path(td))
        unknown = ms.append_evidence(
            "E-USE-UNKNOWN",
            {"query": "REST::ENERGY::HIGH_CONSEQUENCE", "reason": "use adequacy unresolved"},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source="MS1559-PASS07",
        )
        deficit = ms.record_action_limited_unknown(
            deficit_id="D-USE",
            question_key="use-adequacy:REST:ENERGY:Q-HIGH",
            hypothesis_digest_sha256=h("HSET:SAFE-VS-HARMFUL"),
            unknown_evidence_id=unknown.evidence_id,
            missing_discriminator_signature_sha256=h("MISSING:DIAGNOSTIC-PROBE"),
            assistance_ancestry=("PASS07_SUPPLIED_BOUNDED_HYPOTHESIS_SET",),
        )

        # Two supplied bounded hypotheses disagree only on P1. This is assistance
        # debt by design: Pass 7 tests the acquisition loop, not hypothesis genesis.
        hypotheses = [
            Hypothesis("H-SAFE", lambda x: "A" if x == "P0" else "SAFE"),
            Hypothesis("H-HARM", lambda x: "A" if x == "P0" else "HARM"),
        ]
        discrimination = ms.active_discrimination(hypotheses, ["P0", "P1"], [])
        selected = discrimination["next_probe"]

        ms.register_capability(probe_contract("PROBE-P1", "SAFE"))
        bound = ms.bind_probe_capability(deficit.deficit_id, "PROBE-P1")
        q = QueryObligation(
            "Q-PROBE",
            "bounded-diagnostic-probe",
            required_authority=Authority.DERIVED_READ_ONLY,
            operational_scope_id="R2-DIAGNOSTIC",
        )
        invoked = ms.capabilities.invoke("PROBE-P1", q)

        # Bind the selected probe coordinate to the bounded consequence hypotheses.
        ms.register_epistemic_projection(
            "P1-PROJECTION",
            h("P1-PROJECTION"),
            assistance_ancestry=("PASS07_SUPPLIED_PROBE_TO_OPAQUE_PROJECTION_BINDING",),
        )
        contrast = EpistemicContrastBinding(
            binding_id="B-USE",
            deficit_id=deficit.deficit_id,
            hypothesis_digest_sha256=deficit.hypothesis_digest_sha256,
            rows=(EpistemicContrastRow(
                "P1-PROJECTION",
                0,
                (("H-SAFE", h("SAFE")), ("H-HARM", h("HARM"))),
                None,
            ),),
            assistance_ancestry=("PASS07_SUPPLIED_BOUNDED_CONTRAST",),
        )
        ms.register_epistemic_contrast(contrast)

        evidence = ms.append_evidence(
            "E-PROBE-ACTUAL",
            {
                "actual_probe_capability_id": "PROBE-P1",
                "actual_probe_result": invoked.get("value"),
                "epistemic_projection": {
                    "projection_id": "P1-PROJECTION",
                    "projection_epoch": 0,
                    "outcome_digest_sha256": h("SAFE"),
                },
            },
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="EXT-DIAGNOSTIC",
        )
        ms.record_epistemic_probe_evidence(deficit.deficit_id, evidence.evidence_id)
        bearing = ms.assess_epistemic_evidence_bearing(deficit.deficit_id, "B-USE", evidence.evidence_id)
        status = ms.epistemic_deficit_status(deficit.deficit_id)

        # Anti-flattery: a hypothesis set that agrees everywhere must not nominate a probe.
        non_discriminating = ms.active_discrimination(
            [Hypothesis("H0", lambda x: "SAME"), Hypothesis("H1", lambda x: "SAME")],
            ["P0", "P1"],
            [],
        )

        checks = {
            "active_discrimination_selects_only_disagreement_probe": selected == "P1",
            "probe_binding_is_not_resolution": bound["state"] == "PROBE_AVAILABLE",
            "probe_executes_through_current_capability_contract": invoked.get("status") == "CAPABILITY_RESULT",
            "actual_probe_evidence_requests_revisit": status["state"] == "REVISIT_REQUIRED",
            "bearing_is_discriminating": bearing.get("bearing_kind") == "DISCRIMINATES_LIVE_SET",
            "bearing_has_no_answer_authority": bearing.get("truth_authority") == "NONE" and bearing.get("answer_authority") == "NONE",
            "zero_disagreement_does_not_fake_probe": non_discriminating["next_probe"] is None,
        }
        out = {
            "schema": "microseed.ms1559.pass07.consequence-deficit-probe-loop.v1",
            "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
            "pass": 7,
            "ms": 1559,
            "phase": "EMBODIED_DIAGNOSTIC_COMPOSITION_PROBE",
            "discriminator": (
                "GIVEN_A_CURRENT_QUERY_LOCAL_EPISTEMIC_DEFICIT_AND_BOUNDED_COMPETING_HYPOTHESES_CAN_EXISTING_"
                "ACTIVE_DISCRIMINATION_CAPABILITY_INVOCATION_PROBE_EVIDENCE_AND_BEARING_MACHINERY_REDUCE_THE_DEFICIT_"
                "WITHOUT_A_NEW_EXPLORATION_OR_EPISTEMIC_EXECUTIVE"
            ),
            "checks": checks,
            "all_checks_pass": all(checks.values()),
            "selected_probe": selected,
            "probe_invocation": invoked,
            "bearing": bearing,
            "final_deficit": status,
            "assistance_debt": [
                "BOUNDED_SAFE_VS_HARMFUL_HYPOTHESES_SUPPLIED",
                "P1_TO_PROBE_CAPABILITY_MAPPING_SUPPLIED",
                "OPAQUE_PROJECTION_AND_CONTRAST_SUPPLIED",
                "NO_CREDIT_FOR_ENDOGENOUS_ADEQUACY_QUESTION_OR_HYPOTHESIS_FORMATION",
            ],
            "surviving_localization": (
                "EXISTING_MICROSEED_CAN_SELECT_AND_EXECUTE_A_DISCRIMINATING_PROBE_AND_RETURN_ACTUAL_EVIDENCE_TO_A_QUERY_LOCAL_DEFICIT_"
                "ONCE_THE_DEFICIT_HYPOTHESES_AND_PROBE_MAPPING_EXIST__ACTIVE_EVIDENCE_ACQUISITION_IS_NOT_THE_MISSING_PRIMITIVE"
            ),
            "remaining_open_seam": (
                "ENDOGENOUS_FORMATION_OF_THE_BOUNDED_USE_ADEQUACY_QUESTION_CONTRAST_AND_CANDIDATE_HYPOTHESES_FROM_CURRENT_CONSEQUENCE_EVIDENCE_PLUS_USE_QUERY"
            ),
            "new_primitive_earned": False,
            "main_dev_mutation": "NONE",
            "nonclaims": [
                "NO_ENDOGENOUS_HYPOTHESIS_FORMATION_CREDIT",
                "NO_PROBE_MAPPING_FORMATION_CREDIT",
                "NO_QUERY_ADEQUACY_RESOLUTION_CREDIT",
                "NO_PAL_IMPORT",
            ],
        }
        path = Path(__file__).with_name("MS1559_PASS07_CONSEQUENCE_DEFICIT_PROBE_LOOP.json")
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
