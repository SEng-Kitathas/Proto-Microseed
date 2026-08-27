from __future__ import annotations

import inspect
import json
from pathlib import Path

from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.predictive_adaptation import (
    ActionOutcomePredictiveCurrentnessWitness,
    PredictiveCurrentnessConfig,
    nominate_drift_replacement_candidates,
)
from microseed.development.drift_recurrence import assess_projection_drift_structure

OUT = Path(__file__).with_name("MS1561_PASS09_EXISTING_ALTERNATIVE_MECHANISM_QUARRY.json")


def relation() -> QualifiedActionOutcomePredictiveRelation:
    return QualifiedActionOutcomePredictiveRelation(
        relation_id="R-CURRENT",
        candidate_id="C-OLD",
        candidate_sha256="a" * 64,
        start_state_id="S",
        capability_id="ACT",
        next_state_id="N",
        value_effect=-0.25,
        support=20,
        consistency=0.8,
        source_evidence_ids=("E1",),
        qualification_evidence_ids=("Q1",),
        holdout_support=8,
        holdout_accuracy=1.0,
        capability_epoch=1,
        frame_epochs=(("F", 1),),
        episode_schema_epochs=(("EP", 1),),
        value_epoch=("V", 1),
    )


def current_witness() -> ActionOutcomePredictiveCurrentnessWitness:
    return ActionOutcomePredictiveCurrentnessWitness(
        witness_id="W-CURRENT",
        relation_id="R-CURRENT",
        relation_candidate_sha256="a" * 64,
        status="CURRENT_WITHIN_BOUNDS",
        window_accuracies=(1.0,),
        assessed_evidence_ids=("E1",),
        drift_evidence_ids=(),
        drift_window=None,
        config=PredictiveCurrentnessConfig(),
    )


def main() -> None:
    replacements_without_drift = nominate_drift_replacement_candidates(
        relation(), current_witness(), (), min_support=8, min_consistency=0.78
    )
    projection_sig = str(inspect.signature(assess_projection_drift_structure))
    replacement_sig = str(inspect.signature(nominate_drift_replacement_candidates))

    checks = {
        "action_outcome_replacement_requires_prior_drift_witness": replacements_without_drift == (),
        "projection_drift_comparison_requires_caller_supplied_historical_candidate": "historical_candidate" in projection_sig,
        "projection_drift_comparison_requires_caller_supplied_alternative_candidate": "alternative_candidate" in projection_sig,
        "action_outcome_replacement_api_requires_existing_relation_and_witness": (
            "relation" in replacement_sig and "witness" in replacement_sig
        ),
    }
    result = {
        "milestone": "MS1561",
        "campaign_pass": 9,
        "discriminator": (
            "CAN_EXISTING_ALTERNATIVE_PREDICTIVE_STRUCTURE_OR_REPLACEMENT_LINEAGE_CARRY_"
            "SIMULTANEOUS_CURRENT_SAFE_VS_HARMFUL_ALTERNATIVES_BEFORE_A_CURRENT_RELATION_"
            "HAS_ALREADY_BEEN_QUALIFIED_AND_CHALLENGED"
        ),
        "runtime_probe": {
            "replacement_candidates_with_current_non_drift_witness": len(replacements_without_drift),
        },
        "api_quarry": {
            "assess_projection_drift_structure_signature": projection_sig,
            "nominate_drift_replacement_candidates_signature": replacement_sig,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "EXISTING_ALTERNATIVE_AND_REPLACEMENT_MACHINERY_IS_DOWNSTREAM__ACTION_OUTCOME_"
            "REPLACEMENT_REQUIRES_AN_ALREADY_QUALIFIED_RELATION_PLUS_DRIFT_WITNESS__PROJECTION_"
            "ALTERNATIVE_COMPARISON_REQUIRES_A_CALLER_SUPPLIED_ALTERNATIVE_CONSTRUCTOR__NEITHER_"
            "BOOTSTRAPS_A_SIMULTANEOUS_CURRENT_CONSEQUENCE_HYPOTHESIS_SET_FROM_BIMODAL_EVIDENCE"
        ),
        "surviving_reuse": (
            "IF_A_BOUNDED_COMPETING_CONSEQUENCE_SET_CAN_BE_LAWFULLY_NOMINATED__EXISTING_"
            "HYPOTHESISSET_ACTIVE_DISCRIMINATION_AND_EPISTEMIC_DEFICIT_LIFECYCLE_CAN_CONSUME_IT"
        ),
        "non_claims": [
            "DOES_NOT_PROVE_A_NEW_GENERAL_HYPOTHESIS_GENERATOR_IS_REQUIRED",
            "DOES_NOT_LICENSE_LATENT_REGIME_IDENTITY",
            "DOES_NOT_LICENSE_AUTOMATIC_SPLITTING_ON_ERROR",
            "DOES_NOT_MUTATE_MAINDEV",
        ],
        "breadth_rerank": (
            "ROTATE_FROM_PREDICTIVE_ALTERNATIVE_MACHINERY__TEST_WHETHER_EXISTING_EVIDENCE_"
            "BEARING_CONTRAST_CAN_FORM_A_USE_LOCAL_SAFE_VS_HARMFUL_QUESTION_DIRECTLY_FROM_"
            "OBSERVED_CURRENT_CONSEQUENCES_WITHOUT_PREDICTIVE_MODEL_MULTIPLICATION"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1561_PASS09_QUARRY_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
