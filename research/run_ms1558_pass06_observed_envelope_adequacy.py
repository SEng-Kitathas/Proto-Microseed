from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from microseed.development.value import pressure_magnitude_for_value, residual_pressure_after_effect
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step, deterministic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

MIN_SUPPORT = 5  # reuse current singleton qualification support, no new threshold
REGIMES = ((0, 100), (100, 200), (200, 300))


def pv(s: State):
    return tuple(
        pressure_magnitude_for_value(value_contract(v), x)
        for v, x in zip(VALUES, (s.energy, s.thermal, s.integrity))
    )


def hidden_nonworsening(s: State, action: str, tick: int) -> bool:
    before = pv(s)
    after = pv(deterministic_step(s, action, tick))
    return all(a <= b + 1e-12 for a, b in zip(after, before)) and any(a < b - 1e-12 for a, b in zip(after, before))


def median(xs):
    ys = sorted(xs)
    return ys[len(ys)//2] if len(ys) % 2 else 0.5 * (ys[len(ys)//2-1] + ys[len(ys)//2])


def point_stance(value_id: str, current: float, xs: list[float]) -> str:
    effect = median(xs)
    contract = value_contract(value_id)
    cur = pressure_magnitude_for_value(contract, current)
    residual = residual_pressure_after_effect(contract, current, effect)
    if cur > 0:
        return "YES" if residual < cur else ("NO" if residual > cur else "UNKNOWN")
    return "YES" if residual == 0 else "NO"


def envelope_stance(value_id: str, current: float, xs: list[float]) -> str:
    if len(xs) < MIN_SUPPORT:
        return "UNKNOWN"
    contract = value_contract(value_id)
    cur = pressure_magnitude_for_value(contract, current)
    residuals = [residual_pressure_after_effect(contract, current, x) for x in xs]
    if cur > 0:
        if all(r < cur for r in residuals):
            return "YES"
        if all(r > cur for r in residuals):
            return "NO"
        return "UNKNOWN"
    if all(r == 0 for r in residuals):
        return "YES"
    if all(r > 0 for r in residuals):
        return "NO"
    return "UNKNOWN"


def license(pre, samples, mode):
    if any(pre[v] is None for v in VALUES):
        return []
    licensed = []
    for action in ACTIONS:
        stances = []
        for value_id in VALUES:
            xs = samples.get((action, value_id), [])
            if len(xs) < MIN_SUPPORT:
                stances.append("UNKNOWN")
            elif mode == "POINT":
                stances.append(point_stance(value_id, float(pre[value_id]), xs))
            else:
                stances.append(envelope_stance(value_id, float(pre[value_id]), xs))
        if all(s == "YES" for s in stances):
            licensed.append(action)
    return licensed


def evaluate(seed: int):
    process_rng = random.Random(seed * 8101 + 11)
    obs_rng = random.Random(seed * 8101 + 13)
    policy_rng = random.Random(seed * 8101 + 17)
    state = State(5.3, 6.4, 6.0)
    timeline = []
    for tick in range(300):
        true_pre = state
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        nxt = stochastic_step(state, action, tick, process_rng)
        post = observe(nxt, obs_rng)
        timeline.append((tick, true_pre, pre, action, post))
        state = nxt

    regimes = []
    for start, end in REGIMES:
        segment = timeline[start:end]
        training = segment[:70]
        validation = segment[70:]
        samples = defaultdict(list)
        for tick, true_pre, pre, action, post in training:
            for value_id in VALUES:
                if pre[value_id] is not None and post[value_id] is not None:
                    samples[(action, value_id)].append(float(post[value_id]) - float(pre[value_id]))

        modes = {
            m: {"decision": 0, "unique": 0, "safe": 0, "harmful": 0, "multiple": 0, "none": 0, "missing": 0}
            for m in ("POINT", "OBSERVED_ENVELOPE")
        }
        for tick, true_pre, pre, action, post in validation:
            for mode in modes:
                if any(pre[v] is None for v in VALUES):
                    modes[mode]["missing"] += 1
                    continue
                modes[mode]["decision"] += 1
                licensed = license(pre, samples, mode)
                if len(licensed) == 1:
                    modes[mode]["unique"] += 1
                    if hidden_nonworsening(true_pre, licensed[0], tick):
                        modes[mode]["safe"] += 1
                    else:
                        modes[mode]["harmful"] += 1
                elif len(licensed) > 1:
                    modes[mode]["multiple"] += 1
                else:
                    modes[mode]["none"] += 1
        regimes.append({"regime": start // 100, "modes": modes})
    return {"seed": seed, "regimes": regimes}


def main() -> None:
    rows = [evaluate(seed) for seed in range(100, 112)]
    summary = {}
    for regime in range(3):
        summary[str(regime)] = {}
        for mode in ("POINT", "OBSERVED_ENVELOPE"):
            total = {
                key: sum(row["regimes"][regime]["modes"][mode][key] for row in rows)
                for key in rows[0]["regimes"][regime]["modes"][mode]
            }
            total["harmful_rate_when_unique"] = total["harmful"] / max(total["unique"], 1)
            total["safe_rate_when_unique"] = total["safe"] / max(total["unique"], 1)
            summary[str(regime)][mode] = total

    envelope_nonzero_action = any(summary[str(r)]["OBSERVED_ENVELOPE"]["unique"] > 0 for r in range(3))
    uniform_harmful_rate_improvement = all(
        summary[str(r)]["OBSERVED_ENVELOPE"]["harmful_rate_when_unique"]
        <= summary[str(r)]["POINT"]["harmful_rate_when_unique"]
        for r in range(3)
    )
    out = {
        "schema": "microseed.ms1558.pass06.observed-envelope-adequacy.v1",
        "campaign": "MS1553-1577_DEVELOPMENTAL_CONSEQUENCE_EVIDENCE_ADEQUACY",
        "pass": 6,
        "ms": 1558,
        "phase": "BORING_ESTIMATOR_FREE_ADEQUACY_PROBE",
        "discriminator": (
            "CAN_A_QUERY_LOCAL_STANCE_BE_PRODUCED_BY_REUSING_ONLY_OBSERVED_EFFECT_SUPPORT_PLUS_EXISTING_VALUE_GEOMETRY_"
            "WITHOUT_CONFIDENCE_LEVELS_FITTED_MODELS_OR_NEW_THRESHOLDS"
        ),
        "rule": (
            "YES_ONLY_IF_EVERY_OBSERVED_CURRENT_SUPPORT_EFFECT_LOWERS_CURRENT_PRESSURE_OR_PRESERVES_AN_UNPRESSURED_COORDINATE__"
            "NO_ONLY_IF_EVERY_SUPPORT_EFFECT_WORSENS__OTHERWISE_UNKNOWN"
        ),
        "min_support": MIN_SUPPORT,
        "support_threshold_ancestry": "REUSES_DISCOVERYCONFIG_MIN_SINGLETON_SAMPLES_DEFAULT_5",
        "summary": summary,
        "checks": {
            "envelope_allows_some_unique_action": envelope_nonzero_action,
            "envelope_harmful_rate_not_worse_in_any_regime": uniform_harmful_rate_improvement,
        },
        "disposition": (
            "PRESSURE_SUPPORTED_BORING_QUERY_LOCAL_ENVELOPE_COMPARATOR" if envelope_nonzero_action and uniform_harmful_rate_improvement
            else "REJECTED_AS_GENERAL_ADEQUACY_MECHANISM"
        ),
        "main_dev_mutation": "NONE",
        "new_primitive_earned": False,
        "nonclaims": [
            "OBSERVED_ENVELOPE_NOT_A_GUARANTEE",
            "NO_UNSEEN_TAIL_AUTHORITY",
            "NO_CONFIDENCE_LEVEL",
            "NO_MAINDEV_PROMOTION",
            "NO_WHOLE_ORGANISM_CREDIT",
        ],
    }
    path = Path(__file__).with_name("MS1558_PASS06_OBSERVED_ENVELOPE_ADEQUACY.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
