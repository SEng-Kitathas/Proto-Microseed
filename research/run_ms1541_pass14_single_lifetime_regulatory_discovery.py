from __future__ import annotations
import json, random, statistics
from pathlib import Path
from microseed.development.projection_discovery import ProjectionDiscoveryConfig, ProjectionSample, discover_epistemic_projection_candidates
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1539_pass12_r2_regulatory_consequence_projection import consequence_stance
from research.run_ms1537_pass10_r2_projection_quarry import VALUES, RAW_STEP, qtoken


def pre_drift_rows(seed:int,channel:str):
    process_rng=random.Random(seed*5003+11);obs_rng=random.Random(seed*5003+13);policy_rng=random.Random(seed*5003+17)
    s=State(5.3,6.4,6.0);rows=[]
    for tick in range(100):
        pre=observe(s,obs_rng);a=policy_rng.choice(ACTIONS);ns=stochastic_step(s,a,tick,process_rng);post=observe(ns,obs_rng)
        if all(pre[v] is not None for v in VALUES) and post[channel] is not None:
            raw=tuple(qtoken(float(pre[v]),RAW_STEP) for v in VALUES)
            rows.append(ProjectionSample(f'R2-SL-{channel}-{seed}-{tick}',raw,a,consequence_stance(channel,float(pre[channel]),float(post[channel])),f'R2-SINGLE-{seed}','R2-FRAME',0))
        s=ns
    return rows

def main():
    reveal=ProjectionDiscoveryConfig(max_subset=2,min_train_support=10,min_key_action_support=2,min_validation_accuracy=0,min_lift_over_action_baseline=-1,min_scope_accuracy=0,complexity_penalty=.008,max_candidates=12)
    moderate=ProjectionDiscoveryConfig(max_subset=2,min_train_support=10,min_key_action_support=2,min_validation_accuracy=.72,min_lift_over_action_baseline=.08,min_scope_accuracy=.62,complexity_penalty=.008,max_candidates=12)
    channels={}
    for ch in VALUES:
        seed_rows=[]
        for seed in range(100,112):
            rows=pre_drift_rows(seed,ch)
            cut=max(1,int(len(rows)*.70));train=rows[:cut];val=rows[cut:]
            admitted=discover_epistemic_projection_candidates(train,val,moderate)
            revealed=discover_epistemic_projection_candidates(train,val,reveal)
            best=(admitted or revealed)
            seed_rows.append({'seed':seed,'total_rows':len(rows),'train_rows':len(train),'validation_rows':len(val),'admitted_candidate':bool(admitted),'best':None if not best else {'positions':list(best[0].input_positions),'validation_accuracy':best[0].validation_accuracy,'action_baseline_accuracy':best[0].action_baseline_accuracy,'lift':best[0].lift,'min_scope_accuracy':best[0].min_scope_accuracy}})
        valid=[x for x in seed_rows if x['best']]
        channels[ch]={'seeds':seed_rows,'admitted_seed_count':sum(x['admitted_candidate'] for x in seed_rows),'seeds_with_any_revealed_candidate':len(valid),'mean_rows':statistics.fmean(x['total_rows'] for x in seed_rows),'mean_best_lift':statistics.fmean(x['best']['lift'] for x in valid) if valid else None,'mean_best_validation_accuracy':statistics.fmean(x['best']['validation_accuracy'] for x in valid) if valid else None}
    out={'schema':'microseed.ms1541.pass14.single-lifetime-regulatory-discovery.v1','data_boundary':'ONE_R2_LIFETIME_PRE_DRIFT_ONLY__RANDOM_ACTIONS__NO_HIDDEN_STATE','split':'FIRST_70_PERCENT_NOMINATION__LAST_30_PERCENT_VALIDATION','channels':channels,'disposition':'SINGLE_LIFETIME_DISCOVERY_SUFFICIENT' if all(channels[ch]['admitted_seed_count']>=6 for ch in VALUES) else 'SINGLE_LIFETIME_DISCOVERY_INSUFFICIENT','nonclaims':['NO_WHOLE_ORGANISM_CREDIT','NO_MAINDEV_MUTATION','NO_NEW_PRIMITIVE']}
    p=Path(__file__).with_name('MS1541_PASS14_SINGLE_LIFETIME_REGULATORY_DISCOVERY.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
