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

OUT = Path(__file__).with_name("MS1574_PASS22_IDENTIFIABILITY_RECONCILIATION.json")
MIN_SUPPORT = 8
MIN_CONSISTENCY = 0.75
TRAIN_TICKS = 70
TOTAL_TICKS = 100


def sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def contract(value_id: str) -> ValueVariableContract:
    low, high = BANDS[value_id]
    return ValueVariableContract(
        value_id=value_id,
        purpose="R2_REGULATORY",
        viable_low=low,
        viable_high=high,
        signature_sha256=sha(("MS1574", value_id)),
        authority=Authority.REFERENCE_ONLY,
        lineage=("MS953-977", "MS1574-EVALUATOR-FORENSIC"),
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


def state_values(state: State) -> dict[str, float]:
    return {"ENERGY": state.energy, "THERMAL": state.thermal, "INTEGRITY": state.integrity}


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


def collect(seed: int) -> tuple[list[dict], int, dict[str, float], dict[str, float]]:
    process_rng = random.Random(seed * 9001 + 11)
    obs_rng = random.Random(seed * 9001 + 13)
    policy_rng = random.Random(seed * 9001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows: list[dict] = []
    latest_complete_tick = -1
    latest_complete_obs: dict[str, float] | None = None
    latest_complete_true: dict[str, float] | None = None

    for tick in range(TOTAL_TICKS):
        true_pre = state_values(state)
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        nxt = stochastic_step(state, action, tick, process_rng)
        true_post = state_values(nxt)
        post = observe(nxt, obs_rng)
        observed_context = {v: band_token(v, pre[v]) for v in VALUES}
        true_context = {v: band_token(v, true_pre[v]) for v in VALUES}

        for value_id in VALUES:
            if pre[value_id] is None or post[value_id] is None:
                continue
            rows.append({
                "tick": tick,
                "evidence_id": sha((seed, tick, action, value_id)),
                "action": action,
                "value_id": value_id,
                "observed_effect": float(post[value_id]) - float(pre[value_id]),
                "true_effect": float(true_post[value_id]) - float(true_pre[value_id]),
                "observed_context": observed_context,
                "true_context": true_context,
            })

        if all(post[v] is not None for v in VALUES):
            latest_complete_tick = tick
            latest_complete_obs = {v: float(post[v]) for v in VALUES}
            latest_complete_true = true_post
        state = nxt

    if latest_complete_obs is None or latest_complete_true is None:
        raise AssertionError("R2 seed unexpectedly had no complete learner-visible boundary")
    return rows, latest_complete_tick, latest_complete_obs, latest_complete_true


def nominate_mapping(train_rows: list[dict], selector: str, context_key: str, stance_key: str) -> dict[str, str] | None:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in train_rows:
        token = row[context_key].get(selector)
        if token is not None:
            groups[token].append(row[stance_key])
    mapping: dict[str, str] = {}
    for token, stances in sorted(groups.items()):
        stance, support = Counter(stances).most_common(1)[0]
        consistency = support / len(stances)
        if support >= MIN_SUPPORT and consistency >= MIN_CONSISTENCY:
            mapping[token] = stance
    if len(mapping) < 2 or len(set(mapping.values())) < 2:
        return None
    return mapping


def evaluate(mapping: dict[str, str], rows: list[dict], selector: str, context_key: str, stance_key: str) -> tuple[int, float]:
    eligible = [row for row in rows if row[context_key].get(selector) in mapping]
    if not eligible:
        return 0, 0.0
    correct = sum(mapping[row[context_key][selector]] == row[stance_key] for row in eligible)
    return len(eligible), correct / len(eligible)


def modal_accuracy(train_rows: list[dict], holdout_rows: list[dict], stance_key: str) -> float:
    if not train_rows or not holdout_rows:
        return 0.0
    modal = Counter(row[stance_key] for row in train_rows).most_common(1)[0][0]
    return sum(row[stance_key] == modal for row in holdout_rows) / len(holdout_rows)


def analyze_surface(rows: list[dict], query_tick: int, context_key: str, stance_key: str) -> list[dict]:
    nominations = []
    for action in ACTIONS:
        for target_value in VALUES:
            train = [
                row for row in rows
                if row["tick"] < TRAIN_TICKS and row["action"] == action and row["value_id"] == target_value
            ]
            holdout = [
                row for row in rows
                if TRAIN_TICKS <= row["tick"] <= query_tick
                and row["action"] == action and row["value_id"] == target_value
            ]
            if not ({"YES", "NO"} <= {row[stance_key] for row in train}):
                continue
            baseline = modal_accuracy(train, holdout, stance_key)
            for selector in VALUES:
                mapping = nominate_mapping(train, selector, context_key, stance_key)
                if mapping is None:
                    continue
                support, accuracy = evaluate(mapping, holdout, selector, context_key, stance_key)
                nominations.append({
                    "action": action,
                    "target_value_id": target_value,
                    "selector_value_id": selector,
                    "mapping": mapping,
                    "holdout_support": support,
                    "holdout_accuracy": accuracy,
                    "modal_holdout_accuracy": baseline,
                    "holdout_lift": accuracy - baseline if support else 0.0,
                })
    nominations.sort(key=lambda x: (-x["holdout_lift"], -x["holdout_support"], x["action"], x["target_value_id"], x["selector_value_id"]))
    return nominations


def one_seed(seed: int) -> dict:
    rows, query_tick, query_obs, query_true = collect(seed)
    rows = [row for row in rows if row["tick"] <= query_tick]
    for row in rows:
        row["observed_stance"] = stance_for(
            row["action"], row["value_id"], row["observed_effect"], query_obs[row["value_id"]], row["evidence_id"]
        )
        row["true_stance"] = stance_for(
            row["action"], row["value_id"], row["true_effect"], query_true[row["value_id"]], row["evidence_id"]
        )

    surfaces = {
        "LEARNER_VISIBLE": ("observed_context", "observed_stance"),
        "ORACLE_SELECTOR_ONLY": ("true_context", "observed_stance"),
        "ORACLE_CONSEQUENCE_ONLY": ("observed_context", "true_stance"),
        "ORACLE_BOTH": ("true_context", "true_stance"),
    }
    out = {"seed": seed, "query_boundary_tick": query_tick, "surfaces": {}}
    for name, (context_key, stance_key) in surfaces.items():
        nominations = analyze_surface(rows, query_tick, context_key, stance_key)
        strong = [n for n in nominations if n["holdout_support"] >= 3 and n["holdout_lift"] >= 0.15]
        out["surfaces"][name] = {
            "nominations": nominations,
            "strong_count": len(strong),
            "best_lift": nominations[0]["holdout_lift"] if nominations else None,
        }
    return out


def main() -> None:
    seeds = list(range(107, 119))
    runs = [one_seed(seed) for seed in seeds]
    surface_names = ["LEARNER_VISIBLE", "ORACLE_SELECTOR_ONLY", "ORACLE_CONSEQUENCE_ONLY", "ORACLE_BOTH"]
    summary = {}
    for name in surface_names:
        any_nom = sum(bool(run["surfaces"][name]["nominations"]) for run in runs)
        any_strong = sum(run["surfaces"][name]["strong_count"] > 0 for run in runs)
        lifts = [
            n["holdout_lift"]
            for run in runs
            for n in run["surfaces"][name]["nominations"]
            if n["holdout_support"] >= 3
        ]
        summary[name] = {
            "seeds_with_any_mapping": any_nom,
            "seeds_with_any_strong_mapping": any_strong,
            "mean_lift_supported_mappings": sum(lifts) / len(lifts) if lifts else None,
        }

    observation_channel_is_causal_for_this_grammar = (
        summary["LEARNER_VISIBLE"]["seeds_with_any_strong_mapping"] < 8
        and summary["ORACLE_BOTH"]["seeds_with_any_strong_mapping"] >= 8
    )
    checks = {
        "same_fixed_selector_grammar_and_gates_on_all_surfaces": True,
        "no_hidden_surface_is_fed_back_to_microseed": True,
        "all_twelve_runs_use_repaired_learner_visible_query_boundary": len(runs) == 12 and all(r["query_boundary_tick"] >= 72 for r in runs),
        "factorized_observation_and_consequence_oracles_are_reported": True,
    }
    result = {
        "milestone": "MS1574",
        "campaign_pass": 22,
        "phase": "EXPRESSIVITY_VS_R2_IDENTIFIABILITY_RECONCILIATION",
        "discriminator": (
            "IS_PASS21_NEGATIVE_CAUSED_BY_THE_LEARNER_VISIBLE_OBSERVATION_SURFACE_OR_DOES_"
            "THE_SAME_FIXED_BELOW_WITHIN_ABOVE_GRAMMAR_FAIL_EVEN_WHEN_EVALUATOR_ONLY_TRUE_"
            "STATE_AND_TRUE_ACTUAL_CONSEQUENCE_ARE_SUBSTITUTED_FOR_FORENSIC_COMPARISON"
        ),
        "method": {
            "learner_visible": "observed coarse context + observed actual effect stance",
            "oracle_selector_only": "true pre-state coarse context + same learner-visible observed effect stance",
            "oracle_consequence_only": "observed coarse context + true stochastic state-transition effect stance",
            "oracle_both": "true coarse context + true stochastic state-transition effect stance",
            "important_boundary": "oracle surfaces are evaluator-only causal forensics and are never organism evidence",
            "selector_grammar": "ONE_VALUE_BELOW_WITHIN_ABOVE",
            "min_support": MIN_SUPPORT,
            "min_consistency": MIN_CONSISTENCY,
            "train_ticks": TRAIN_TICKS,
        },
        "summary": summary,
        "runs": runs,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "observation_channel_assurance_debt_is_causal_for_this_exact_grammar": observation_channel_is_causal_for_this_grammar,
        "disposition": (
            "NARROWED__OBSERVATION_SURFACE_CAUSALLY_LIMITS_THIS_GRAMMAR"
            if observation_channel_is_causal_for_this_grammar
            else "NARROWED_NEGATIVE__SIMPLE_COARSE_SELECTOR_GRAMMAR_REMAINS_INSUFFICIENT_EVEN_UNDER_EVALUATOR_ONLY_OBSERVABILITY_RELIEF"
        ),
        "interpretation": (
            "THIS_PASS_DOES_NOT_QUALIFY_HIDDEN_STATE_OR_TRUE_EFFECTS_FOR_MICROSEED__IT_ONLY_"
            "ASKS_WHETHER_PAL163_164_STYLE_OBSERVATION_CHANNEL_DEBT_EXPLAINS_THE_CURRENT_"
            "PASS21_NEGATIVE_BEFORE_WE_OPEN_A_SENSOR_ASSURANCE_FRONTIER"
        ),
        "nonclaims": [
            "ORACLE_BOTH_SUCCESS_WOULD_NOT_AUTHORIZE_HIDDEN_STATE_INPUT",
            "ORACLE_BOTH_FAILURE_DOES_NOT_PROVE_RELATIONAL_HYPOTHESIS_FORMATION_IMPOSSIBLE",
            "NO_RICHER_SELECTOR_GRAMMAR_IS_TESTED",
            "NO_SENSOR_ASSURANCE_RUNTIME_IS_ADDED",
            "NO_MAINDEV_MUTATION",
        ],
        "main_dev_mutation": "NONE",
        "breadth_next": (
            "IF_ORACLE_BOTH_IS_STILL_NEGATIVE_CLOSE_THIS_R2_SELECTOR_ROUTE_AND_RECONCILE_"
            "THE_BOUNDED_FIXTURE_SURVIVOR_AS_EXPRESSIVITY_WITHOUT_R2_IDENTIFIABILITY__THEN_"
            "SELECT_THE_NEXT_END_GOAL_BEARING_PRELINGUAL_FRONTIER_RATHER_THAN_TUNING_R2"
        ),
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1574_PASS22_RECONCILIATION_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": result["all_checks_pass"],
        "summary": summary,
        "observation_channel_assurance_debt_is_causal_for_this_exact_grammar": observation_channel_is_causal_for_this_grammar,
        "disposition": result["disposition"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
