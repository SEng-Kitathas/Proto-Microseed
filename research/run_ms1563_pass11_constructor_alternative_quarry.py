from __future__ import annotations

import json
from pathlib import Path

from microseed.development.constructor_growth import (
    ConstructorAtom,
    ConstructorProjectionSample,
    _modal_states,
)
from microseed.development.robust_constructor_growth import _exact_conflict_masks

OUT = Path(__file__).with_name("MS1563_PASS11_CONSTRUCTOR_ALTERNATIVE_QUARRY.json")


def sample(i: int, effect: str) -> ConstructorProjectionSample:
    return ConstructorProjectionSample(
        sample_id=f"S-{i:03d}",
        raw_history=(("SAME-OBS",),),
        action_token="ACT",
        effect_token=effect,
        operational_scope_id="Q",
        frame_id="FRAME",
        frame_epoch=1,
    )


def main() -> None:
    rows = tuple([sample(i, "SAFE-OUTCOME") for i in range(16)] + [sample(16 + i, "HARMFUL-OUTCOME") for i in range(4)])
    atoms = (ConstructorAtom(0, 0),)

    ordinary_modal = _modal_states(rows, atoms)
    robust_conflicts = _exact_conflict_masks(rows, atoms, 1000)

    checks = {
        "ordinary_constructor_semantic_preprocessing_collapses_same_state_action_to_one_mode": (
            ordinary_modal == (("ACT", ("SAME-OBS",), "SAFE-OUTCOME"),)
        ),
        "ordinary_constructor_preprocessing_does_not_emit_harmful_alternative_handle": all(
            effect != "HARMFUL-OUTCOME" for _, _, effect in ordinary_modal
        ),
        "robust_constructor_finds_no_discriminating_feature_mask_when_opposing_outcomes_share_identical_observation": (
            robust_conflicts == ()
        ),
    }

    result = {
        "milestone": "MS1563",
        "campaign_pass": 11,
        "discriminator": (
            "CAN_EXISTING_DEVELOPMENTAL_CONSTRUCTOR_OR_ROBUST_CONSTRUCTOR_NOMINATE_RECURRING_"
            "ACTUAL_OUTCOME_ALTERNATIVES_AS_EVIDENCE_BOUND_OPAQUE_CANDIDATE_HANDLES_WHEN_"
            "THERE_IS_NO_OBSERVABLE_CONTEXT_THAT_PREDICTS_WHICH_OUTCOME_WILL_OCCUR"
        ),
        "fixture": {
            "same_observable_state": True,
            "same_action": "ACT",
            "safe_outcomes": 16,
            "harmful_outcomes": 4,
            "note": "No gates were modified in this semantic audit. The prior zero-gate probe hit an invalid empty-support research configuration and is retained as a harness scar, not evidence.",
        },
        "ordinary_modal_states": [
            [action, list(state), effect] for action, state, effect in ordinary_modal
        ],
        "robust_exact_conflict_masks": list(robust_conflicts),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "EXISTING_CONSTRUCTOR_FAMILY_IS_PREDICTIVE_PARTITION_FORMATION__ORDINARY_"
            "CONSTRUCTION_REDUCES_IDENTICAL_STATE_ACTION_OUTCOMES_TO_A_MODE_BEFORE_SEARCH__"
            "ROBUST_CONSTRUCTION_SEARCHES_FOR_OBSERVABLE_FEATURES_THAT_SEPARATE_DISCORDANT_"
            "OUTCOMES_AND_HAS_NO_EDGE_WHEN_NONE_EXIST__NEITHER_PRESERVES_THE_RECURRING_"
            "OUTCOMES_THEMSELVES_AS_SIMULTANEOUS_CURRENT_POSSIBILITY_CANDIDATES"
        ),
        "harness_scar": (
            "DO_NOT_ZERO_ALL_CONSTRUCTOR_QUALITY_GATES_TO_PROBE_SEMANTIC_EXPRESSIVITY__THAT_"
            "CAN_FORCE_AN_INVALID_EMPTY_SUPPORT_PATH__AUDIT_THE_PRESEARCH_SEMANTICS_DIRECTLY"
        ),
        "non_claims": [
            "DOES_NOT_LICENSE_HIDDEN_STATE_OR_MIXTURE_IDENTITY",
            "DOES_NOT_REQUIRE_PREDICTING_WHICH_ALTERNATIVE_WILL_OCCUR",
            "DOES_NOT_LICENSE_GENERAL_HYPOTHESIS_GENERATION",
            "DOES_NOT_MUTATE_MAINDEV",
        ],
        "breadth_rerank": (
            "REPRESENTATION_AND_PREDICTIVE_CONSTRUCTOR_ROUTE_SATURATED_FOR_THIS_SLICE__NEXT_"
            "TEST_THE_MINIMAL_NONPREDICTIVE_OPERATION__WHETHER_RECURRENT_ACTUAL_OUTCOME_"
            "CLUSTERS_CAN_BE_PRESERVED_AS_OPAQUE_EVIDENCE_BOUND_POSSIBILITY_CANDIDATES_AND_"
            "CLASSIFIED_RELATIVE_TO_THE_CURRENT_VALUE_USE_AT_QUERY_TIME"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1563_PASS11_CONSTRUCTOR_QUARRY_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
