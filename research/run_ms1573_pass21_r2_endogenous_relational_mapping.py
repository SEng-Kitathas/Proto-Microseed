from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import random
from pathlib import Path

from microseed.development.action_licensing import project_regulatory_effect_license
from microseed.development.value import pressure_magnitude_for_value
from microseed.runtime.types import Authority, ValueVariableContract
from research.habitat_r2_exact import ACTIONS, BANDS, State, observe, stochastic_step
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

OUT = Path(__file__).with_name("MS1573_PASS21_R2_ENDOGENOUS_RELATIONAL_MAPPING.json")

MIN_SUPPORT = 8
MIN_CONSISTENCY = 0.75
TRAIN_TICKS = 70
TOTAL_TICKS = 100


def sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def contract(value_id: str) -> ValueVariableContract:
    low, high = BANDS[value_id]
    return ValueVariableContract(
        value_id=value_id,
        purpose="R2_REGULATORY",
        viable_low=low,
        viable_high=high,
        signature_sha256=sha(("MS1573", value_id)),
        authority=Authority.REFERENCE_ONLY,
        lineage=("MS953-977", "MS1573-RESEARCH"),
        currentness="CURRENT",
    )


def band_token(value_id: str, value: float | None) -> str | None:
    if value is None:
        return None
    low, high = BANDS[value_id]
    if value < low:
        return "BELOW"
    if value > high:
        return "ABOVE"
    return "WITHIN"


def stance_for(action: str, value_id: str, effect: float, current_value: float, evidence_id: str) -> str:
    c = contract(value_id)
    pressure = pressure_magnitude_for_value(c, current_value)
    return project_regulatory_effect_license(
        action,
        value_id,
        current_value=current_value,
        current_pressure=pressure,
        value_epoch=1,
        contract=c,
        effect_row={
            "effect": effect,
            "authority": Authority.MODEL_OUTPUT_ONLY.value,
            "episode_schema_epoch": f"R2-E-{value_id}@1",
            "source_trace_ids": (evidence_id,),
        },
    ).commitment.value


def collect(seed: int) -> tuple[list[dict], dict[str, float] | None]:
    process_rng = random.Random(seed * 9001 + 11)
    obs_rng = random.Random(seed * 9001 + 13)
    policy_rng = random.Random(seed * 9001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows: list[dict] = []
    final_obs = None
    for tick in range(TOTAL_TICKS):
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        nxt = stochastic_step(state, action, tick, process_rng)
        post = observe(nxt, obs_rng)
        context = {value_id: band_token(value_id, pre[value_id]) for value_id in VALUES}
        for value_id in VALUES:
            if pre[value_id] is None or post[value_id] is None:
                continue
            rows.append({
                "tick": tick,
                "evidence_id": sha((seed, tick, action, value_id)),
                "action": action,
                "value_id": value_id,
                "effect": float(post[value_id]) - float(pre[value_id]),
                "context": context,
            })
        final_obs = post
        state = nxt
    if final_obs is None or any(final_obs[v] is None for v in VALUES):
        return rows, None
    return rows, {v: float(final_obs[v]) for v in VALUES}


def nominate_mapping(train_rows: list[dict], selector_value_id: str) -> dict[str, str] | None:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in train_rows:
        token = row["context"].get(selector_value_id)
        if token is not None:
            groups[token].append(row["target_stance"])
    mapping: dict[str, str] = {}
    stats = {}
    for token, stances in sorted(groups.items()):
        stance, support = Counter(stances).most_common(1)[0]
        consistency = support / len(stances)
        stats[token] = (stance, support, consistency)
        if support >= MIN_SUPPORT and consistency >= MIN_CONSISTENCY:
            mapping[token] = stance
    # It is only a discriminating alternative structure if at least two selector
    # results map to different target stances.
    if len(mapping) < 2 or len(set(mapping.values())) < 2:
        return None
    return mapping


def evaluate_mapping(mapping: dict[str, str], rows: list[dict], selector_value_id: str) -> dict[str, float | int]:
    eligible = [r for r in rows if r["context"].get(selector_value_id) in mapping]
    if not eligible:
        return {"support": 0, "accuracy": 0.0}
    correct = sum(mapping[r["context"][selector_value_id]] == r["target_stance"] for r in eligible)
    return {"support": len(eligible), "accuracy": correct / len(eligible)}


def modal_accuracy(train_rows: list[dict], holdout_rows: list[dict]) -> float:
    if not train_rows or not holdout_rows:
        return 0.0
    modal = Counter(r["target_stance"] for r in train_rows).most_common(1)[0][0]
    return sum(r["target_stance"] == modal for r in holdout_rows) / len(holdout_rows)


def one_seed(seed: int) -> dict:
    rows, final_obs = collect(seed)
    if final_obs is None:
        return {"seed": seed, "status": "INCOMPLETE_FINAL_OBSERVATION", "nominations": []}
    for row in rows:
        row["target_stance"] = stance_for(
            row["action"], row["value_id"], row["effect"], final_obs[row["value_id"]], row["evidence_id"]
        )

    nominations = []
    for action in ACTIONS:
        for target_value in VALUES:
            train = [r for r in rows if r["tick"] < TRAIN_TICKS and r["action"] == action and r["value_id"] == target_value]
            holdout = [r for r in rows if r["tick"] >= TRAIN_TICKS and r["action"] == action and r["value_id"] == target_value]
            train_stances = {r["target_stance"] for r in train}
            if not ({"YES", "NO"} <= train_stances):
                continue
            baseline = modal_accuracy(train, holdout)
            for selector in VALUES:
                mapping = nominate_mapping(train, selector)
                if mapping is None:
                    continue
                hold = evaluate_mapping(mapping, holdout, selector)
                nominations.append({
                    "action": action,
                    "target_value_id": target_value,
                    "selector_value_id": selector,
                    "mapping": mapping,
                    "train_support": len(train),
                    "holdout_support": hold["support"],
                    "holdout_accuracy": hold["accuracy"],
                    "modal_holdout_accuracy": baseline,
                    "holdout_lift": hold["accuracy"] - baseline if hold["support"] else 0.0,
                })
    nominations.sort(key=lambda x: (-x["holdout_lift"], -x["holdout_support"], x["action"], x["target_value_id"], x["selector_value_id"]))
    return {"seed": seed, "status": "OK", "nominations": nominations}


def main() -> None:
    seeds = list(range(107, 119))
    runs = [one_seed(seed) for seed in seeds]
    complete = [r for r in runs if r["status"] == "OK"]
    seeds_with_any = [r for r in complete if r["nominations"]]
    positive = [
        r for r in complete
        if any(n["holdout_support"] >= 3 and n["holdout_lift"] > 0.0 for n in r["nominations"])
    ]
    strong = [
        r for r in complete
        if any(n["holdout_support"] >= 3 and n["holdout_lift"] >= 0.15 for n in r["nominations"])
    ]
    total_nominations = sum(len(r["nominations"]) for r in complete)
    nomination_lifts = [n["holdout_lift"] for r in complete for n in r["nominations"] if n["holdout_support"] >= 3]

    checks = {
        "all_twelve_runs_have_complete_current_observation": len(complete) == 12,
        "fixed_gates_and_grammar_used_without_sweep": True,
        # This pass is expected to localize whether the tiny mechanism transfers;
        # the check records the result rather than forcing a green transfer.
        "transfer_result_is_explicitly_measured": True,
    }
    transfer_supported = len(strong) >= 8
    result = {
        "milestone": "MS1573",
        "campaign_pass": 21,
        "phase": "R2_SINGLE_LIFETIME_ENDOGENOUS_MAPPING_TRANSFER",
        "discriminator": (
            "CAN_THE_PASS19_RELATIONAL_UNITIZATION_FORM_A_USEFUL_DIAGNOSTIC_MAPPING_FROM_"
            "ONE_R2_LIFETIME_USING_ONLY_ALREADY_OBSERVED_COARSE_CURRENT_VALUE_RELATIONS_"
            "AND_QUERY_RELATIVE_TARGET_STANCES__WITHOUT_SUPPLYING_A_HIDDEN_REGIME_OR_"
            "DIAGNOSTIC_MAPPING"
        ),
        "fixed_configuration": {
            "seeds": seeds,
            "ticks_per_lifetime": TOTAL_TICKS,
            "train_ticks": TRAIN_TICKS,
            "holdout_ticks": TOTAL_TICKS - TRAIN_TICKS,
            "selector_grammar": "ONE_EXISTING_VALUE_RELATION_TOKEN_BELOW_WITHIN_ABOVE",
            "min_support": MIN_SUPPORT,
            "min_consistency": MIN_CONSISTENCY,
            "no_selector_conjunctions": True,
            "no_threshold_sweep": True,
            "no_hidden_regime": True,
        },
        "summary": {
            "complete_runs": len(complete),
            "seeds_with_any_discriminating_mapping": len(seeds_with_any),
            "seeds_with_any_positive_holdout_mapping": len(positive),
            "seeds_with_any_strong_holdout_mapping": len(strong),
            "total_nominated_mappings": total_nominations,
            "mean_holdout_lift_for_nominations_with_support_ge_3": (
                sum(nomination_lifts) / len(nomination_lifts) if nomination_lifts else None
            ),
            "transfer_supported_by_predeclared_breadth_rule": transfer_supported,
        },
        "runs": runs,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "disposition": (
            "SURVIVED_R2_SINGLE_LIFETIME_TRANSFER"
            if transfer_supported
            else "NARROWED_NEGATIVE__BOUNDED_RELATIONAL_UNITIZATION_DOES_NOT_RELIABLY_BOOTSTRAP_A_DIAGNOSTIC_MAPPING_FROM_CURRENT_R2_OBSERVABLE_RELATIONS_WITHIN_ONE_LIFETIME"
        ),
        "interpretation": (
            "A_POSITIVE_BOUNDED_FIXTURE_RESULT_DOES_NOT_AUTOMATICALLY_TRANSFER_TO_R2__THE_"
            "R2_TEST_ASKS_ONLY_WHETHER_EXISTING_COARSE_OBSERVABLE_RELATIONS_SUPPLY_ENOUGH_"
            "RECURRENT_CONDITIONAL_STRUCTURE_FOR_THE_TINY_UNITIZATION_TO_FORM_A_DIAGNOSTIC_"
            "MAPPING_WITHOUT_HIDDEN_LABELS"
        ),
        "nonclaims": [
            "A_NEGATIVE_DOES_NOT_DISPROVE_RELATIONAL_HYPOTHESIS_FORMATION_IN_GENERAL",
            "A_NEGATIVE_MAY_REFLECT_R2_IDENTIFIABILITY_OR_SAMPLE_LIMITS",
            "NO_PERMISSION_FOR_SELECTOR_GRAMMAR_EXPANSION_OR_PARAMETER_SEARCH",
            "NO_MAINDEV_MUTATION",
        ],
        "main_dev_mutation": "NONE",
        "breadth_next": (
            "IF_NEGATIVE_RECONCILE_WITH_PASS21_IDENTIFIABILITY_AND_PARENT_CHILD_REPRESENTABLE_NOT_IDENTIFIABLE_SCARS__"
            "DO_NOT_TRY_RICHER_SELECTOR_GRAMMARS__SEPARATE_MECHANISM_EXPRESSIVITY_FROM_ENVIRONMENTAL_IDENTIFIABILITY_BEFORE_PROMOTION"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not result["all_checks_pass"]:
        raise SystemExit("MS1573_PASS21_HARNESS_FAILURE")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    print(result["disposition"])


if __name__ == "__main__":
    main()
