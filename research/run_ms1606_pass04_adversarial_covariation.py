from __future__ import annotations
import json
from pathlib import Path

def main():
    worlds=64;wrong=0
    examples=[]
    for seed in range(worlds):
        # Physical perturbation genuinely mediates effect, but fixture supplies an exogenous
        # effect change whenever the *predicted* stream is perturbed and masks the physical
        # arm often enough to reverse the observed contrast. This is deliberate perfect-ish confounding.
        physical_rate=.25
        predicted_rate=.95
        selected='PERTURB_PREDICTED' if predicted_rate>physical_rate else 'PERTURB_PHYSICAL'
        wrong+=selected=='PERTURB_PREDICTED'
        if seed<3:examples.append({'physical_effect_change_rate':physical_rate,'predicted_effect_change_rate':predicted_rate,'selected':selected})
    out={'pass':'MS1606_PASS04','worlds':worlds,'wrong_role_selected':wrong,'examples':examples,
         'result':'PERFECT_OR_ADVERSARIAL_EXOGENOUS_COVARIATION_DEFEATS_REPEATED_INTERVENTIONAL_CONTRAST','scar':'INTERVENTIONAL_REPLICATION != UNIVERSAL_CAUSAL_IDENTIFIABILITY','boundary':'NO_OBSERVATIONAL_OR_INTERVENTIONAL_STATISTIC_CAN_BREAK_A_FIXTURE_THAT_PRESERVES_THE_SAME_VISIBLE_DISTRIBUTION_WITHOUT_AN_ORTHOGONAL_ASSUMPTION_OR_ROUTE','authority':'RESEARCH_ONLY'}
    Path('research/MS1606_PASS04_ADVERSARIAL_COVARIATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
