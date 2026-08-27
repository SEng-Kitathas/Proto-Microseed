from __future__ import annotations

import hashlib
import inspect
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed import Authority, EpistemicStatus, Microseed
from microseed.evidence.authority import FixedQualifier
from microseed.development.action_learning import ActionOutcomeExperience, ActionOutcomePredictiveCandidate


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="microseed-ms1556-") as td:
        ms = Microseed(Path(td))
        payload = {"execution_id": "X", "value_id": "ENERGY", "actual_value_effect": 0.5}
        e1 = ms.append_evidence("E1", payload, EpistemicStatus.PRESSURE_SUPPORTED, source="SENSOR-A")
        e2 = ms.append_evidence("E2", payload, EpistemicStatus.PRESSURE_SUPPORTED, source="SENSOR-A")
        e3 = ms.append_evidence(
            "E3",
            {**payload, "capture_variant": "second-packet"},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="SENSOR-A",
        )
        e4 = ms.append_evidence(
            "E4",
            {**payload, "capture_variant": "independent-channel"},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source="SENSOR-B",
        )

        rows = {eid: ms.evidence.get(eid) for eid in ("E1", "E2", "E3", "E4")}
        exact_duplicate_detectable = rows["E1"]["sha256"] == rows["E2"]["sha256"]
        same_source_visible = rows["E1"]["source"] == rows["E3"]["source"] == "SENSOR-A"

        qualifier = FixedQualifier(ms.evidence)
        duplicate_basis_decision = qualifier.decide((e1, e2), Authority.DERIVED_READ_ONLY)
        mixed_basis_decision = qualifier.decide((e1, e4), Authority.DERIVED_READ_ONLY)

        # This mirrors the actual action-learning carrier: evidence IDs are kept,
        # but evidence hashes/source/root ancestry are not copied into the row.
        exp = ActionOutcomeExperience(
            evidence_id="E1", execution_id="X", start_state_id="S0", capability_id="REST",
            actual_next_state_id="S1", actual_value_effect=0.5, capability_epoch=0,
            frame_epochs=(("F",0),), episode_schema_epochs=(("E",0),), value_epoch=("ENERGY",0),
        )

        candidate_fields = list(ActionOutcomePredictiveCandidate.__dataclass_fields__)
        experience_fields = list(ActionOutcomeExperience.__dataclass_fields__)

        out = {
            "schema": "microseed.ms1556.pass04.evidence-identity-quarry.v1",
            "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
            "pass": 4,
            "ms": 1556,
            "phase": "QUARRY_EXISTING_EVIDENCE_ANCESTRY",
            "discriminator": (
                "CAN_REDUNDANCY_PRESSURE_BE_PARTLY_EXPRESSED_FROM_EXISTING_CONTENT_BOUND_EVIDENCE_IDENTITY_"
                "WITHOUT_A_NEW_PROVENANCE_GRAPH"
            ),
            "ledger_observations": {
                "E1_sha256": rows["E1"]["sha256"],
                "E2_sha256": rows["E2"]["sha256"],
                "E3_sha256": rows["E3"]["sha256"],
                "E4_sha256": rows["E4"]["sha256"],
                "exact_duplicate_content_is_detectable_by_existing_sha256": exact_duplicate_detectable,
                "same_source_is_visible_in_ledger": same_source_visible,
                "different_source_is_visible_but_not_independence_proof": True,
            },
            "qualification_behavior": {
                "duplicate_content_basis_state": duplicate_basis_decision.state.value,
                "duplicate_content_basis_reason": duplicate_basis_decision.reason,
                "mixed_source_basis_state": mixed_basis_decision.state.value,
                "mixed_source_basis_reason": mixed_basis_decision.reason,
                "fixed_qualifier_checks_independence": False,
            },
            "learning_carriers": {
                "ActionOutcomeExperience_fields": experience_fields,
                "ActionOutcomePredictiveCandidate_fields": candidate_fields,
                "experience_example": exp.serializable(),
                "experience_carries_evidence_id": "evidence_id" in experience_fields,
                "candidate_carries_source_evidence_ids": "source_evidence_ids" in candidate_fields,
                "carrier_copies_evidence_sha256": any("sha" in f.lower() for f in experience_fields),
                "carrier_copies_source_identity": any(f == "source" or "source_origin" in f for f in experience_fields),
                "carrier_copies_root_ancestry": any("root" in f.lower() or "ancestry" in f.lower() for f in experience_fields),
            },
            "surviving_localization": (
                "EXACT_DUPLICATE_CONTENT_AND_SOURCE_IDENTITY_ALREADY_EXIST_IN_THE_LEDGER__ACTION_LEARNING_PRESERVES_EVIDENCE_IDS__"
                "BUT_CURRENT_QUALIFICATION_AND_CONSEQUENCE_USE_DO_NOT_PROJECT_THAT_IDENTITY_INTO_REDUNDANCY_OR_INDEPENDENCE_SEMANTICS__"
                "SHARED_STRUCTURAL_ROOT_ANCESTRY_IS_NOT_CURRENTLY_REPRESENTED"
            ),
            "composition_first_implication": (
                "BEFORE_ANY_PROVENANCE_SUBSYSTEM_TEST_A_READ_ONLY_EVIDENCE_BASIS_PROJECTION_FROM_EXISTING_EVIDENCE_IDS_TO_LEDGER_SHA_SOURCE_EXECUTION_ID"
                "__EXACT_DUPLICATE_COLLAPSE_IS_LAWFUL__SOURCE_DIFFERENCE_REMAINS_NONAUTHORITATIVE"
            ),
            "new_primitive_earned": False,
            "main_dev_mutation": "NONE",
            "pal_transfer": "NONE__PAL34_ONLY_NOMINATED_THE_REDUNDANCY_ATTACK",
            "nonclaims": [
                "SOURCE_ID_DIFFERENCE_NOT_INDEPENDENCE",
                "CONTENT_HASH_DIFFERENCE_NOT_INDEPENDENCE",
                "NO_STRUCTURAL_ROOT_ANCESTRY_EARNED",
                "NO_FIXED_QUALIFIER_PROMOTION",
            ],
        }
        path = Path(__file__).with_name("MS1556_PASS04_EVIDENCE_IDENTITY_QUARRY.json")
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
