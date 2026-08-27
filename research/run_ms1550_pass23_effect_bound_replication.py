from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path

from microseed.development.value import pressure_magnitude_for_value, residual_pressure_after_effect
from research.habitat_r2_exact import ACTIONS, State, observe, stochastic_step, deterministic_step
from research.run_ms1536_habitat_r2_whole_organism import value_contract
from research.run_ms1537_pass10_r2_projection_quarry import VALUES

Z=1.96; MIN_SUPPORT=3
REGIMES=((0,100),(100,200),(200,300))


def pv(s):
    return tuple(pressure_magnitude_for_value(value_contract(v),x) for v,x in zip(VALUES,(s.energy,s.thermal,s.integrity)))

def hidden_nonworsening(s,a,t):
    b=pv(s);n=pv(deterministic_step(s,a,t));return all(x<=y+1e-12 for x,y in zip(n,b)) and any(x<y-1e-12 for x,y in zip(n,b))

def estimate(xs):
    if len(xs)<MIN_SUPPORT:return None
    mean=sum(xs)/len(xs);sd=math.sqrt(sum((x-mean)**2 for x in xs)/(len(xs)-1)) if len(xs)>1 else 0.0;half=Z*sd/math.sqrt(len(xs))
    ys=sorted(xs);m=ys[len(ys)//2] if len(ys)%2 else .5*(ys[len(ys)//2-1]+ys[len(ys)//2])
    return {'mean':mean,'median':m,'low':mean-half,'high':mean+half,'n':len(xs)}

def interval_stance(v,current,e):
    c=value_contract(v);cur=pressure_magnitude_for_value(c,current)
    lo,hi=sorted((e['low'],e['high']));r1=residual_pressure_after_effect(c,current,lo);r2=residual_pressure_after_effect(c,current,hi);maxr=max(r1,r2)
    postlo=current+lo;posthi=current+hi;intersects=not(posthi<c.viable_low or postlo>c.viable_high);minr=0.0 if intersects else min(r1,r2)
    if cur>0:
        if maxr<cur:return 'YES'
        if minr>cur:return 'NO'
        return 'UNKNOWN'
    if maxr==0:return 'YES'
    if minr>0:return 'NO'
    return 'UNKNOWN'
def point_stance(v,current,e):
    c=value_contract(v);cur=pressure_magnitude_for_value(c,current);r=residual_pressure_after_effect(c,current,e['median'])
    if cur>0:return 'YES' if r<cur else ('NO' if r>cur else 'UNKNOWN')
    return 'YES' if r==0 else 'NO'

def license(pre,ests,mode):
    if any(pre[v] is None for v in VALUES):return []
    lic=[]
    for a in ACTIONS:
        ss=[]
        for v in VALUES:
            e=ests.get((a,v));ss.append('UNKNOWN' if e is None else (point_stance(v,float(pre[v]),e) if mode=='POINT' else interval_stance(v,float(pre[v]),e)))
        if all(s=='YES' for s in ss):lic.append(a)
    return lic

def evaluate(seed):
    pr=random.Random(seed*7001+11);orng=random.Random(seed*7001+13);pol=random.Random(seed*7001+17);state=State(5.3,6.4,6.0);timeline=[]
    for tick in range(300):
        true_pre=state;pre=observe(state,orng);a=pol.choice(ACTIONS);nxt=stochastic_step(state,a,tick,pr);post=observe(nxt,orng)
        timeline.append((tick,true_pre,pre,a,post));state=nxt
    regimes=[]
    for start,end in REGIMES:
        seg=timeline[start:end];train=seg[:70];val=seg[70:]
        grouped=defaultdict(list)
        for tick,s,pre,a,post in train:
            for v in VALUES:
                if pre[v] is not None and post[v] is not None:grouped[(a,v)].append(float(post[v])-float(pre[v]))
        ests={k:e for k,xs in grouped.items() if (e:=estimate(xs)) is not None}
        modes={m:{'decision':0,'unique':0,'safe':0,'harmful':0,'multiple':0,'none':0,'missing':0} for m in ('POINT','INTERVAL')}
        for tick,s,pre,a,post in val:
            for m in modes:
                if any(pre[v] is None for v in VALUES):modes[m]['missing']+=1;continue
                modes[m]['decision']+=1;lic=license(pre,ests,m)
                if len(lic)==1:
                    modes[m]['unique']+=1
                    if hidden_nonworsening(s,lic[0],tick):modes[m]['safe']+=1
                    else:modes[m]['harmful']+=1
                elif len(lic)>1:modes[m]['multiple']+=1
                else:modes[m]['none']+=1
        regimes.append({'regime':start//100,'tick_range':[start,end],'modes':modes})
    return {'seed':seed,'regimes':regimes}

def main():
    rows=[evaluate(s) for s in range(100,112)]
    summary={}
    for r in range(3):
        summary[str(r)]={}
        for m in ('POINT','INTERVAL'):
            total={k:sum(row['regimes'][r]['modes'][m][k] for row in rows) for k in rows[0]['regimes'][r]['modes'][m]}
            total['harmful_rate_when_unique']=total['harmful']/max(total['unique'],1);total['safe_rate_when_unique']=total['safe']/max(total['unique'],1)
            summary[str(r)][m]=total
    out={'schema':'microseed.ms1550.pass23.effect-bound-replication.v1','discriminator':'DO_QUERY_RELATIVE_EFFECT_BOUNDS_REDUCE_FALSE_GREEN_LICENSES_ACROSS_ALL_THREE_R2_REGIMES_WHEN_EVIDENCE_IS_REEARNED_WITHIN_EACH_REGIME','boundary':'EVALUATOR_SPLITS_REGIMES_ONLY_FOR_RESEARCH_REPLICATION; REGIME_IDENTITY_NOT_ORGANISM_INPUT','summary':summary,'seeds':rows,'nonclaims':['NO_DRIFT_DETECTION_CREDIT','NO_CONFIDENCE_INTERVAL_CONSTITUTION','NO_MAINDEV_MUTATION','NO_WHOLE_ORGANISM_CREDIT','NO_PAL_ARCHITECTURE_IMPORT']}
    p=Path(__file__).with_name('MS1550_PASS23_EFFECT_BOUND_REPLICATION.json');p.write_text(json.dumps(out,indent=2,sort_keys=True,default=lambda o:o.__dict__)+'\n');print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
