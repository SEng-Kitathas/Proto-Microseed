from __future__ import annotations

import json
import math
import random
from pathlib import Path

from microseed.development.projection_discovery import ProjectionDiscoveryConfig, ProjectionSample, discover_epistemic_projection_candidates
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step

VALUES = ("ENERGY", "THERMAL", "INTEGRITY")
RAW_STEP = 0.5
EFFECT_STEP = 0.25


def qtoken(value: float, step: float) -> str:
    q = round(float(value) / step) * step
    return f"{q:.2f}"


def collect(seed: int, channel: str) -> list[ProjectionSample]:
    process_rng = random.Random(seed * 4001 + 11)
    obs_rng = random.Random(seed * 4001 + 13)
    policy_rng = random.Random(seed * 4001 + 17)
    state = State(5.3, 6.4, 6.0)
    rows=[]
    for tick in range(320):
        pre = observe(state, obs_rng)
        action = policy_rng.choice(ACTIONS)
        next_state = stochastic_step(state, action, tick, process_rng)
        post = observe(next_state, obs_rng)
        if all(pre[value_id] is not None for value_id in VALUES) and post[channel] is not None:
            raw_tokens = tuple(qtoken(float(pre[value_id]), RAW_STEP) for value_id in VALUES)
            effect_token = qtoken(float(post[channel]) - float(pre[channel]), EFFECT_STEP)
            rows.append(ProjectionSample(
                sample_id=f"R2-{channel}-{seed}-{tick}", raw_tokens=raw_tokens, action_token=action,
                effect_token=effect_token, operational_scope_id=f"R2-SEED-{seed}", frame_id="R2-FRAME", frame_epoch=0,
            ))
        state = next_state
    return rows


def main() -> None:
    training_seeds = range(200, 208)
    validation_seeds = range(208, 212)
    cfg = ProjectionDiscoveryConfig(max_subset=2, min_train_support=20, min_key_action_support=3,
                                    min_validation_accuracy=.72, min_lift_over_action_baseline=.08,
                                    min_scope_accuracy=.62, complexity_penalty=.008, max_candidates=12)
    channels={}
    for channel in VALUES:
        train=[row for seed in training_seeds for row in collect(seed,channel)]
        validation=[row for seed in validation_seeds for row in collect(seed,channel)]
        candidates=discover_epistemic_projection_candidates(train,validation,cfg)
        channels[channel]={
            "train_rows":len(train),"validation_rows":len(validation),
            "candidates":[{
                "candidate_id":c.candidate_id,"input_positions":list(c.input_positions),"bucket_count":c.bucket_count,
                "validation_accuracy":c.validation_accuracy,"action_baseline_accuracy":c.action_baseline_accuracy,
                "lift":c.lift,"min_scope_accuracy":c.min_scope_accuracy,"raw_key_count":c.raw_key_count,
                "assistance_ancestry":list(c.assistance_ancestry),
            } for c in candidates[:5]],
        }
    out={
        "schema":"microseed.ms1537.pass10.r2-projection-quarry.v1",
        "data_boundary":"NOISY_R2_PREACTION_SENSOR_TOKENS_PLUS_OBSERVED_POST_MINUS_PRE_EFFECT_TOKEN",
        "hidden_regime_labels_used":False,
        "raw_token_quantization_step":RAW_STEP,
        "effect_token_quantization_step":EFFECT_STEP,
        "projection_config":cfg.__dict__,
        "channels":channels,
        "disposition":"EXISTING_PROJECTION_DISCOVERY_HAS_R2_CONTEXT_SIGNAL" if all(channels[c]["candidates"] for c in VALUES) else "PROJECTION_SIGNAL_INCOMPLETE",
        "nonclaims":["NO_PROJECTION_ADMISSION","NO_ROUTING_QUALIFICATION","NO_MAINDEV_MUTATION","NO_SEMANTIC_REGIME_AUTHORITY"],
    }
    path=Path(__file__).with_name("MS1537_PASS10_R2_PROJECTION_QUARRY.json")
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
