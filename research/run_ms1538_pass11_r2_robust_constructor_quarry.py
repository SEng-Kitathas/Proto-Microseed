from __future__ import annotations

import json
from pathlib import Path

from microseed.development.constructor_growth import ConstructorProjectionSample
from microseed.development.robust_constructor_growth import (
    RobustConstructorGrowthConfig,
    discover_robust_projection_constructor_candidates,
)
from research.run_ms1537_pass10_r2_projection_quarry import VALUES, collect

FRAME_ID = "R2-FRAME"
FRAME_EPOCH = 0


def convert(rows):
    out=[]
    for row in rows:
        out.append(ConstructorProjectionSample(
            sample_id=row.sample_id,
            raw_history=(tuple(row.raw_tokens),),
            action_token=row.action_token,
            effect_token=row.effect_token,
            operational_scope_id=row.operational_scope_id,
            frame_id=FRAME_ID,
            frame_epoch=FRAME_EPOCH,
        ))
    return out


def rows_for(channel, seeds):
    return convert([r for seed in seeds for r in collect(seed, channel)])


def candidate_view(c):
    return {
        "candidate_id": c.candidate_id,
        "atoms": [a.token() for a in c.atoms],
        "train_accuracy": c.train_accuracy,
        "pressure_accuracy": c.pressure_accuracy,
        "validation_accuracy": c.validation_accuracy,
        "action_baseline_accuracy": c.action_baseline_accuracy,
        "lift": c.lift,
        "min_scope_accuracy": c.min_scope_accuracy,
        "observed_conflict_coverage": c.observed_conflict_coverage,
        "evaluated_support_count": c.evaluated_support_count,
        "search_trace": [x.serializable() for x in c.search_trace],
        "assistance_ancestry": list(c.assistance_ancestry),
    }


def main():
    training_seeds=range(200,206)
    pressure_seeds=range(206,208)
    validation_seeds=range(208,212)

    native_cfg=RobustConstructorGrowthConfig(
        max_support_ceiling=3,
        max_lag_ceiling=0,
        top_supports_per_order=16,
        min_train_support=100,
        min_validation_accuracy=.90,
        min_lift_over_action_baseline=.25,
        min_scope_accuracy=.85,
        combination_budget=50000,
        max_candidates=8,
    )
    # Anti-confound only: reveal the best candidate the existing search can construct.
    # This does not change tokens, support ceiling, lag ceiling, or search grammar.
    reveal_cfg=RobustConstructorGrowthConfig(
        max_support_ceiling=3,
        max_lag_ceiling=0,
        top_supports_per_order=16,
        min_train_support=100,
        min_validation_accuracy=0.0,
        min_lift_over_action_baseline=-1.0,
        min_scope_accuracy=0.0,
        combination_budget=50000,
        max_candidates=8,
    )

    channels={}
    for channel in VALUES:
        train=rows_for(channel,training_seeds)
        pressure=rows_for(channel,pressure_seeds)
        validation=rows_for(channel,validation_seeds)
        native=discover_robust_projection_constructor_candidates(train,pressure,validation,native_cfg)
        reveal=discover_robust_projection_constructor_candidates(train,pressure,validation,reveal_cfg)
        channels[channel]={
            "train_rows":len(train),"pressure_rows":len(pressure),"validation_rows":len(validation),
            "native_candidates":[candidate_view(c) for c in native[:5]],
            "best_revealed_candidates":[candidate_view(c) for c in reveal[:5]],
        }

    best_lifts=[max([c["lift"] for c in channels[ch]["best_revealed_candidates"]],default=None) for ch in VALUES]
    material=all(x is not None and x>=.08 for x in best_lifts)
    out={
        "schema":"microseed.ms1538.pass11.r2-robust-constructor-quarry.v1",
        "data_boundary":"SAME_OBSERVED_ONLY_R2_DATA_AND_TOKENIZATION_AS_PASS10",
        "hidden_regime_labels_used":False,
        "training_seeds":list(training_seeds),"pressure_seeds":list(pressure_seeds),"validation_seeds":list(validation_seeds),
        "native_config":native_cfg.__dict__,
        "anti_confound_reveal_config":reveal_cfg.__dict__,
        "channels":channels,
        "material_lift_reference":.08,
        "disposition":"ROBUST_CONSTRUCTOR_MATERIAL_SIGNAL" if material else "ROBUST_CONSTRUCTOR_SIGNAL_INSUFFICIENT",
        "nonclaims":["NO_CANDIDATE_ADMISSION","NO_PROJECTION_AUTHORITY","NO_SEMANTIC_REGIME_IDENTITY","NO_MAINDEV_MUTATION"],
    }
    path=Path(__file__).with_name('MS1538_PASS11_R2_ROBUST_CONSTRUCTOR_QUARRY.json')
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
