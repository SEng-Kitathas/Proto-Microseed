from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from microseed.development.action_learning import (
    ActionOutcomeExperience,
    nominate_action_outcome_candidates,
)

OUT = Path(__file__).with_name("MS1560_PASS08_BIMODAL_CANDIDATE_PRESERVATION.json")


def row(i: int, effect: float) -> ActionOutcomeExperience:
    return ActionOutcomeExperience(
        evidence_id=f"E-{i:03d}",
        execution_id=f"X-{i:03d}",
        start_state_id="S-CURRENT",
        capability_id="ACT",
        actual_next_state_id="S-NEXT",
        actual_value_effect=effect,
        capability_epoch=1,
        frame_epochs=(("FRAME", 1),),
        episode_schema_epochs=(("EPISODE", 1),),
        value_epoch=("VALUE", 1),
    )


def fixture(safe: int, harmful: int) -> tuple[ActionOutcomeExperience, ...]:
    rows = [row(i, -0.25) for i in range(safe)]
    rows.extend(row(safe + i, +0.25) for i in range(harmful))
    return tuple(rows)


def summarize(rows: Iterable[ActionOutcomeExperience]) -> dict[str, object]:
    rows = tuple(rows)
    candidates = nominate_action_outcome_candidates(rows)
    observed = {
        "safe_minus_0_25": sum(1 for r in rows if r.actual_value_effect == -0.25),
        "harmful_plus_0_25": sum(1 for r in rows if r.actual_value_effect == +0.25),
    }
    return {
        "observed_clusters": observed,
        "candidate_count": len(candidates),
        "candidates": [c.serializable() for c in candidates],
        "minority_cluster_semantically_exposed": any(c.value_effect == +0.25 for c in candidates)
        and any(c.value_effect == -0.25 for c in candidates),
        "all_observation_evidence_ids_retained_in_modal_candidate_ancestry": (
            bool(candidates)
            and set(candidates[0].source_evidence_ids) == {r.evidence_id for r in rows}
        ),
    }


def main() -> None:
    cases = {
        "80_20": summarize(fixture(16, 4)),
        "70_30": summarize(fixture(14, 6)),
        "50_50": summarize(fixture(10, 10)),
    }

    checks = {
        "80_20_native_gate_nominates_only_dominant_mode": (
            cases["80_20"]["candidate_count"] == 1
            and cases["80_20"]["candidates"][0]["value_effect"] == -0.25
            and cases["80_20"]["minority_cluster_semantically_exposed"] is False
        ),
        "80_20_candidate_ancestry_still_contains_minority_evidence_ids": (
            cases["80_20"]["all_observation_evidence_ids_retained_in_modal_candidate_ancestry"] is True
        ),
        "70_30_native_gate_nominates_no_candidate": cases["70_30"]["candidate_count"] == 0,
        "50_50_native_gate_nominates_no_candidate": cases["50_50"]["candidate_count"] == 0,
        "no_case_exposes_two_competing_consequence_candidates": all(
            case["minority_cluster_semantically_exposed"] is False for case in cases.values()
        ),
    }

    result = {
        "milestone": "MS1560",
        "campaign_pass": 8,
        "discriminator": (
            "CAN_EXISTING_ACTION_OUTCOME_LEARNING_PRESERVE_OR_NOMINATE_MULTIPLE_"
            "EVIDENCE_SUPPORTED_CONSEQUENCE_ALTERNATIVES_FOR_ONE_CURRENT_ACTION_VALUE_"
            "USE_QUERY_WITHOUT_A_NEW_UNCERTAINTY_MODEL_OR_HYPOTHESIS_GENERATOR"
        ),
        "fixed_native_gates": {"min_support": 8, "min_consistency": 0.78, "effect_round_digits": 3},
        "cases": cases,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "CURRENT_ACTION_OUTCOME_NOMINATION_COLLAPSES_ONE_ANCESTRY_GROUP_TO_AT_MOST_ONE_"
            "MODAL_CONSEQUENCE_CANDIDATE_OR_NONE__MINORITY_CONTRADICTORY_EVIDENCE_IDS_REMAIN_"
            "IN_ANCESTRY_WHEN_A_DOMINANT_CANDIDATE_EXISTS_BUT_THEIR_ALTERNATIVE_CONSEQUENCE_"
            "SEMANTICS_ARE_NOT_PRESERVED_AS_A_COMPETING_CANDIDATE_SET"
        ),
        "non_claims": [
            "DOES_NOT_PROVE_A_NEW_HYPOTHESIS_GENERATOR_IS_REQUIRED",
            "DOES_NOT_LICENSE_MIXTURE_MODELS_OR_LATENT_STATE",
            "DOES_NOT_PROMOTE_PAL_PROVENANCE_OR_RELIABILITY_ARCHITECTURE",
            "DOES_NOT_MUTATE_MAINDEV",
        ],
        "next_composition_first_check": (
            "QUARRY_EXISTING_ALTERNATIVE_PREDICTIVE_STRUCTURE_AND_REPLACEMENT_LINEAGE_ONCE__"
            "TEST_WHETHER_IT_CAN_CARRY_SIMULTANEOUS_CURRENT_SAFE_VS_HARMFUL_ALTERNATIVES_"
            "BEFORE_ANY_NEW_CANDIDATE_SET_STRUCTURE_IS_ADMITTED"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1560_PASS08_ASSAY_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
