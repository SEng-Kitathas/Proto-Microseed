from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

Z95 = 1.96


def collect(seed: int, ticks: int = 100):
    process_rng=random.Random(seed*5003+11)
    obs_rng=random.Random(seed*5003+13)
    policy_rng=random.Random(seed*5003+17)
    state=State(5.3,6.4,6.0)
    out=[]
    for tick in range(ticks):
        pre_true=state
        pre_obs=observe(state,obs_rng)
        action=policy_rng.choice(ACTIONS)
        nxt=stochastic_step(state,action,tick,process_rng)
        post_obs=observe(nxt,obs_rng)
        for value_id, before_true, after_true in zip(VALUES,(pre_true.energy,pre_true.thermal,pre_true.integrity),(nxt.energy,nxt.thermal,nxt.integrity)):
            observed=None
            if pre_obs[value_id] is not None and post_obs[value_id] is not None:
                observed=float(post_obs[value_id])-float(pre_obs[value_id])
            out.append({
                'tick':tick,'action':action,'value_id':value_id,
                'true_effect':float(after_true-before_true),
                'observed_effect':observed,
            })
        state=nxt
    return out


def summarize(values:list[float]):
    if not values:return None
    mean=statistics.fmean(values)
    sd=statistics.stdev(values) if len(values)>1 else 0.0
    se=sd/math.sqrt(len(values)) if values else float('inf')
    n95=None
    if abs(mean)>1e-12 and sd>0:
        n95=(Z95*sd/abs(mean))**2
    return {'n':len(values),'mean':mean,'sd':sd,'se':se,'ci95_halfwidth':Z95*se,'ci95_low':mean-Z95*se,'ci95_high':mean+Z95*se,'approx_n_for_95pct_mean_sign':n95}


def main():
    pooled=defaultdict(lambda:{'true':[],'observed':[]})
    lifetime_counts=defaultdict(list)
    # 200 independent pre-drift lifetimes: enough for evaluator-side distribution characterization.
    for seed in range(100,300):
        rows=collect(seed,100)
        counts=defaultdict(int)
        for r in rows:
            key=(r['action'],r['value_id'])
            pooled[key]['true'].append(r['true_effect'])
            if r['observed_effect'] is not None:
                pooled[key]['observed'].append(r['observed_effect']);counts[key]+=1
        for key in [(a,v) for a in ACTIONS for v in VALUES]:
            lifetime_counts[key].append(counts[key])

    pairs={}
    for action in ACTIONS:
        for value_id in VALUES:
            key=(action,value_id)
            true=summarize(pooled[key]['true']);obs=summarize(pooled[key]['observed'])
            counts=lifetime_counts[key]
            expected=statistics.fmean(counts)
            pairs[f'{action}::{value_id}']={
                'true_effect_distribution_evaluator_only':true,
                'learner_visible_observed_effect_distribution':obs,
                'one_lifetime_observed_sample_count':{
                    'mean':expected,
                    'min':min(counts),'max':max(counts),
                    'median':statistics.median(counts),
                },
                'n95_to_one_lifetime_ratio':None if obs is None or obs['approx_n_for_95pct_mean_sign'] is None else obs['approx_n_for_95pct_mean_sign']/max(expected,1e-9),
            }

    out={
        'schema':'microseed.ms1548.pass21.r2-identifiability-audit.v1',
        'discriminator':'IS_THE_SINGLE_LIFETIME_R2_CONSEQUENCE_GAP_PARTLY_INFORMATION_LIMITED_UNDER_THE_CURRENT_SENSOR_NOISE_AND_ACTION_OPPORTUNITY_SURFACE',
        'boundary':'EVALUATOR_ONLY_FORENSIC_CHARACTERIZATION; HIDDEN_TRUE_EFFECTS_ARE_NEVER_ORGANISM_INPUT',
        'confidence_reference':'1.96-sigma normal approximation used descriptively only; not constitutional threshold',
        'lifetimes':200,
        'pre_drift_ticks_per_lifetime':100,
        'pairs':pairs,
        'nonclaims':['NO_INFORMATION_THEORETIC_LOWER_BOUND_PROOF','NO_GAUSSIANITY_AUTHORITY','NO_MAINDEV_MUTATION','NO_NEW_PRIMITIVE','NO_WHOLE_ORGANISM_CREDIT'],
    }
    p=Path(__file__).with_name('MS1548_PASS21_R2_IDENTIFIABILITY_AUDIT.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    compact={k:{
        'true_mean':round(v['true_effect_distribution_evaluator_only']['mean'],4),
        'obs_mean':round(v['learner_visible_observed_effect_distribution']['mean'],4),
        'obs_sd':round(v['learner_visible_observed_effect_distribution']['sd'],4),
        'one_life_n':round(v['one_lifetime_observed_sample_count']['mean'],2),
        'approx_n95_sign':None if v['learner_visible_observed_effect_distribution']['approx_n_for_95pct_mean_sign'] is None else round(v['learner_visible_observed_effect_distribution']['approx_n_for_95pct_mean_sign'],1),
        'ratio':None if v['n95_to_one_lifetime_ratio'] is None else round(v['n95_to_one_lifetime_ratio'],1),
    } for k,v in pairs.items()}
    print(json.dumps(compact,indent=2,sort_keys=True))
if __name__=='__main__':main()
