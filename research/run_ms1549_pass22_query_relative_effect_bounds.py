from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

from microseed.development.value import pressure_magnitude_for_value, residual_pressure_after_effect
from research.habitat_r2_exact import ACTIONS, State, BANDS, observe, stochastic_step, deterministic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

Z = 1.96
MIN_SUPPORT = 3
TRAIN_TICKS = 70
TOTAL_TICKS = 100


def pressure_vector(state: State):
    return tuple(
        pressure_magnitude_for_value(value_contract(value_id), value)
        for value_id, value in zip(VALUES, (state.energy, state.thermal, state.integrity))
    )


def collect(seed:int):
    process_rng=random.Random(seed*5003+11);obs_rng=random.Random(seed*5003+13);policy_rng=random.Random(seed*5003+17)
    state=State(5.3,6.4,6.0);train=[];validation=[]
    for tick in range(TOTAL_TICKS):
        true_pre=state
        pre=observe(state,obs_rng);action=policy_rng.choice(ACTIONS);nxt=stochastic_step(state,action,tick,process_rng);post=observe(nxt,obs_rng)
        row={'tick':tick,'true_pre':true_pre,'pre':pre,'action':action,'post':post}
        (train if tick<TRAIN_TICKS else validation).append(row)
        state=nxt
    return train,validation


def effect_samples(train):
    grouped=defaultdict(list)
    for row in train:
        for v in VALUES:
            if row['pre'][v] is None or row['post'][v] is None: continue
            grouped[(row['action'],v)].append(float(row['post'][v])-float(row['pre'][v]))
    return grouped


def estimate(xs):
    if len(xs)<MIN_SUPPORT:return None
    mean=statistics.fmean(xs);sd=statistics.stdev(xs) if len(xs)>1 else 0.0;half=Z*sd/math.sqrt(len(xs))
    return {'n':len(xs),'mean':mean,'median':statistics.median(xs),'low':mean-half,'high':mean+half,'sd':sd}


def interval_residual_bounds(value_id,current,low_eff,high_eff):
    c=value_contract(value_id)
    lo=min(low_eff,high_eff);hi=max(low_eff,high_eff)
    end_lo=current+lo;end_hi=current+hi
    # residual pressure is convex and zero anywhere inside viable interval.
    r_lo=residual_pressure_after_effect(c,current,lo);r_hi=residual_pressure_after_effect(c,current,hi)
    max_r=max(r_lo,r_hi)
    intersects_safe=not (end_hi < c.viable_low or end_lo > c.viable_high)
    min_r=0.0 if intersects_safe else min(r_lo,r_hi)
    return min_r,max_r


def interval_stance(value_id,current,est):
    c=value_contract(value_id);cur=pressure_magnitude_for_value(c,current)
    min_r,max_r=interval_residual_bounds(value_id,current,est['low'],est['high'])
    if cur>0:
        if max_r < cur: return 'YES'
        if min_r > cur: return 'NO'
        return 'UNKNOWN'
    if max_r == 0: return 'YES'
    if min_r > 0: return 'NO'
    return 'UNKNOWN'


def point_stance(value_id,current,effect):
    c=value_contract(value_id);cur=pressure_magnitude_for_value(c,current);res=residual_pressure_after_effect(c,current,effect)
    if cur>0:
        return 'YES' if res<cur else ('NO' if res>cur else 'UNKNOWN')
    return 'YES' if res==0 else 'NO'


def license_for(pre,estimates,mode):
    per_action={}
    licensed=[]
    if any(pre[v] is None for v in VALUES):return [],per_action
    for action in ACTIONS:
        stances=[]
        for v in VALUES:
            est=estimates.get((action,v))
            if est is None: st='UNKNOWN'
            elif mode=='POINT_MEDIAN':st=point_stance(v,float(pre[v]),est['median'])
            else:st=interval_stance(v,float(pre[v]),est)
            stances.append(st)
        per_action[action]=stances
        if all(s=='YES' for s in stances):licensed.append(action)
    return licensed,per_action


def hidden_nonworsening(true_state,action,tick):
    before=pressure_vector(true_state);after=pressure_vector(deterministic_step(true_state,action,tick))
    return all(a<=b+1e-12 for a,b in zip(after,before)) and any(a<b-1e-12 for a,b in zip(after,before))


def evaluate(seed):
    train,val=collect(seed);grouped=effect_samples(train);ests={k:estimate(v) for k,v in grouped.items()};ests={k:v for k,v in ests.items() if v is not None}
    modes=('POINT_MEDIAN','QUERY_RELATIVE_INTERVAL')
    stat={m:{'decision_ticks':0,'unique_license_ticks':0,'hidden_nonworsening_unique':0,'hidden_worsening_unique':0,'multiple_license_ticks':0,'no_license_ticks':0,'missing_sensor_ticks':0} for m in modes}
    detail=[]
    for row in val:
        for mode in modes:
            if any(row['pre'][v] is None for v in VALUES):
                stat[mode]['missing_sensor_ticks']+=1;continue
            stat[mode]['decision_ticks']+=1
            lic,per=license_for(row['pre'],ests,mode)
            if len(lic)==1:
                stat[mode]['unique_license_ticks']+=1
                if hidden_nonworsening(row['true_pre'],lic[0],row['tick']):stat[mode]['hidden_nonworsening_unique']+=1
                else:stat[mode]['hidden_worsening_unique']+=1
            elif len(lic)>1:stat[mode]['multiple_license_ticks']+=1
            else:stat[mode]['no_license_ticks']+=1
        detail.append({'tick':row['tick']})
    return {'seed':seed,'estimate_support':{f'{a}::{v}':ests.get((a,v)) for a in ACTIONS for v in VALUES},'modes':stat}


def main():
    seeds=[evaluate(s) for s in range(100,112)]
    summary={}
    for mode in ('POINT_MEDIAN','QUERY_RELATIVE_INTERVAL'):
        totals={k:sum(s['modes'][mode][k] for s in seeds) for k in seeds[0]['modes'][mode]}
        summary[mode]=totals
        summary[mode]['hidden_worsening_rate_when_unique']=totals['hidden_worsening_unique']/max(totals['unique_license_ticks'],1)
        summary[mode]['hidden_nonworsening_rate_when_unique']=totals['hidden_nonworsening_unique']/max(totals['unique_license_ticks'],1)
    out={
        'schema':'microseed.ms1549.pass22.query-relative-effect-bounds.v1',
        'discriminator':'CAN_BOUNDED_EFFECT_UNCERTAINTY_PLUS_EXISTING_VALUE_INTERVALS_SUPPORT_QUERY_RELATIVE_SAFE_USE_WITHOUT_PRETENDING_TINY_EFFECT_SIGNS_ARE_KNOWN',
        'data_boundary':'ONE_R2_PRE_DRIFT_LIFETIME__FIRST_70_TICKS_EFFECT_EVIDENCE__LAST_30_TICKS_DECISION_OPPORTUNITIES__OBSERVED_VALUES_ONLY_FOR_LICENSE; TRUE_STATE_EVALUATOR_ONLY',
        'interval':'mean +/- 1.96 * sample_sd/sqrt(n), descriptive research comparator only',
        'min_support':MIN_SUPPORT,
        'summary':summary,'seeds':seeds,
        'nonclaims':['NO_CONFIDENCE_INTERVAL_CONSTITUTION','NO_GAUSSIANITY_AUTHORITY','NO_MAINDEV_MUTATION','NO_PAL_IMPORT','NO_WHOLE_ORGANISM_CREDIT','NO_NEW_PRIMITIVE_EARNED'],
    }
    p=Path(__file__).with_name('MS1549_PASS22_QUERY_RELATIVE_EFFECT_BOUNDS.json');p.write_text(json.dumps(out,indent=2,sort_keys=True,default=lambda o:o.__dict__)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
