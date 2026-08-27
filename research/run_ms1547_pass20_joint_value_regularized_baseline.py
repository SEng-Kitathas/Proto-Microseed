from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES
from research.run_ms1545_pass18_ordered_affine_baselines import median_by_action, stance_from_effect


def rows(seed: int, channel: str) -> list[dict]:
    process_rng=random.Random(seed*5003+11)
    obs_rng=random.Random(seed*5003+13)
    policy_rng=random.Random(seed*5003+17)
    state=State(5.3,6.4,6.0)
    out=[]
    for tick in range(100):
        pre=observe(state,obs_rng)
        action=policy_rng.choice(ACTIONS)
        nxt=stochastic_step(state,action,tick,process_rng)
        post=observe(nxt,obs_rng)
        if all(pre[v] is not None for v in VALUES) and post[channel] is not None:
            current={v:float(pre[v]) for v in VALUES}
            effect=float(post[channel])-current[channel]
            out.append({'tick':tick,'action':action,'values':current,'effect':effect,'actual_stance':stance_from_effect(channel,current[channel],effect)})
        state=nxt
    return out


def scale_stats(train: list[dict]):
    means={v:statistics.fmean(r['values'][v] for r in train) for v in VALUES}
    scales={}
    for v in VALUES:
        var=statistics.fmean((r['values'][v]-means[v])**2 for r in train)
        scales[v]=math.sqrt(var) if var>1e-12 else 1.0
    return means,scales


def features(row:dict, mode:str, means:dict, scales:dict):
    xs=[(row['values'][v]-means[v])/scales[v] for v in VALUES]
    one=[1.0 if row['action']==a else 0.0 for a in ACTIONS]
    if mode=='STATE_ONLY': return xs
    if mode=='ACTION_PLUS_JOINT_STATE': return [*xs,*one]
    if mode=='ACTION_X_JOINT_STATE':
        interactions=[]
        for bit in one:
            interactions.extend(bit*x for x in xs)
        return [*one,*interactions]
    raise ValueError(mode)


class Fixed:
    def __init__(self,label):self.label=label
    def predict(self,X):return [self.label for _ in X]


def fit(train,mode):
    means,scales=scale_stats(train)
    ys=[r['actual_stance'] for r in train]
    if len(set(ys))==1:return Fixed(ys[0]),means,scales
    X=[features(r,mode,means,scales) for r in train]
    clf=LogisticRegression(C=1.0,max_iter=1000,solver='lbfgs')
    clf.fit(X,ys)
    return clf,means,scales


def evaluate(seed,ch):
    rs=rows(seed,ch);cut=max(1,int(len(rs)*.70));tr=rs[:cut];va=rs[cut:]
    medians=median_by_action([{'action':r['action'],'effect':r['effect']} for r in tr])
    modes=('STATE_ONLY','ACTION_PLUS_JOINT_STATE','ACTION_X_JOINT_STATE')
    models={m:fit(tr,m) for m in modes}
    actual=[];preds={'ACTION_MEDIAN':[],**{m:[] for m in modes}}
    for r in va:
        actual.append(r['actual_stance'])
        med=medians.get(r['action'])
        preds['ACTION_MEDIAN'].append(None if med is None else stance_from_effect(ch,r['values'][ch],med))
        for m in modes:
            clf,means,scales=models[m]
            preds[m].append(str(clf.predict([features(r,m,means,scales)])[0]))
    stats={}
    base_correct=sum(p==y for p,y in zip(preds['ACTION_MEDIAN'],actual))
    for name,ps in preds.items():
        known=[i for i,p in enumerate(ps) if p is not None]
        ys=[actual[i] for i in known];qs=[ps[i] for i in known]
        correct=sum(q==y for q,y in zip(qs,ys))
        stats[name]={
            'accuracy_all_rows':correct/max(len(actual),1),
            'balanced_accuracy_when_available':float(balanced_accuracy_score(ys,qs)) if ys else None,
            'lift_over_action_median':(correct-base_correct)/max(len(actual),1),
        }
    return {'seed':seed,'train_rows':len(tr),'validation_rows':len(va),'models':stats}


def main():
    channels={}
    for ch in VALUES:
        rs=[evaluate(seed,ch) for seed in range(100,112)]
        names=tuple(rs[0]['models'])
        channels[ch]={'seeds':rs,'summary':{name:{
            'mean_accuracy':statistics.fmean(r['models'][name]['accuracy_all_rows'] for r in rs),
            'mean_balanced_accuracy':statistics.fmean(r['models'][name]['balanced_accuracy_when_available'] for r in rs),
            'mean_lift_over_action_median':statistics.fmean(r['models'][name]['lift_over_action_median'] for r in rs),
            'positive_lift_seed_count':sum(r['models'][name]['lift_over_action_median']>0 for r in rs),
        } for name in names}}
    out={
        'schema':'microseed.ms1547.pass20.joint-value-regularized-baseline.v1',
        'discriminator':'CAN_SPARSE_JOINT_CURRENT_VALUE_STRUCTURE_PLUS_ACTION_CLOSE_SINGLE_LIFETIME_R2_REGULATORY_CONSEQUENCE_GAP_WITH_A_STANDARD_REGULARIZED_LINEAR_MODEL',
        'data_boundary':'ONE_R2_LIFETIME_PRE_DRIFT__ALL_THREE_NOISY_CURRENT_VALUE_OBSERVATIONS_PLUS_ACTION__ACTUAL_OBSERVED_TARGET_COORDINATE_CONSEQUENCE',
        'model':'fixed sklearn LogisticRegression(C=1.0, lbfgs); no tuning',
        'feature_sets':{
            'STATE_ONLY':'three standardized current value coordinates',
            'ACTION_PLUS_JOINT_STATE':'joint state + action one-hot with shared state coefficients',
            'ACTION_X_JOINT_STATE':'action one-hot + action-specific interactions with all three current values',
        },
        'channels':channels,
        'nonclaims':['NO_MAINDEV_MUTATION','NO_NEW_PRIMITIVE','NO_WHOLE_ORGANISM_CREDIT','NO_LINEAR_MODEL_ARCHITECTURE','NO_HYPERPARAMETER_SWEEP','NO_HIDDEN_STATE'],
    }
    p=Path(__file__).with_name('MS1547_PASS20_JOINT_VALUE_REGULARIZED_BASELINE.json');p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({c:channels[c]['summary'] for c in VALUES},indent=2,sort_keys=True))
if __name__=='__main__':main()
