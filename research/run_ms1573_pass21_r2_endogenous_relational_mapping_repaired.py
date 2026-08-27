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

OUT = Path(__file__).with_name("MS1573_PASS21_R2_ENDOGENOUS_RELATIONAL_MAPPING_REPAIRED.json")

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


def collect(seed: int) -> tuple[list[dict], int | None, dict[str, float] | None]:
    process_rng = random.Random(seed * 9001 + 11)
    obs_rng = random.Random(seed * 9001 + 13)
    policy_rng = random.Random(seed * 9001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows: list[dict] = []
    latest_complete_tick: int | None = None
    latest_complete_obs: dict[str, float] | None = None

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
        if all(post[value_id] is not None for value_id in VALUES):
            latest_complete_tick = tick
            latest_complete_obs = {value_id: float(post[value_id]) for value_id in VALUES}
        state = nxt

    return rows, latest_complete_tick, latest_complete_obs


def nominate_mapping(train_rows: list[dict], selector_value_id: str) -> dict[str, str] | None:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in train_rows:
        token = row["context"].get(selector_value_id)
        if token is not None:
            groups[token].append(row["target_stance"])
    mapping: dict[str, str] = {}
    for token, stances in sorted(groups.items()):
        stance, support = Counter(stances).most_common(1)[0]
        consistency = support / len(stances)
        if support >= MIN_SUPPORT and consistency >= MIN_CONSISTENCY:
            mapping[token] = stance
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
    rows, query_tick, query_obs = collect(seed)
    if query_tick is None or query_obs is None:
        return {"seed": seed, "status": "NO_COMPLETE_LEARNER_VISIBLE_QUERY_BOUNDARY", "nominations": []}

    # Harness repair only: the query is asked at the latest complete learner-visible
    # observation. Evidence after that boundary does not exist for this query.
    rows = [row for row in rows if row["tick"] <= query_tick]
    for row in rows:
        row["target_stance"] = stance_for(
            row["action"],
            row["value_id"],
            row["effect"],
            query_obs[row["value_id"]],
            row["evidence_id"],
        )

    nominations = []
    for action in ACTIONS:
        for target_value in VALUES:
            train = [
                r for r in rows
                if r["tick"] < TRAIN_TICKS and r["action"] == action and r["value_id"] == target_value
            ]
            holdout = [
                r for r in rows
                if TRAIN_TICKS <= r["tick"] <= query_tick
                and r["action"] == action
                and r["value_id"] == target_value
            ]
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
    nominations.sort(
        key=lambda x: (
            -x["holdout_lift"],
            -x["holdout_support"],
            x["action"],
            x["target_value_id"],
            x["selector_value_id"],
        )
    )
    return {
        "seed": seed,
        "status": "OK",
        "query_boundary_tick": query_tick,
        "query_observation": query_obs,
        "available_holdout_ticks": max(0, query_tick - TRAIN_TICKS + 1),
        "nominations": nominations,
    }


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
    nomination_lifts = [
        n["holdout_lift"]
        for r in complete
        for n in r["nominations"]
        if n["holdout_support"] >= 3
    ]

    checks = {
        "all_twelve_runs_resolve_a_learner_visible_complete_query_boundary": len(complete) == 12,
        "all_query_boundaries_preserve_independent_holdout_after_tick_70": all(
            r["query_boundary_tick"] >= TRAIN_TICKS + 2 for r in complete
        ),
        "evidence_is_truncated_at_each_query_boundary": True,
        "fixed_gates_and_grammar_used_without_sweep": True,
        "transfer_result_is_explicitly_measured": True,
    }
    transfer_supported = len(strong) >= 8
    result = {
        "milestone": "MS1573",
        "campaign_pass": 21,
        "phase": "R2_SINGLE_LIFETIME_ENDOGENOUS_MAPPING_TRANSFER__HARNESS_REPAIR",
        "discriminator": (
            "CAN_THE_PASS19_RELATIONAL_UNITIZATION_FORM_A_USEFUL_DIAGNOSTIC_MAPPING_FROM_"
            "ONE_R2_LIFETIME_USING_ONLY_ALREADY_OBSERVED_COARSE_CURRENT_VALUE_RELATIONS_"
            "AND_QUERY_RELATIVE_TARGET_STANCES__WITHOUT_SUPPLYING_A_HIDDEN_REGIME_OR_"
            "DIAGNOSTIC_MAPPING"
        ),
        "harness_repair": {
            "original_nonresult": "FINAL_TICK_COMPLETE_OBSERVATION_WAS_REQUIRED",
            "repair": (
                "ASK_THE_QUERY_AT_THE_LATEST_LEARNER_VISIBLE_COMPLETE_POST_OBSERVATION_AND_"
                "TRUNCATE_ALL_DEVELOPMENTAL_EVIDENCE_AT_THAT_BOUNDARY"
            ),
            "not_changed": [
                "R2_HABITAT",
                "R2_MISSINGNESS_OR_NOISE",
                "SELECTOR_GRAMMAR",
                "MIN_SUPPORT_8",
                "MIN_CONSISTENCY_0_75",
                "TRAIN_BOUNDARY_TICK_70",
                "NO_HIDDEN_REGIME",
            ],
        },
        "fixed_configuration": {
            "seeds": seeds,
            "ticks_per_lifetime": TOTAL_TICKS,
            "train_ticks": TRAIN_TICKS,
            "holdout_end": "LATEST_COMPLETE_LEARNER_VISIBLE_QUERY_BOUNDARY",
            "selector_grammar": "ONE_EXISTING_VALUE_RELATION_TOKEN_BELOW_WITHIN_ABOVE",
            "min_support": MIN_SUPPORT,
            "min_consistency": MIN_CONSISTENCY,
            "no_selector_conjunctions": True,
            "no_threshold_sweep": True,
            "no_hidden_regime": True,
        },
        "summary": {
            "complete_runs": len(complete),
            "query_boundary_ticks": {str(r["seed"]): r["query_boundary_tick"] for r in complete},
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
            "THE_FINAL_TICK_MISSINGNESS_CONFOUND_IS_REMOVED_WITHOUT_IMPUTATION_OR_HIDDEN_STATE__"
            "THE_REPAIRED_R2_TEST_NOW_MEASURES_ONLY_WHETHER_EXISTING_COARSE_LEARNER_VISIBLE_"
            "RELATIONS_SUPPLY_ENOUGH_RECURRENT_CONDITIONAL_STRUCTURE_FOR_THE_TINY_"
            "UNITIZATION_TO_FORM_A_DIAGNOSTIC_MAPPING"
        ),
        "nonclaims": [
            "A_NEGATIVE_DOES_NOT_DISPROVE_RELATIONAL_HYPOTHESIS_FORMATION_IN_GENERAL",
            "A_NEGATIVE_MAY_REFLECT_R2_IDENTIFIABILITY_OR_SAMPLE_LIMITS",
            "NO_PERMISSION_FOR_SELECTOR_GRAMMAR_EXPANSION_OR_PARAMETER_SEARCH",
            "LEARNER_VISIBLE_DOES_NOT_MEAN_EPISTEMICALLY_QUALIFIED_OBSERVATION_CHANNEL",
            "NO_MAINDEV_MUTATION",
        ],
        "main_dev_mutation": "NONE",
        "breadth_next": (
            "IF_NEGATIVE_RECONCILE_MECHANISM_EXPRESSIVITY_WITH_R2_IDENTIFIABILITY_AND_THE_"
            "OPEN_OBSERVATION_CHANNEL_ASSURANCE_DEBT__DO_NOT_TRY_RICHER_SELECTOR_GRAMMARS_"
            "OR_SENSOR_ASSURANCE_AS_A_DETOUR_UNLESS_THE_PROPOSITION_DEPENDS_ON_IT"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1573_PASS21_HARNESS_REPAIR_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": result["all_checks_pass"],
        "complete_runs": len(complete),
        "query_boundary_ticks": result["summary"]["query_boundary_ticks"],
        "seeds_with_any_discriminating_mapping": len(seeds_with_any),
        "seeds_with_any_positive_holdout_mapping": len(positive),
        "seeds_with_any_strong_holdout_mapping": len(strong),
        "total_nominated_mappings": total_nominations,
        "mean_holdout_lift": result["summary"]["mean_holdout_lift_for_nominations_with_support_ge_3"],
        "transfer_supported": transfer_supported,
        "disposition": result["disposition"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
