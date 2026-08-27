from __future__ import annotations
import json, random, statistics
from pathlib import Path
from microseed.development.projection_discovery import ProjectionDiscoveryConfig, ProjectionSample, discover_epistemic_projection_candidates
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1539_pass12_r2_regulatory_consequence_projection import consequence_stance
from research.run_ms1537_pass10_r2_projection_quarry import VALUES
from microseed.development.value import pressure_magnitude_for_value


def regulatory_relation(value_id:str,value:float)->str:
    c=value_contract(value_id)
    if value < c.viable_low:return 'BELOW_VIABLE_INTERVAL'
    if value > c.viable_high:return 'ABOVE_VIABLE_INTERVAL'
    return 'WITHIN_VIABLE_INTERVAL'


def pre_drift_rows(seed:int,channel:str):
    process_rng=random.Random(seed*5003+11);obs_rng=random.Random(seed*5003+13);policy_rng=random.Random(seed*5003+17)
    s=State(5.3,6.4,6.0);rows=[]
    for tick in range(100):
        pre=observe(s,obs_rng);a=policy_rng.choice(ACTIONS);ns=stochastic_step(s,a,tick,process_rng);post=observe(ns,obs_rng)
        if all(pre[v] is not None for v in VALUES) and post[channel] is not None:
            raw=tuple(regulatory_relation(v,float(pre[v])) for v in VALUES)
            rows.append(ProjectionSample(f'R2-RR-{channel}-{seed}-{tick}',raw,a,consequence_stance(channel,float(pre[channel]),float(post[channel])),f'R2-SINGLE-{seed}','R2-FRAME',0))
        s=ns
    return rows


def main():
    moderate=ProjectionDiscoveryConfig(max_subset=2,min_train_support=10,min_key_action_support=2,min_validation_accuracy=.72,min_lift_over_action_baseline=.08,min_scope_accuracy=.62,complexity_penalty=.008,max_candidates=12)
    reveal=ProjectionDiscoveryConfig(max_subset=2,min_train_support=10,min_key_action_support=2,min_validation_accuracy=0,min_lift_over_action_baseline=-1,min_scope_accuracy=0,complexity_penalty=.008,max_candidates=12)
    channels={}
    for ch in VALUES:
        rows_out=[]
        for seed in range(100,112):
            rows=pre_drift_rows(seed,ch);cut=max(1,int(len(rows)*.70));tr=rows[:cut];va=rows[cut:]
            admitted=discover_epistemic_projection_candidates(tr,va,moderate);revealed=discover_epistemic_projection_candidates(tr,va,reveal);best=(admitted or revealed)
            rows_out.append({'seed':seed,'total_rows':len(rows),'train_rows':len(tr),'validation_rows':len(va),'admitted_candidate':bool(admitted),'best':None if not best else {'positions':list(best[0].input_positions),'validation_accuracy':best[0].validation_accuracy,'action_baseline_accuracy':best[0].action_baseline_accuracy,'lift':best[0].lift,'min_scope_accuracy':best[0].min_scope_accuracy,'bucket_count':best[0].bucket_count}})
        valid=[x for x in rows_out if x['best']]
        channels[ch]={'seeds':rows_out,'admitted_seed_count':sum(x['admitted_candidate'] for x in rows_out),'seeds_with_any_revealed_candidate':len(valid),'mean_rows':statistics.fmean(x['total_rows'] for x in rows_out),'mean_best_lift':statistics.fmean(x['best']['lift'] for x in valid) if valid else None,'mean_best_accuracy':statistics.fmean(x['best']['validation_accuracy'] for x in valid) if valid else None}
    out={'schema':'microseed.ms1542.pass15.single-lifetime-regulatory-relation-context.v1','context_tokens':'EXISTING_VALUE_PRESSURE_RELATION__BELOW_WITHIN_ABOVE','outcome_target':'EXISTING_REGULATORY_CONSEQUENCE_STANCE','data_boundary':'ONE_R2_LIFETIME_PRE_DRIFT__NO_HIDDEN_STATE','channels':channels,'disposition':'EXISTING_REGULATORY_RELATION_IMPROVES_SINGLE_LIFETIME_DISCOVERY' if any(channels[ch]['admitted_seed_count']>=4 for ch in VALUES) else 'REGULATORY_RELATION_CONTEXT_STILL_INSUFFICIENT','nonclaims':['NO_PROJECTION_ADMISSION','NO_MAINDEV_MUTATION','NO_WHOLE_ORGANISM_CREDIT']}
    p=Path(__file__).with_name('MS1542_PASS15_SINGLE_LIFETIME_REGULATORY_RELATION_CONTEXT.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
