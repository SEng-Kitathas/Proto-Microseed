from __future__ import annotations

from collections import defaultdict
import json
import statistics
from pathlib import Path

from research.run_ms1548_pass21_r2_identifiability_audit import collect
from research.run_ms1537_pass10_r2_projection_quarry import VALUES
from research.habitat_r2_exact import ACTIONS

OUT = Path(__file__).with_name("MS1565_PASS13_R2_POSSIBILITY_FRAGMENTATION.json")
ROUND_DIGITS = 3  # frozen from Pass 12; no tuning sweep


def summarize_seed(seed: int) -> dict[str, object]:
    rows = collect(seed, 100)
    by = defaultdict(list)
    for row in rows:
        if row["observed_effect"] is not None:
            by[(row["action"], row["value_id"])].append(float(row["observed_effect"]))
    pairs = {}
    for action in ACTIONS:
        for value_id in VALUES:
            vals = by[(action, value_id)]
            rounded = [round(v, ROUND_DIGITS) for v in vals]
            unique = len(set(rounded))
            pairs[f"{action}::{value_id}"] = {
                "observations": len(vals),
                "unique_3dp_outcome_clusters": unique,
                "fragmentation_ratio": None if not vals else unique / len(vals),
                "largest_cluster_support": max((rounded.count(x) for x in set(rounded)), default=0),
            }
    return {"seed": seed, "pairs": pairs}


def main() -> None:
    seeds = list(range(100, 112))
    per_seed = [summarize_seed(seed) for seed in seeds]
    aggregate = {}
    for action in ACTIONS:
        for value_id in VALUES:
            key = f"{action}::{value_id}"
            ratios = [x["pairs"][key]["fragmentation_ratio"] for x in per_seed if x["pairs"][key]["fragmentation_ratio"] is not None]
            largest = [x["pairs"][key]["largest_cluster_support"] for x in per_seed]
            obs = [x["pairs"][key]["observations"] for x in per_seed]
            aggregate[key] = {
                "mean_observations": statistics.fmean(obs),
                "mean_fragmentation_ratio": statistics.fmean(ratios) if ratios else None,
                "median_fragmentation_ratio": statistics.median(ratios) if ratios else None,
                "max_largest_cluster_support": max(largest),
                "mean_largest_cluster_support": statistics.fmean(largest),
            }

    all_ratios = [v["mean_fragmentation_ratio"] for v in aggregate.values() if v["mean_fragmentation_ratio"] is not None]
    checks = {
        "fixed_3dp_identity_is_highly_fragmented_in_r2": statistics.fmean(all_ratios) > 0.80,
        "no_pair_builds_a_large_recurrent_exact_3dp_cluster": max(v["max_largest_cluster_support"] for v in aggregate.values()) < 8,
    }
    result = {
        "milestone": "MS1565",
        "campaign_pass": 13,
        "discriminator": (
            "DOES_PASS12_EXACT_ROUNDED_OBSERVED_POSSIBILITY_NOMINATION_GENERALIZE_TO_ONE_"
            "LIFETIME_OF_NOISY_CONTINUOUS_R2_EXPERIENCE_WITHOUT_TUNING_ITS_CLUSTER_IDENTITY"
        ),
        "frozen_rule": {"effect_round_digits": ROUND_DIGITS, "seeds": seeds, "ticks_per_lifetime": 100},
        "aggregate": aggregate,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "disposition": "REJECTED_AS_GENERAL_NOISY_POSSIBILITY_NOMINATION_MECHANISM",
        "localization": (
            "PASS12_DISCRETE_OUTCOME_IDENTITY_FRAGMENTs_UNDER_R2_SENSOR_PROCESS_NOISE__THE_"
            "FIXED_3DP_RULE_PRODUCES_NEAR_ONE_CANDIDATE_PER_OBSERVATION_AND_NO_ACTION_VALUE_"
            "PAIR_REACHES_EXISTING_MIN_SUPPORT_8_ON_A_SINGLE_EXACT_CLUSTER__DO_NOT_PROMOTE_"
            "EXACT_ROUNDED_OUTCOME_POSSIBILITY_IDENTITY"
        ),
        "next_composition_first_check": (
            "QUARRY_THE_ALREADY_EARNED_QUANTIZATION_TOLERANCE_AND_MEDIAN_RECURRENCE_MECHANISM_"
            "AS_A_CANDIDATE_IDENTITY_OPERATION_ON_OBSERVED_OUTCOME_POSSIBILITIES__ONE_FIXED_"
            "CONFIG_ONLY__NO_CLUSTERING_MODEL_ZOO"
        ),
        "main_dev_mutation": "NONE",
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1565_PASS13_EXPECTED_FRAGMENTATION_NOT_OBSERVED")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": result["all_checks_pass"],
        "mean_fragmentation": statistics.fmean(all_ratios),
        "max_largest_cluster_support": max(v["max_largest_cluster_support"] for v in aggregate.values()),
        "disposition": result["disposition"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
