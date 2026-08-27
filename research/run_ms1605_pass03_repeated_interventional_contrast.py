from __future__ import annotations
import json,random
from pathlib import Path

def run(seed:int,n:int=64,noise_p:float=.20):
    rng=random.Random(seed)
    rows=[]
    for i in range(n):
        probe='PERTURB_PHYSICAL' if i%2==0 else 'PERTURB_PREDICTED'
        caused=1 if probe=='PERTURB_PHYSICAL' else 0
        nuisance=1 if rng.random()<noise_p else 0
        # Binary change witness. Independent nuisance can create false positives on either arm.
        effect_changed=bool(caused or nuisance)
        rows.append((probe,effect_changed,nuisance))
    rates={p:sum(1 for q,e,_ in rows if q==p and e)/sum(1 for q,_,_ in rows if q==p) for p in ('PERTURB_PHYSICAL','PERTURB_PREDICTED')}
    return rates,rows

def main():
    worlds=[];correct=0
    for seed in range(160500,160564):
        rates,_=run(seed)
        selected=max(rates,key=rates.get)
        correct+=selected=='PERTURB_PHYSICAL'
        worlds.append({'seed':seed,'rates':rates,'selected':selected})
    out={'pass':'MS1605_PASS03','worlds':64,'fixed_trials_per_world':64,'independent_nuisance_probability':.20,'correct_role_by_repeated_contrast':correct,'examples':worlds[:5],
         'result':'REPEATED_BALANCED_INTERVENTIONAL_CONTRAST_CAN_IDENTIFY_MEDIATOR_UNDER_INDEPENDENT_NUISANCE','boundary':'INDEPENDENT_NUISANCE_IS_A_FIXTURE_ASSUMPTION_NOT_EARNED_WORLD_TRUTH','authority':'RESEARCH_ONLY'}
    Path('research/MS1605_PASS03_REPEATED_INTERVENTIONAL_CONTRAST.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
