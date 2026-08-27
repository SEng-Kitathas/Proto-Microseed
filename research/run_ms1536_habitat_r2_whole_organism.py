from __future__ import annotations

import hashlib
import json
import random
import statistics
import tempfile
from collections import Counter
from pathlib import Path

from microseed import (
    Authority,
    CapabilityContract,
    EpisodeSchemaContract,
    Microseed,
    Observation,
    OperationalFrameContract,
    QualificationState,
    QueryObligation,
    ValueVariableContract,
)
from microseed.development.discovery import OperationalTrace

from research.habitat_r2_exact import (
    ACTIONS,
    ACTION_COST,
    BANDS,
    TICKS,
    RESTART_TICKS,
    State,
    aggregate,
    catastrophic_count,
    observe,
    run as run_baseline,
    stochastic_step,
    deterministic_step,
    violation,
    whole_viable,
)

VALUES = ("ENERGY", "THERMAL", "INTEGRITY")
TRAIN_SAMPLES_PER_ACTION_VALUE = 61


def obligation() -> QueryObligation:
    return QueryObligation("ACT", "bounded-hostile-effect", required_authority=Authority.EFFECT, operational_scope_id="R2")


def frame() -> OperationalFrameContract:
    return OperationalFrameContract(
        "R2-FRAME", "opaque-r2-regulatory-frame", hashlib.sha256(b"R2-FRAME").hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS1536-R2",), "CURRENT", qualification=QualificationState.SHADOW_QUALIFIED,
    )


def value_contract(value_id: str) -> ValueVariableContract:
    low, high = BANDS[value_id]
    return ValueVariableContract(
        value_id, "opaque-r2-regulatory", low, high, hashlib.sha256(f"R2:{value_id}:{low}:{high}".encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS953-977", "MS1536-R2"), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=("SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE", "SUPPLIED_R2_VIABILITY_INTERVAL"),
    )


def episode(value_id: str) -> EpisodeSchemaContract:
    schema_id = f"R2-E-{value_id}"
    return EpisodeSchemaContract(
        schema_id, "opaque-r2-single-value-effect-binding", hashlib.sha256(schema_id.encode()).hexdigest(),
        Authority.DERIVED_READ_ONLY, ("MS1103-1127", "MS1536-R2"), "CURRENT",
        qualification=QualificationState.SHADOW_QUALIFIED,
        frame_epochs=(("R2-FRAME", 0),), value_epochs=((value_id, 0),),
    )


def register_current_surfaces(ms: Microseed) -> None:
    ms.register_operational_frame(frame())
    for value_id in VALUES:
        ms.register_value_variable(value_contract(value_id))
        ms.register_episode_schema(episode(value_id))
    for capability_id in ACTIONS:
        ms.register_capability(CapabilityContract(
            capability_id, "opaque-r2-action", {}, {}, (), (), Authority.EFFECT,
            ("MS1536-R2",), "CURRENT", {}, query_obligation_id="ACT",
            qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda _capability_id=capability_id, **_: {"action": _capability_id},
            operational_scope_id="R2",
        ))


def collect_pre_drift_random_training(seed: int) -> list[tuple[str, str, float]]:
    process_rng = random.Random(seed * 3001 + 11)
    obs_rng = random.Random(seed * 3001 + 13)
    policy_rng = random.Random(seed * 3001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows: list[tuple[str, str, float]] = []
    counts = Counter()
    for _ in range(20000):
        if all(counts[(action, value_id)] >= TRAIN_SAMPLES_PER_ACTION_VALUE for action in ACTIONS for value_id in VALUES):
            break
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        next_state = stochastic_step(state, action, 0, process_rng)  # declared pre-drift regime only
        post = observe(next_state, obs_rng)
        for value_id in VALUES:
            if counts[(action, value_id)] >= TRAIN_SAMPLES_PER_ACTION_VALUE:
                continue
            if pre[value_id] is None or post[value_id] is None:
                continue
            rows.append((action, value_id, float(post[value_id] - pre[value_id])))
            counts[(action, value_id)] += 1
        state = next_state
    if any(counts[(action, value_id)] < TRAIN_SAMPLES_PER_ACTION_VALUE for action in ACTIONS for value_id in VALUES):
        raise RuntimeError("PRE_DRIFT_RANDOM_TRAINING_COVERAGE_INCOMPLETE")
    return rows


def seed_training(ms: Microseed, rows: list[tuple[str, str, float]]) -> None:
    for index, (action, value_id, effect) in enumerate(rows):
        ms.record_operational_trace(OperationalTrace(
            trace_id=f"R2-TRAIN-{index}-{action}-{value_id}", steps=(action,), step_effects=((effect,),),
            frame_id="R2-FRAME", episode_schema_id=f"R2-E-{value_id}", operational_scope_id="R2", obligation_id="ACT",
        ))


def pressure_vector(state: State) -> tuple[float, float, float]:
    out=[]
    for value_id, x in zip(VALUES, (state.energy, state.thermal, state.integrity)):
        low, high = BANDS[value_id]
        out.append(low-x if x < low else x-high if x > high else 0.0)
    return tuple(out)


def hidden_action_dominated(state: State, action: str, tick: int) -> bool:
    chosen = deterministic_step(state, action, tick)
    chosen_vec = pressure_vector(chosen) + (ACTION_COST[action],)
    for other in ACTIONS + ("NO_ACTION",):
        if other == action:
            continue
        candidate = deterministic_step(state, other, tick)
        other_vec = pressure_vector(candidate) + (ACTION_COST[other],)
        if all(o <= c + 1e-12 for o, c in zip(other_vec, chosen_vec)) and any(o < c - 1e-12 for o, c in zip(other_vec, chosen_vec)):
            return True
    return False


def run_microseed(seed: int, training_rows: list[tuple[str, str, float]]) -> dict:
    td = tempfile.TemporaryDirectory(prefix=f"microseed-ms1536-{seed}-")
    state_dir = Path(td.name)
    ms = Microseed(state_dir)
    register_current_surfaces(ms)
    seed_training(ms, training_rows)

    process_rng = random.Random(seed * 1009 + 17)
    obs_rng = random.Random(seed * 1009 + 23)
    state = State(5.3, 6.4, 6.0)
    viable = 0
    violations=[]
    cats=0
    cost=0.0
    missing=0
    actions=Counter()
    abstentions=Counter()
    hidden_dominated=0
    outcome_count=0
    no_observed_outcome=0
    nomination_events=0

    for tick in range(TICKS):
        if tick in RESTART_TICKS:
            ms = Microseed(state_dir)
            register_current_surfaces(ms)

        pre_obs = observe(state, obs_rng)
        missing += sum(value is None for value in pre_obs.values())
        action = "NO_ACTION"
        execution_id = None

        if any(pre_obs[value_id] is None for value_id in VALUES):
            abstentions["MISSING_CURRENT_SENSOR_COORDINATE"] += 1
        else:
            for value_id in VALUES:
                ms.observe_value_state(value_id, float(pre_obs[value_id]))
            ms.observe_opaque_control_state(
                Observation(f"R2-CTRL-{seed}-{tick}", "R2_SENSOR", "control", "R2-OPAQUE-STATE", authority=Authority.OBSERVATION_ONLY),
                evidence_id=f"R2-CTRL-EVID-{seed}-{tick}",
            )
            nominated = ms.nominate_multi_value_action_intent(VALUES, obligation())
            if nominated.get("status") != "ACTION_INTENT_NOMINATED":
                abstentions[str(nominated.get("reason", nominated.get("status")))] += 1
            else:
                executed = ms.execute_bounded_action(nominated["intent"]["intent_id"], obligation())
                if executed.get("status") != "ACTION_EXECUTED":
                    abstentions[str(executed.get("reason", executed.get("status")))] += 1
                else:
                    action = str(executed["handler_value"]["action"])
                    execution_id = str(executed["execution"]["execution_id"])
                    if hidden_action_dominated(state, action, tick):
                        hidden_dominated += 1

        actions[action] += 1
        cost += ACTION_COST[action]
        state = stochastic_step(state, action, tick, process_rng)

        if execution_id is not None:
            post_obs = observe(state, obs_rng)
            missing += sum(value is None for value in post_obs.values())
            observed_values = {value_id: float(value) for value_id, value in post_obs.items() if value is not None}
            if observed_values:
                outcome = ms.record_bounded_action_outcome(
                    execution_id,
                    Observation(
                        f"R2-OUT-{seed}-{tick}", "R2_SENSOR", f"action-execution:{execution_id}",
                        {"next_state_id": "R2-OPAQUE-STATE", "observed_values": observed_values},
                        authority=Authority.OBSERVATION_ONLY,
                    ),
                    evidence_id=f"R2-OUT-EVID-{seed}-{tick}",
                )
                if outcome.get("status") == "ACTION_OUTCOME_OBSERVED":
                    outcome_count += 1
                    candidates = ms.nominate_action_outcome_predictive_candidates(min_support=8, min_consistency=.78)
                    nomination_events += int(bool(candidates))
            else:
                no_observed_outcome += 1

        viable += int(whole_viable(state))
        violations.append(violation(state))
        cats += catastrophic_count(state)

    result = {
        "seed": seed,
        "whole_viability": viable / TICKS,
        "mean_violation": statistics.fmean(violations),
        "catastrophic_coordinate_ticks": cats,
        "resource_spend": cost,
        "missing_observations": missing,
        "final_state": {"energy": state.energy, "thermal": state.thermal, "integrity": state.integrity},
        "actions": dict(actions),
        "abstentions": dict(abstentions),
        "hidden_pareto_dominated_executions": hidden_dominated,
        "executions": sum(actions[action] for action in ACTIONS),
        "outcomes_recorded": outcome_count,
        "unobserved_executed_outcomes": no_observed_outcome,
        "action_outcome_experience_rows": len(ms._action_outcome_experiences()),
        "action_outcome_candidate_count": len(ms.action_outcome_learning.candidates),
        "candidate_nomination_ticks": nomination_events,
        "main_dev_mutation": "NONE",
        "supplied_random_training_assistance": True,
    }
    td.cleanup()
    return result


def main() -> None:
    seeds = [100, 101, 102]
    training = collect_pre_drift_random_training(1536)
    microseed_rows = [run_microseed(seed, training) for seed in seeds]
    baseline_rows = {
        policy: [run_baseline(policy, seed) for seed in seeds]
        for policy in ("ORACLE_EVALUATOR_CEILING", "FIXED_CYCLE", "RANDOM", "PASSIVE_NO_ACTION")
    }
    out = {
        "schema": "microseed.ms1536.pass09.r2-whole-organism.v1",
        "habitat_id": "HABITAT-R2-MS1528-ABSTENTION-COMPLETE-2026-08-24",
        "seeds": seeds,
        "training_assistance": {
            "kind": "PRE_DRIFT_RANDOM_EXPLORATION__NO_HIDDEN_EFFECT_LABELS",
            "rows": len(training),
            "per_action_value_minimum": TRAIN_SAMPLES_PER_ACTION_VALUE,
            "competence_credit": "NONE",
        },
        "microseed_rows": microseed_rows,
        "microseed_aggregate": aggregate(microseed_rows),
        "baseline_aggregate": {policy: aggregate(rows) for policy, rows in baseline_rows.items()},
        "baseline_rows": baseline_rows,
        "nonclaims": [
            "THREE_SEED_BUILD_DERIVE_ASSAY_NOT_FULL_CAMPAIGN_PROMOTION",
            "SUPPLIED_RANDOM_PRETRAINING_IS_ASSISTANCE_DEBT",
            "HIDDEN_STATE_USED_ONLY_FOR_EVALUATION_NOT_ORGANISM_EVIDENCE",
            "NO_MAIN_DEV_MUTATION",
            "NO_LANGUAGE",
        ],
    }
    path = Path(__file__).with_name("MS1536_PASS09_R2_WHOLE_ORGANISM.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "microseed": out["microseed_aggregate"],
        "baselines": out["baseline_aggregate"],
        "microseed_actions": [row["actions"] for row in microseed_rows],
        "hidden_dominated": [row["hidden_pareto_dominated_executions"] for row in microseed_rows],
        "candidate_counts": [row["action_outcome_candidate_count"] for row in microseed_rows],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
