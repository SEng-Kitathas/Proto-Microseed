from __future__ import annotations

import inspect
import json
from pathlib import Path

from microseed.development.epistemic import EpistemicContrastBinding, EpistemicContrastRegistry
from microseed.runtime.entity import Microseed

OUT = Path(__file__).with_name("MS1562_PASS10_EVIDENCE_BEARING_CONTRAST_FORMATION_AUDIT.json")


def main() -> None:
    entity_methods = set(dir(Microseed))
    register_sig = str(inspect.signature(Microseed.register_epistemic_contrast))
    assess_sig = str(inspect.signature(Microseed.assess_epistemic_evidence_bearing))
    binding_sig = str(inspect.signature(EpistemicContrastBinding))
    registry_doc = (EpistemicContrastRegistry.__doc__ or "").strip()

    candidate_formation_like = sorted(
        name for name in entity_methods
        if "contrast" in name.lower()
        and any(token in name.lower() for token in ("discover", "nominate", "construct", "generate", "propose"))
    )

    checks = {
        "contrast_registration_requires_caller_supplied_binding": "binding" in register_sig,
        "bearing_assessment_requires_existing_binding_id": "binding_id" in assess_sig,
        "binding_requires_caller_supplied_rows": "rows" in binding_sig,
        "binding_origin_is_supplied_or_externally_qualified_only": (
            EpistemicContrastBinding.__dataclass_fields__["binding_origin"].default == "SUPPLIED_AND_PROVENANCED"
        ),
        "no_current_entity_api_discovers_or_nominates_epistemic_contrast": candidate_formation_like == [],
        "registry_explicitly_refuses_question_or_hypothesis_invention": (
            "invent replacement hypotheses" in registry_doc and "generate semantic questions" in registry_doc
        ),
    }

    result = {
        "milestone": "MS1562",
        "campaign_pass": 10,
        "discriminator": (
            "CAN_EXISTING_EPISTEMIC_EVIDENCE_BEARING_FORM_A_USE_LOCAL_SAFE_VS_HARMFUL_"
            "CONTRAST_DIRECTLY_FROM_OBSERVED_CURRENT_CONSEQUENCES_WITHOUT_CALLER_SUPPLIED_"
            "CANDIDATE_HANDLES_AND_PREDICTIONS"
        ),
        "api_quarry": {
            "register_epistemic_contrast": register_sig,
            "assess_epistemic_evidence_bearing": assess_sig,
            "epistemic_contrast_binding": binding_sig,
            "candidate_formation_like_entity_methods": candidate_formation_like,
            "registry_contract": registry_doc,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "EXISTING_EPISTEMIC_BEARING_IS_A_VERIFIER_OVER_A_PREEXISTING_BOUNDED_CONTRAST__"
            "IT_DOES_NOT_FORM_THE_CANDIDATE_HANDLES_OR_THEIR_PREDICTED_OUTCOME_PARTITION_FROM_"
            "RAW_ACTION_OUTCOME_EVIDENCE__THEREFORE_ACTIVE_BEARING_AND_PROBING_ARE_DOWNSTREAM_"
            "OF_THE_REMAINING_USE_ADEQUACY_HYPOTHESIS_FORMATION_SEAM"
        ),
        "surviving_existing_parts": [
            "EPISTEMIC_DEFICIT_LIFECYCLE",
            "EPISTEMIC_CONTRAST_VERIFICATION",
            "DISCRIMINATING_EVIDENCE_BEARING",
            "HYPOTHESISSET_ACTIVE_DISCRIMINATION",
            "CURRENTNESS_ANCHORS",
            "TERNARY_COMMITMENT_CONJUNCTION",
        ],
        "non_claims": [
            "DOES_NOT_PROVE_SEMANTIC_SAFE_HARMFUL_LABELS_MUST_BE_STORED",
            "DOES_NOT_PROVE_A_GENERAL_QUESTION_GENERATOR_IS_REQUIRED",
            "DOES_NOT_LICENSE_PROVENANCE_OR_UNCERTAINTY_MANAGER",
            "DOES_NOT_MUTATE_MAINDEV",
        ],
        "breadth_rerank": (
            "QUARRY_EXISTING_DEVELOPMENTAL_CONSTRUCTOR_AND_RECURRENCE_ABSTRACTION_MECHANISMS_"
            "FOR_THE_SMALLER_INVARIANT__CAN_RECURRING_ACTUAL_OUTCOME_ALTERNATIVES_BE_NOMINATED_"
            "AS_EVIDENCE_BOUND_OPAQUE_CANDIDATE_HANDLES_WITHOUT_PREDICTING_WHICH_ONE_WILL_OCCUR"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1562_PASS10_AUDIT_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
