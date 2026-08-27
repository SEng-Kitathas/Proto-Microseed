from __future__ import annotations

import json
import random
from pathlib import Path

from microseed.development.constructor_growth import ConstructorProjectionSample
from microseed.development.projection_discovery import (
    ProjectionDiscoveryConfig,
    ProjectionSample,
    discover_epistemic_projection_candidates,
)
from microseed.development.robust_constructor_growth import (
    RobustConstructorGrowthConfig,
    discover_robust_projection_constructor_candidates,
)
from microseed.development.value import pressure_magnitude_for_value
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import RAW_STEP, VALUES, qtoken


def consequence_stance(value_id: str, pre_value: float, post_value: float) -> str:
    """Reuse existing regulatory-pressure semantics; no hidden world state.

    This is the observed consequence relation needed by the current action-license
    question, not a new utility or priority scale.
    """
    contract = value_contract(value_id)
    current = pressure_magnitude_for_value(contract, pre_value)
    residual = pressure_magnitude_for_value(contract, post_value)
    if current > 0.0:
        if residual < current:
            return "YES"
        if residual > current:
            return "NO"
        return "UNKNOWN"
    return "YES" if residual == 0.0 else "NO"


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
            effect_token = consequence_stance(channel, float(pre[channel]), float(post[channel]))
            rows.append(ProjectionSample(
                sample_id=f"R2-RC-{channel}-{seed}-{tick}", raw_tokens=raw_tokens,
                action_token=action, effect_token=effect_token,
                operational_scope_id=f"R2-SEED-{seed}", frame_id="R2-FRAME", frame_epoch=0,
            ))
        state = next_state
    return rows


def constructor_rows(rows: list[ProjectionSample]) -> list[ConstructorProjectionSample]:
    return [ConstructorProjectionSample(
        sample_id=row.sample_id, raw_history=(tuple(row.raw_tokens),),
        action_token=row.action_token, effect_token=row.effect_token,
        operational_scope_id=row.operational_scope_id,
        frame_id=row.frame_id, frame_epoch=row.frame_epoch,
    ) for row in rows]


def projection_view(c):
    return {
        "candidate_id":c.candidate_id,"input_positions":list(c.input_positions),
        "validation_accuracy":c.validation_accuracy,"action_baseline_accuracy":c.action_baseline_accuracy,
        "lift":c.lift,"min_scope_accuracy":c.min_scope_accuracy,"bucket_count":c.bucket_count,
        "assistance_ancestry":list(c.assistance_ancestry),
    }


def robust_view(c):
    return {
        "candidate_id":c.candidate_id,"atoms":[a.token() for a in c.atoms],
        "pressure_accuracy":c.pressure_accuracy,"validation_accuracy":c.validation_accuracy,
        "action_baseline_accuracy":c.action_baseline_accuracy,"lift":c.lift,
        "min_scope_accuracy":c.min_scope_accuracy,"observed_conflict_coverage":c.observed_conflict_coverage,
        "assistance_ancestry":list(c.assistance_ancestry),
    }


def main() -> None:
    train_seeds=range(200,206)
    pressure_seeds=range(206,208)
    validation_seeds=range(208,212)

    # Same moderate prospective gates used in Pass 10. These are research gates,
    # not constitutional thresholds.
    proj_cfg=ProjectionDiscoveryConfig(
        max_subset=2,min_train_support=20,min_key_action_support=3,
        min_validation_accuracy=.72,min_lift_over_action_baseline=.08,
        min_scope_accuracy=.62,complexity_penalty=.008,max_candidates=12,
    )
    robust_cfg=RobustConstructorGrowthConfig(
        max_support_ceiling=3,max_lag_ceiling=0,top_supports_per_order=16,
        min_train_support=100,min_validation_accuracy=.72,
        min_lift_over_action_baseline=.08,min_scope_accuracy=.62,
        combination_budget=50000,max_candidates=8,
    )
    reveal_proj=ProjectionDiscoveryConfig(
        max_subset=2,min_train_support=20,min_key_action_support=3,
        min_validation_accuracy=0.0,min_lift_over_action_baseline=-1.0,
        min_scope_accuracy=0.0,complexity_penalty=.008,max_candidates=12,
    )

    channels={}
    for channel in VALUES:
        train=[r for seed in train_seeds for r in collect(seed,channel)]
        pressure=[r for seed in pressure_seeds for r in collect(seed,channel)]
        validation=[r for seed in validation_seeds for r in collect(seed,channel)]
        # Simple projection gets train+pressure as its nomination training set so the
        # held-out validation seeds remain untouched; robust keeps all three roles.
        simple=discover_epistemic_projection_candidates(train+pressure,validation,proj_cfg)
        revealed=discover_epistemic_projection_candidates(train+pressure,validation,reveal_proj)
        robust=discover_robust_projection_constructor_candidates(
            constructor_rows(train),constructor_rows(pressure),constructor_rows(validation),robust_cfg,
        )
        channels[channel]={
            "train_rows":len(train),"pressure_rows":len(pressure),"validation_rows":len(validation),
            "simple_candidates":[projection_view(c) for c in simple[:5]],
            "robust_candidates":[robust_view(c) for c in robust[:5]],
            "best_revealed_simple":[projection_view(c) for c in revealed[:3]],
        }

    qualified_channels=[ch for ch,v in channels.items() if v['simple_candidates'] or v['robust_candidates']]
    out={
        "schema":"microseed.ms1539.pass12.r2-regulatory-consequence-projection.v1",
        "data_boundary":"NOISY_R2_PREACTION_SENSOR_TOKENS_PLUS_OBSERVED_POSTACTION_VALUE__NO_HIDDEN_STATE",
        "target_relation":"EXISTING_REGULATORY_PRESSURE_CONSEQUENCE_STANCE__YES_LOWER_OR_PRESERVE__NO_WORSEN_OR_CREATE__UNKNOWN_EQUAL_PRESSURE",
        "hidden_regime_labels_used":False,
        "semantic_value_priority_added":False,
        "same_raw_tokenization_as_pass10":True,
        "simple_projection_config":proj_cfg.__dict__,
        "robust_constructor_config":robust_cfg.__dict__,
        "channels":channels,
        "channels_with_candidate_under_supplied_research_gates":qualified_channels,
        "disposition":(
            "DECISION_RELEVANT_REGULATORY_TARGET_RECOVERS_MATERIAL_OBSERVABLE_SIGNAL"
            if qualified_channels else "REGULATORY_TARGET_SIGNAL_INSUFFICIENT"
        ),
        "nonclaims":[
            "NO_PROJECTION_ADMISSION","NO_ROUTING_QUALIFICATION","NO_MAINDEV_MUTATION",
            "NO_WHOLE_ORGANISM_COMPETENCE_CREDIT","NO_SEMANTIC_REGIME_AUTHORITY",
            "NO_GENERAL_CLAIM_THAT_EXACT_EFFECT_MAGNITUDE_IS_USELESS",
        ],
    }
    path=Path(__file__).with_name('MS1539_PASS12_R2_REGULATORY_CONSEQUENCE_PROJECTION.json')
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
