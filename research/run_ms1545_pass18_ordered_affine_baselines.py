from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from microseed.development.value import pressure_magnitude_for_value, residual_pressure_after_effect
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

MIN_ACTION_SUPPORT = 3


def stance_from_effect(value_id: str, current_value: float, effect: float) -> str:
    contract = value_contract(value_id)
    current_pressure = pressure_magnitude_for_value(contract, current_value)
    residual = residual_pressure_after_effect(contract, current_value, effect)
    if current_pressure > 0:
        if residual < current_pressure:
            return "YES"
        if residual > current_pressure:
            return "NO"
        return "UNKNOWN"
    return "YES" if residual == 0 else "NO"


def rows(seed: int, channel: str) -> list[dict[str, float | int | str]]:
    process_rng = random.Random(seed * 5003 + 11)
    obs_rng = random.Random(seed * 5003 + 13)
    policy_rng = random.Random(seed * 5003 + 17)
    state = State(5.3, 6.4, 6.0)
    out: list[dict[str, float | int | str]] = []
    for tick in range(100):
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        next_state = stochastic_step(state, action, tick, process_rng)
        post = observe(next_state, obs_rng)
        if pre[channel] is not None and post[channel] is not None:
            pre_value = float(pre[channel])
            effect = float(post[channel]) - pre_value
            out.append(
                {
                    "tick": tick,
                    "action": action,
                    "pre_value": pre_value,
                    "effect": effect,
                    "actual_stance": stance_from_effect(channel, pre_value, effect),
                }
            )
        state = next_state
    return out


def median_by_action(train: list[dict]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in train:
        grouped[str(row["action"])].append(float(row["effect"]))
    return {
        action: float(statistics.median(effects))
        for action, effects in grouped.items()
        if len(effects) >= MIN_ACTION_SUPPORT
    }


def fit_affine(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if len(points) < MIN_ACTION_SUPPORT:
        return None
    mean_x = statistics.fmean(x for x, _ in points)
    mean_y = statistics.fmean(y for _, y in points)
    denom = sum((x - mean_x) ** 2 for x, _ in points)
    if denom <= 1e-12:
        return mean_y, 0.0
    slope = sum((x - mean_x) * (y - mean_y) for x, y in points) / denom
    intercept = mean_y - slope * mean_x
    return intercept, slope


def state_only_affine(train: list[dict]) -> tuple[float, float] | None:
    return fit_affine([(float(row["pre_value"]), float(row["effect"])) for row in train])


def additive_action_affine(train: list[dict]) -> tuple[dict[str, float], float] | None:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in train:
        grouped[str(row["action"])].append((float(row["pre_value"]), float(row["effect"])))
    usable = {action: pts for action, pts in grouped.items() if len(pts) >= MIN_ACTION_SUPPORT}
    if len(usable) != len(ACTIONS):
        return None

    action_means = {
        action: (
            statistics.fmean(x for x, _ in pts),
            statistics.fmean(y for _, y in pts),
        )
        for action, pts in usable.items()
    }
    numerator = 0.0
    denominator = 0.0
    for action, pts in usable.items():
        mean_x, mean_y = action_means[action]
        for x, y in pts:
            numerator += (x - mean_x) * (y - mean_y)
            denominator += (x - mean_x) ** 2
    slope = numerator / denominator if denominator > 1e-12 else 0.0
    intercepts = {
        action: mean_y - slope * mean_x
        for action, (mean_x, mean_y) in action_means.items()
    }
    return intercepts, slope


def action_specific_affine(train: list[dict]) -> dict[str, tuple[float, float]]:
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in train:
        grouped[str(row["action"])].append((float(row["pre_value"]), float(row["effect"])))
    result: dict[str, tuple[float, float]] = {}
    for action, points in grouped.items():
        model = fit_affine(points)
        if model is not None:
            result[action] = model
    return result


def predict(model_name: str, row: dict, models: dict) -> float | None:
    action = str(row["action"])
    x = float(row["pre_value"])
    if model_name == "ACTION_MEDIAN":
        return models[model_name].get(action)
    if model_name == "STATE_ONLY_AFFINE":
        model = models[model_name]
        if model is None:
            return None
        intercept, slope = model
        return intercept + slope * x
    if model_name == "ACTION_PLUS_SHARED_SLOPE":
        model = models[model_name]
        if model is None:
            return None
        intercepts, slope = model
        if action not in intercepts:
            return None
        return intercepts[action] + slope * x
    if model_name == "ACTION_SPECIFIC_AFFINE":
        model = models[model_name].get(action)
        if model is None:
            return None
        intercept, slope = model
        return intercept + slope * x
    raise ValueError(model_name)


def evaluate(seed: int, channel: str) -> dict:
    samples = rows(seed, channel)
    cut = max(1, int(len(samples) * 0.70))
    train = samples[:cut]
    validation = samples[cut:]

    models = {
        "ACTION_MEDIAN": median_by_action(train),
        "STATE_ONLY_AFFINE": state_only_affine(train),
        "ACTION_PLUS_SHARED_SLOPE": additive_action_affine(train),
        "ACTION_SPECIFIC_AFFINE": action_specific_affine(train),
    }
    names = tuple(models)
    stats = {name: {"correct": 0, "known": 0} for name in names}
    details = []
    for row in validation:
        actual = str(row["actual_stance"])
        row_detail = {
            "tick": int(row["tick"]),
            "action": str(row["action"]),
            "pre_value": float(row["pre_value"]),
            "actual": actual,
            "predictions": {},
        }
        for name in names:
            predicted_effect = predict(name, row, models)
            if predicted_effect is None or not math.isfinite(predicted_effect):
                predicted_stance = None
            else:
                predicted_stance = stance_from_effect(channel, float(row["pre_value"]), predicted_effect)
                stats[name]["known"] += 1
                stats[name]["correct"] += int(predicted_stance == actual)
            row_detail["predictions"][name] = {
                "effect": predicted_effect,
                "stance": predicted_stance,
            }
        details.append(row_detail)

    n = max(len(validation), 1)
    result_models = {}
    for name in names:
        known = stats[name]["known"]
        correct = stats[name]["correct"]
        result_models[name] = {
            "coverage": known / n,
            "accuracy_all_rows": correct / n,
            "accuracy_when_available": correct / max(known, 1),
        }
    baseline = result_models["ACTION_MEDIAN"]["accuracy_all_rows"]
    state_only = result_models["STATE_ONLY_AFFINE"]["accuracy_all_rows"]
    for name in names:
        result_models[name]["lift_over_action_median"] = result_models[name]["accuracy_all_rows"] - baseline
        result_models[name]["lift_over_state_only"] = result_models[name]["accuracy_all_rows"] - state_only

    return {
        "seed": seed,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "models": result_models,
        "details": details,
    }


def summarize(rows_: list[dict]) -> dict:
    model_names = tuple(rows_[0]["models"])
    summary = {}
    for name in model_names:
        summary[name] = {
            "mean_coverage": statistics.fmean(r["models"][name]["coverage"] for r in rows_),
            "mean_accuracy_all_rows": statistics.fmean(r["models"][name]["accuracy_all_rows"] for r in rows_),
            "mean_accuracy_when_available": statistics.fmean(r["models"][name]["accuracy_when_available"] for r in rows_),
            "mean_lift_over_action_median": statistics.fmean(r["models"][name]["lift_over_action_median"] for r in rows_),
            "mean_lift_over_state_only": statistics.fmean(r["models"][name]["lift_over_state_only"] for r in rows_),
            "positive_lift_over_action_median_seeds": sum(r["models"][name]["lift_over_action_median"] > 0 for r in rows_),
            "positive_lift_over_state_only_seeds": sum(r["models"][name]["lift_over_state_only"] > 0 for r in rows_),
        }
    return summary


def main() -> None:
    channels = {}
    for channel in VALUES:
        seed_rows = [evaluate(seed, channel) for seed in range(100, 112)]
        channels[channel] = {
            "seeds": seed_rows,
            "summary": summarize(seed_rows),
        }

    candidate = "ACTION_PLUS_SHARED_SLOPE"
    material = all(
        channels[channel]["summary"][candidate]["mean_lift_over_action_median"] >= 0.05
        and channels[channel]["summary"][candidate]["positive_lift_over_action_median_seeds"] >= 8
        and channels[channel]["summary"][candidate]["mean_lift_over_state_only"] >= 0.03
        for channel in VALUES
    )

    out = {
        "schema": "microseed.ms1545.pass18.ordered-affine-baselines.v1",
        "discriminator": "CAN_BORING_ORDERED_SCALAR_GENERALIZATION_CLOSE_SINGLE_LIFETIME_R2_SAMPLE_EFFICIENCY_WITHOUT_NEW_STATE_OR_LEARNER_ARCHITECTURE",
        "data_boundary": "ONE_R2_LIFETIME_PRE_DRIFT__NOISY_OBSERVED_CHANNEL_VALUE_PLUS_ACTUAL_ACTION_EFFECT_ONLY",
        "split": "FIRST_70_PERCENT_TRAIN__LAST_30_PERCENT_VALIDATION",
        "baselines": {
            "ACTION_MEDIAN": "per-action median effect; existing global-action-style boring baseline",
            "STATE_ONLY_AFFINE": "single affine effect model over ordered current scalar; intentionally removes action identity",
            "ACTION_PLUS_SHARED_SLOPE": "per-action intercept plus one shared scalar slope; five-parameter boring ordered model",
            "ACTION_SPECIFIC_AFFINE": "independent affine effect model per action; eight-parameter richer boring comparator",
        },
        "fixed_support_rule": MIN_ACTION_SUPPORT,
        "channels": channels,
        "research_only_materiality_gate": {
            "candidate": candidate,
            "mean_lift_over_action_median_ge": 0.05,
            "positive_seed_count_ge": 8,
            "mean_lift_over_state_only_ge": 0.03,
            "constitutional_authority": "NONE",
        },
        "disposition": (
            "BORING_ORDERED_GENERALIZATION_MATERIALLY_CLOSES_SINGLE_LIFETIME_GAP"
            if material
            else "BORING_ORDERED_GENERALIZATION_INSUFFICIENT"
        ),
        "nonclaims": [
            "NO_MAINDEV_MUTATION",
            "NO_NEW_PRIMITIVE",
            "NO_WHOLE_ORGANISM_CREDIT",
            "NO_LINEARITY_LAW",
            "NO_THRESHOLD_CONSTITUTION",
            "NO_HIDDEN_STATE",
            "NO_MODEL_SELECTION_SWEEP",
        ],
    }
    path = Path(__file__).with_name("MS1545_PASS18_ORDERED_AFFINE_BASELINES.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "disposition": out["disposition"],
        "channels": {
            channel: channels[channel]["summary"]
            for channel in VALUES
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
