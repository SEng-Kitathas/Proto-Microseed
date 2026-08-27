from __future__ import annotations
import json, random, statistics
from pathlib import Path
from collections import defaultdict
from microseed.development.value import pressure_magnitude_for_value, residual_pressure_after_effect
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

TOLERANCE=0.5
MIN_SUPPORT=3


def stance_from_effect(value_id,current_value,effect):
    c=value_contract(value_id);cur=pressure_magnitude_for_value(c,current_value);res=residual_pressure_after_effect(c,current_value,effect)
    if cur>0:
        return 'YES' if res<cur else ('NO' if res>cur else 'UNKNOWN')
    return 'YES' if res==0 else 'NO'


def rows(seed:int,channel:str):
    pr=random.Random(seed*5003+11);orng=random.Random(seed*5003+13);pol=random.Random(seed*5003+17);s=State(5.3,6.4,6.0);out=[]
    for tick in range(100):
        pre=observe(s,orng);a=pol.choice(ACTIONS);ns=stochastic_step(s,a,tick,pr);post=observe(ns,orng)
        if pre[channel] is not None and post[channel] is not None:
            pv=float(pre[channel]);effect=float(post[channel])-pv
            out.append({'tick':tick,'action':a,'pre_value':pv,'effect':effect,'actual_stance':stance_from_effect(channel,pv,effect)})
        s=ns
    return out


def median(xs): return statistics.median(xs)

def evaluate(seed,ch):
    xs=rows(seed,ch);cut=max(1,int(len(xs)*.70));tr=xs[:cut];va=xs[cut:]
    by_action=defaultdict(list)
    for r in tr:by_action[r['action']].append(r)
    local_correct=global_correct=local_known=0
    details=[]
    for r in va:
        ar=by_action[r['action']]
        global_pred=None
        if len(ar)>=MIN_SUPPORT:
            global_pred=stance_from_effect(ch,r['pre_value'],median([x['effect'] for x in ar]))
        near=[x for x in ar if abs(x['pre_value']-r['pre_value'])<=TOLERANCE]
        local_pred=None
        if len(near)>=MIN_SUPPORT:
            local_pred=stance_from_effect(ch,r['pre_value'],median([x['effect'] for x in near]));local_known+=1
        global_correct += int(global_pred==r['actual_stance'])
        local_correct += int(local_pred==r['actual_stance'])
        details.append({'tick':r['tick'],'action':r['action'],'actual':r['actual_stance'],'global':global_pred,'local':local_pred,'local_support':len(near)})
    n=len(va)
    return {'seed':seed,'train_rows':len(tr),'validation_rows':n,'local_coverage':local_known/max(n,1),'local_accuracy_all_rows':local_correct/max(n,1),'global_accuracy_all_rows':global_correct/max(n,1),'local_accuracy_when_available':local_correct/max(local_known,1),'lift_over_global_all_rows':(local_correct-global_correct)/max(n,1),'details':details}

def main():
    channels={}
    for ch in VALUES:
        rs=[evaluate(seed,ch) for seed in range(100,112)]
        channels[ch]={'rows':rs,'mean_local_coverage':statistics.fmean(x['local_coverage'] for x in rs),'mean_local_accuracy_all_rows':statistics.fmean(x['local_accuracy_all_rows'] for x in rs),'mean_global_accuracy_all_rows':statistics.fmean(x['global_accuracy_all_rows'] for x in rs),'mean_local_accuracy_when_available':statistics.fmean(x['local_accuracy_when_available'] for x in rs),'mean_lift_over_global_all_rows':statistics.fmean(x['lift_over_global_all_rows'] for x in rs),'positive_lift_seed_count':sum(x['lift_over_global_all_rows']>0 for x in rs)}
    material=all(channels[ch]['mean_local_coverage']>=.5 and channels[ch]['mean_lift_over_global_all_rows']>=.05 for ch in VALUES)
    out={'schema':'microseed.ms1544.pass17.query-local-median-conditioning.v1','data_boundary':'ONE_R2_LIFETIME_PRE_DRIFT__OBSERVED_SCALAR_VALUE_AND_ACTUAL_EFFECT_ONLY','conditioning':'SAME_ACTION__ABS_PREVALUE_DISTANCE_LE_0_5__MEDIAN_EFFECT__MIN_SUPPORT_3','tolerance':TOLERANCE,'min_support':MIN_SUPPORT,'channels':channels,'disposition':'QUERY_LOCAL_EXISTING_CONDITIONING_MATERIALLY_IMPROVES_SINGLE_LIFETIME_PREDICTION' if material else 'QUERY_LOCAL_CONDITIONING_INSUFFICIENT','nonclaims':['NO_MAINDEV_MUTATION','NO_NEW_PRIMITIVE','NO_WHOLE_ORGANISM_CREDIT','NO_TOLERANCE_SWEEP']}
    p=Path(__file__).with_name('MS1544_PASS17_QUERY_LOCAL_MEDIAN_CONDITIONING.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
