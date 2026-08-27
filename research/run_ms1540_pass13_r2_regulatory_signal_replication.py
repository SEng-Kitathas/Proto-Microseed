from __future__ import annotations
import json, statistics
from collections import Counter, defaultdict
from pathlib import Path
from microseed.development.projection_discovery import ProjectionDiscoveryConfig, discover_epistemic_projection_candidates
from research.run_ms1539_pass12_r2_regulatory_consequence_projection import VALUES, collect


def mode(c):
    return sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))[0][0] if c else None


def predict(candidate,row):
    bucket=candidate.project(row.raw_tokens)
    if bucket is None:return 'UNKNOWN'
    return dict(((b,a),e) for b,a,e in candidate.bucket_action_prediction).get((bucket,row.action_token),'UNKNOWN')


def acc(rows,pred):
    return sum(pred(r)==r.effect_token for r in rows)/max(len(rows),1)


def main():
    training=[r for seed in range(200,208) for ch in () for r in []] # marker only
    result={}
    moderate=ProjectionDiscoveryConfig(max_subset=2,min_train_support=20,min_key_action_support=3,min_validation_accuracy=.72,min_lift_over_action_baseline=.08,min_scope_accuracy=.62,complexity_penalty=.008,max_candidates=12)
    reveal=ProjectionDiscoveryConfig(max_subset=2,min_train_support=20,min_key_action_support=3,min_validation_accuracy=0,min_lift_over_action_baseline=-1,min_scope_accuracy=0,complexity_penalty=.008,max_candidates=12)
    for ch in VALUES:
        train=[r for seed in range(200,208) for r in collect(seed,ch)]
        initial_val=[r for seed in range(208,212) for r in collect(seed,ch)]
        admitted=discover_epistemic_projection_candidates(train,initial_val,moderate)
        revealed=discover_epistemic_projection_candidates(train,initial_val,reveal)
        candidate=(admitted or revealed)[0]
        # Independent baseline tables are trained only on nomination data.
        action_tab=defaultdict(Counter);state_tab=defaultdict(Counter)
        pos=candidate.input_positions[0] if len(candidate.input_positions)==1 else None
        for r in train:
            action_tab[r.action_token][r.effect_token]+=1
            if pos is not None:state_tab[r.raw_tokens[pos]][r.effect_token]+=1
        rows=[]
        for seed in range(212,232):
            hold=collect(seed,ch)
            cand=acc(hold,lambda r:predict(candidate,r))
            action=acc(hold,lambda r:mode(action_tab[r.action_token]))
            state=acc(hold,lambda r:mode(state_tab[r.raw_tokens[pos]]) if pos is not None else 'UNKNOWN')
            rows.append({'seed':seed,'rows':len(hold),'candidate_accuracy':cand,'action_only_accuracy':action,'state_only_accuracy':state,'lift_over_action':cand-action,'lift_over_state':cand-state})
        result[ch]={
            'candidate_source':'MODERATE_GATE' if admitted else 'REVEAL_ONLY_NOT_ADMITTED',
            'candidate_id':candidate.candidate_id,'input_positions':list(candidate.input_positions),
            'initial_validation_accuracy':candidate.validation_accuracy,
            'replication_seed_count':len(rows),
            'mean_candidate_accuracy':statistics.fmean(x['candidate_accuracy'] for x in rows),
            'mean_action_only_accuracy':statistics.fmean(x['action_only_accuracy'] for x in rows),
            'mean_state_only_accuracy':statistics.fmean(x['state_only_accuracy'] for x in rows),
            'mean_lift_over_action':statistics.fmean(x['lift_over_action'] for x in rows),
            'mean_lift_over_state':statistics.fmean(x['lift_over_state'] for x in rows),
            'positive_action_lift_seeds':sum(x['lift_over_action']>0 for x in rows),
            'positive_state_lift_seeds':sum(x['lift_over_state']>0 for x in rows),
            'rows':rows,
        }
    strong=[ch for ch,v in result.items() if v['mean_lift_over_action']>=.08 and v['mean_lift_over_state']>=.05 and v['positive_state_lift_seeds']>=15]
    out={'schema':'microseed.ms1540.pass13.r2-regulatory-signal-replication.v1','nomination_seeds':list(range(200,208)),'initial_validation_seeds':list(range(208,212)),'untouched_replication_seeds':list(range(212,232)),'channels':result,'replicated_strong_channels':strong,'disposition':'REGULATORY_ACTION_SIGNAL_REPLICATES' if len(strong)>=2 else 'REGULATORY_ACTION_SIGNAL_DOES_NOT_REPLICATE_STRONGLY','nonclaims':['NO_CANDIDATE_ADMISSION','NO_MAINDEV_MUTATION','NO_WHOLE_ORGANISM_CREDIT']}
    p=Path(__file__).with_name('MS1540_PASS13_R2_REGULATORY_SIGNAL_REPLICATION.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
