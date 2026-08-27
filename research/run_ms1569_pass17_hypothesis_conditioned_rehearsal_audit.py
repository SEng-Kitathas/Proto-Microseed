from __future__ import annotations

import inspect
import json
from pathlib import Path

from microseed.development.rehearsal import RehearsalTransitionRelation, propose_counterfactual_rehearsal
from microseed.runtime.entity import Microseed

OUT = Path(__file__).with_name("MS1569_PASS17_HYPOTHESIS_CONDITIONED_REHEARSAL_AUDIT.json")


def main() -> None:
    relation_fields = tuple(RehearsalTransitionRelation.__dataclass_fields__)
    rehearsal_sig = str(inspect.signature(propose_counterfactual_rehearsal))
    routing_sig = str(inspect.signature(Microseed.nominate_projection_conditioned_relation_routing))

    checks = {
        "rehearsal_relation_has_no_epistemic_hypothesis_identity": not any("hypoth" in name.lower() for name in relation_fields),
        "counterfactual_rehearsal_has_no_live_hypothesis_conditioning_input": "hypoth" not in rehearsal_sig.lower(),
        "projection_conditioned_routing_requires_preexisting_projection_id": "projection_id" in routing_sig,
        "projection_conditioned_routing_requires_caller_supplied_bucket_overrides": "bucket_action_overrides" in routing_sig,
    }

    result = {
        "milestone": "MS1569",
        "campaign_pass": 17,
        "discriminator": (
            "CAN_EXISTING_REHEARSAL_OR_PROJECTION_CONDITIONED_ACTION_OUTCOME_RELATIONS_"
            "PREDICT_ONE_DIAGNOSTIC_PROBE_DIFFERENTLY_UNDER_EACH_LIVE_USE_ADEQUACY_"
            "ALTERNATIVE_WITHOUT_A_PREEXISTING_QUALIFIED_SELECTOR_OR_CALLER_SUPPLIED_ROUTING"
        ),
        "api_quarry": {
            "rehearsal_relation_fields": list(relation_fields),
            "propose_counterfactual_rehearsal_signature": rehearsal_sig,
            "projection_conditioned_routing_signature": routing_sig,
        },
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "EXISTING_REHEARSAL_PREDICTS_FROM_CURRENT_STATE_ACTION_RELATIONS_AND_EXISTING_"
            "PROJECTION_ROUTING_CONDITIONS_ON_AN_ALREADY_QUALIFIED_OPAQUE_SELECTOR__NEITHER_"
            "REPRESENTS_A_LIVE_EPISTEMIC_ALTERNATIVE_AS_A_COUNTERFACTUAL_MODEL_UNDER_WHICH_"
            "A_DIAGNOSTIC_PROBE_CAN_HAVE_A_DIFFERENT_PREDICTED_OUTCOME__THAT_MAPPING_REMAINS_"
            "SUPPLIED_IN_PASS7_PASS16_FIXTURES"
        ),
        "candidate_missing_capability_pressure": (
            "BOUNDED_COUNTERFACTUAL_HYPOTHESIS_CONSTRUCTION__FORM_MORE_THAN_ONE_EVIDENCE_"
            "ANCHORED_POSSIBLE_RELATION_AND_DERIVE_WHAT_LAWFULLY_AVAILABLE_OBSERVATION_OR_"
            "INTERACTION_WOULD_DIFFER_IF_EACH_WERE_THE_CASE__WITHOUT_GRANTING_ANY_ALTERNATIVE_"
            "TRUTH_OR_REGIME_IDENTITY"
        ),
        "non_claims": [
            "DOES_NOT_EARN_A_GENERAL_WORLD_MODEL_GENERATOR",
            "DOES_NOT_EARN_LATENT_STATE_IDENTITY",
            "DOES_NOT_EARN_A_PLANNER_OR_SCHEDULER",
            "DOES_NOT_MUTATE_MAINDEV",
        ],
        "breadth_rerank": (
            "RECONCILE_WITH_THE_OLDER_BRAIN_LAB_MODEL_SPACE_MISSPECIFICATION_SCAR_AND_PARENT_"
            "CHILD_REPRESENTATION_GROWTH_PRESSURE__THEN_TEST_ONE_MINIMAL_BOUNDED_HYPOTHESIS_"
            "CONSTRUCTION_GRAMMAR_AGAINST_A_BORING_BASELINE_BEFORE_ANY_CODE_INTEGRATION"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1569_PASS17_AUDIT_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
