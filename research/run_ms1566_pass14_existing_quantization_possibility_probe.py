from __future__ import annotations

from collections import Counter, defaultdict
import json
import random
import statistics
from pathlib import Path

from microseed.development.discovery import DiscoveryConfig, _quantize
from microseed.development.value import residual_pressure_after_effect
from microseed.runtime.types import Authority, ValueVariableContract
from research.habitat_r2_exact import ACTIONS, BANDS, State, observe, stochastic_step
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

OUT = Path(__file__).with_name("MS1566_PASS14_EXISTING_QUANTIZATION_POSSIBILITY_PROBE.json")
CFG = DiscoveryConfig()  # exact existing assistance ancestry; no tuned override


def contract(value_id: str) -> ValueVariableContract:
    low, high = BANDS[value_id]
    return ValueVariableContract(
        value_id=value_id,
        purpose="r2-regulatory",
        viable_low=low,
        viable_high=high,
        signature_sha256=(value_id[0].lower() * 64),
        authority=Authority.REFERENCE_ONLY,
        lineage=("MS1566-RESEARCH-FIXTURE",),
        currentness="CURRENT",
    )


def relation(value_id: str, effect: float) -> str:
    c = contract(value_id)
    current = c.viable_high + 0.2  # fixed high-pressure query, evaluator fixture only
    before = residual_pressure_after_effect(c, current, 0.0)
    after = residual_pressure_after_effect(c, current, effect)
    if after < before:
        return "LOWERS_PRESSURE"
    if after > before:
        return "WORSENS_PRESSURE"
    return "NO_DISCRIMINATING_ADVANTAGE"


def collect(seed: int, ticks: int = 100):
    process_rng = random.Random(seed * 7001 + 11)
    obs_rng = random.Random(seed * 7001 + 13)
    policy_rng = random.Random(seed * 7001 + 17)
    state = State(5.3, 6.4, 6.0)
    out = []
    for tick in range(ticks):
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        nxt = stochastic_step(state, action, tick, process_rng)
        post = observe(nxt, obs_rng)
        for value_id in VALUES:
            if pre[value_id] is None or post[value_id] is None:
                continue
            effect = float(post[value_id]) - float(pre[value_id])
            q = _quantize((effect,), CFG.quantization_step)[0]
            out.append((action, value_id, effect, q))
        state = nxt
    return out


def main() -> None:
    seeds = list(range(100, 112))
    rows = [row for seed in seeds for row in collect(seed)]
    by = defaultdict(list)
    for action, value_id, effect, q in rows:
        by[(action, value_id)].append((effect, q))

    pairs = {}
    for action in ACTIONS:
        for value_id in VALUES:
            vals = by[(action, value_id)]
            counts = Counter(q for _, q in vals)
            supported = sorted((q, n) for q, n in counts.items() if n >= CFG.min_singleton_samples)
            preserved = sum(relation(value_id, effect) == relation(value_id, q) for effect, q in vals)
            pairs[f"{action}::{value_id}"] = {
                "observations": len(vals),
                "quantized_bin_count": len(counts),
                "bins_with_existing_min_singleton_support": [[q, n] for q, n in supported],
                "query_relation_preservation_rate": preserved / max(len(vals), 1),
                "zero_bin_count": counts.get(0.0, 0),
                "zero_bin_contains_both_signs": (
                    any(effect < 0 for effect, q in vals if q == 0.0)
                    and any(effect > 0 for effect, q in vals if q == 0.0)
                ),
            }

    rest = {k: v for k, v in pairs.items() if k.startswith("REST::")}
    checks = {
        "existing_quantization_reduces_exact_fragmentation_to_bounded_bin_counts": max(v["quantized_bin_count"] for v in pairs.values()) <= 8,
        "existing_quantization_produces_recurrent_supported_bins": any(v["bins_with_existing_min_singleton_support"] for v in pairs.values()),
        "rest_zero_bin_conflates_opposing_small_effect_signs_on_at_least_one_coordinate": any(v["zero_bin_contains_both_signs"] for v in rest.values()),
    }

    result = {
        "milestone": "MS1566",
        "campaign_pass": 14,
        "discriminator": (
            "CAN_THE_ALREADY_EARNED_DISCOVERY_QUANTIZATION_IDENTITY_RESCUE_NOISY_OBSERVED_"
            "POSSIBILITY_FORMATION_WITHOUT_A_NEW_CLUSTERING_MECHANISM_AND_WITHOUT_ERASING_"
            "THE_SMALL_OPPOSING_EFFECTS_THAT_MATTER_FOR_QUERY_RELATIVE_USE"
        ),
        "existing_config": {
            "quantization_step": CFG.quantization_step,
            "min_singleton_samples": CFG.min_singleton_samples,
            "residual_tolerance_l1": CFG.residual_tolerance_l1,
            "assistance_ancestry": list(CFG.assistance_ancestry()),
        },
        "seeds": seeds,
        "pairs": pairs,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "disposition": "NARROWED_NEGATIVE_FOR_DIRECT_REUSE_AS_POSSIBILITY_IDENTITY",
        "localization": (
            "EXISTING_0_5_QUANTIZATION_SOLVES_FRAGMENTATION_BUT_CAN_COLLAPSE_SMALL_OPPOSING_"
            "EFFECTS_INTO_THE_SAME_ZERO_BUCKET__INCLUDING_REST_COORDINATES__SO_DIRECT_REUSE_"
            "AS_THE_USE_ADEQUACY_POSSIBILITY_IDENTITY_WOULD_ERASE_THE_VERY_DISAGREEMENT_"
            "THE_CAMPAIGN_NEEDS_TO_PRESERVE"
        ),
        "anti_rabbit_cull": [
            "NO_QUANTIZATION_STEP_SWEEP",
            "NO_TOLERANCE_SWEEP",
            "NO_CLUSTERING_ALGORITHM_ZOO",
        ],
        "breadth_rerank": (
            "STOP_OUTCOME_CLUSTER_IDENTITY_TUNING__TEST_A_QUERY_RELATIVE_FORMATION_ROUTE_"
            "THAT_PRESERVES_OBSERVED_CONSEQUENCE_DISAGREEMENT_AS_EVIDENCE_BEARING_WITHOUT_"
            "REQUIRING_STABLE_GLOBAL_EFFECT_CLUSTERS"
        ),
        "main_dev_mutation": "NONE",
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1566_PASS14_EXPECTED_QUANTIZATION_TRADEOFF_NOT_OBSERVED")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": result["all_checks_pass"],
        "rest": rest,
        "disposition": result["disposition"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
