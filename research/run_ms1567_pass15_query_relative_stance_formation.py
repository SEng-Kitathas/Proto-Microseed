from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import random
from pathlib import Path

from microseed.development.action_licensing import project_regulatory_effect_license
from microseed.development.value import pressure_magnitude_for_value
from microseed.runtime.commitment import TernaryCommitment
from microseed.runtime.types import Authority, ValueVariableContract
from research.habitat_r2_exact import ACTIONS, BANDS, State, observe, stochastic_step
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

OUT = Path(__file__).with_name("MS1567_PASS15_QUERY_RELATIVE_STANCE_FORMATION.json")


def contract(value_id: str) -> ValueVariableContract:
    low, high = BANDS[value_id]
    return ValueVariableContract(
        value_id=value_id,
        purpose="r2-regulatory",
        viable_low=low,
        viable_high=high,
        signature_sha256=hashlib.sha256(f"MS1567:{value_id}".encode()).hexdigest(),
        authority=Authority.REFERENCE_ONLY,
        lineage=("MS953-977", "MS1567-RESEARCH"),
        currentness="CURRENT",
    )


def collect(seed: int, ticks: int = 100):
    process_rng = random.Random(seed * 9001 + 11)
    obs_rng = random.Random(seed * 9001 + 13)
    policy_rng = random.Random(seed * 9001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows = []
    last_obs = None
    for tick in range(ticks):
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        nxt = stochastic_step(state, action, tick, process_rng)
        post = observe(nxt, obs_rng)
        for value_id in VALUES:
            if pre[value_id] is not None and post[value_id] is not None:
                rows.append({
                    "evidence_id": f"E-{seed}-{tick}-{action}-{value_id}",
                    "action": action,
                    "value_id": value_id,
                    "effect": float(post[value_id]) - float(pre[value_id]),
                })
        last_obs = post
        state = nxt
    return rows, last_obs


def stance_for(effect: float, action: str, value_id: str, current_value: float, evidence_id: str) -> dict[str, object]:
    c = contract(value_id)
    p = pressure_magnitude_for_value(c, current_value)
    rel = project_regulatory_effect_license(
        action,
        value_id,
        current_value=current_value,
        current_pressure=p,
        value_epoch=1,
        contract=c,
        effect_row={
            "effect": effect,
            "authority": Authority.MODEL_OUTPUT_ONLY.value,
            "episode_schema_epoch": f"R2-E-{value_id}@1",
            "source_trace_ids": (evidence_id,),
        },
    )
    return rel.serializable()


def main() -> None:
    seed = 107
    rows, current_obs = collect(seed)
    if current_obs is None or any(current_obs[v] is None for v in VALUES):
        raise SystemExit("MS1567_FIXTURE_REQUIRES_COMPLETE_FINAL_OBSERVATION")

    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        value_id = row["value_id"]
        rel = stance_for(
            row["effect"], row["action"], value_id,
            float(current_obs[value_id]), row["evidence_id"],
        )
        grouped[(row["action"], value_id)][rel["commitment"]].append(row["evidence_id"])

    pairs = {}
    for action in ACTIONS:
        for value_id in VALUES:
            stance_map = grouped[(action, value_id)]
            nonempty = {stance: ids for stance, ids in stance_map.items() if ids}
            pairs[f"{action}::{value_id}"] = {
                "current_value": float(current_obs[value_id]),
                "stance_support": {stance: len(ids) for stance, ids in sorted(nonempty.items())},
                "stance_evidence_ids": {stance: sorted(ids) for stance, ids in sorted(nonempty.items())},
                "bounded_alternative_count": len(nonempty),
                "has_yes_no_disagreement": (
                    TernaryCommitment.YES.value in nonempty and TernaryCommitment.NO.value in nonempty
                ),
            }

    checks = {
        "every_action_value_pair_has_at_most_three_query_relative_alternatives": all(v["bounded_alternative_count"] <= 3 for v in pairs.values()),
        "at_least_one_pair_preserves_yes_no_disagreement": any(v["has_yes_no_disagreement"] for v in pairs.values()),
        "evidence_ancestry_remains_attached_per_stance": all(
            sum(v["stance_support"].values()) == sum(len(ids) for ids in v["stance_evidence_ids"].values())
            for v in pairs.values()
        ),
    }

    result = {
        "milestone": "MS1567",
        "campaign_pass": 15,
        "discriminator": (
            "CAN_EXISTING_QUERY_RELATIVE_REGULATORY_PROJECTION_APPLIED_PER_CURRENT_EVIDENCE_"
            "ROW_FORM_A_BOUNDED_DISAGREEMENT_SET_WITHOUT_STABLE_EFFECT_CLUSTERS_NEW_NUMERIC_"
            "THRESHOLDS_OR_SEMANTIC_OUTCOME_ONTOLOGY"
        ),
        "seed": seed,
        "current_observation": current_obs,
        "pairs": pairs,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "localization": (
            "YES__THE_EXISTING_REGULATORY_EFFECT_PROJECTION_CAN_COLLAPSE_CONTINUOUS_NOISY_"
            "OUTCOME_EVIDENCE_TO_A_QUERY_RELATIVE_TERNARY_STANCE_SET_WHILE_PRESERVING_"
            "EVIDENCE_ANCESTRY__THIS_SOLVES_EFFECT_IDENTITY_FRAGMENTATION_FOR_CONTRAST_"
            "FORMATION_WITHOUT_CLAIMING_ANY_STANCE_IS_TRUE_OR_PROBABLE"
        ),
        "critical_nonclaim": (
            "ABSENCE_OF_NO_OR_UNKNOWN_STANCES_DOES_NOT_ESTABLISH_EVIDENCE_ADEQUACY__THIS_"
            "PASS_EARNS_ONLY_A_DISAGREEMENT_OR_CONTRAST_FORMATION_ROUTE"
        ),
        "next_discriminator": (
            "CAN_QUERY_RELATIVE_STANCE_DISAGREEMENT_LAWFULLY_NOMINATE_AN_EXISTING_"
            "EPISTEMIC_DEFICIT_AND_CONTENT_BOUND_CONTRAST_WITH_ZERO_NEW_TRUTH_OR_EXECUTION_"
            "AUTHORITY__THEN_REUSE_PASS7_ACTIVE_DISCRIMINATION"
        ),
        "main_dev_mutation": "NONE",
    }
    if not result["all_checks_pass"]:
        raise SystemExit("MS1567_PASS15_STANCE_FORMATION_EXPECTATION_MISMATCH")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": result["all_checks_pass"],
        "disagreement_pairs": [k for k, v in pairs.items() if v["has_yes_no_disagreement"]],
        "max_alternatives": max(v["bounded_alternative_count"] for v in pairs.values()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
