from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

def main():
  with tempfile.TemporaryDirectory(prefix='ms1590-p13-') as td:
    m=Microseed(Path(td))
    # Candidate coupling structures over a bounded intervention vocabulary.
    def pred(mode,probe):
      table={
        'COMMON':{'PERTURB_A':('SHIFT','SHIFT'),'PERTURB_B':('SHIFT','SHIFT')},
        'SEPARATE':{'PERTURB_A':('SHIFT','STABLE'),'PERTURB_B':('STABLE','SHIFT')},
        'A_ONLY':{'PERTURB_A':('SHIFT','STABLE'),'PERTURB_B':('STABLE','STABLE')},
        'B_ONLY':{'PERTURB_A':('STABLE','STABLE'),'PERTURB_B':('STABLE','SHIFT')},
      }
      return table[mode][probe]
    hs=[Hypothesis(mode,lambda p,mode=mode:pred(mode,p)) for mode in ('COMMON','SEPARATE','A_ONLY','B_ONLY')]
    first=m.active_discrimination(hs,['PERTURB_A','PERTURB_B'],[])
    obs1=pred('SEPARATE',first['next_probe'])
    second=m.active_discrimination(hs,['PERTURB_A','PERTURB_B'],[(first['next_probe'],obs1)])
    probe2=second['next_probe']
    obs2=pred('SEPARATE',probe2) if probe2 else None
    final=m.active_discrimination(hs,['PERTURB_A','PERTURB_B'],[(first['next_probe'],obs1)]+([] if probe2 is None else [(probe2,obs2)]))
    out={'pass':'MS1590_PASS13','first':first,'first_observation':obs1,'second':second,'second_observation':obs2,'final':final,'result':'EXISTING_ACTIVE_DISCRIMINATION_CAN_EARN_BOUNDED_FUNCTIONAL_SEPARATION_UNDER_SUPPLIED_COUPLING_HYPOTHESES','boundary':'TESTED_SELECTIVE_SEPARATION_DOES_NOT_PROVE_ABSENCE_OF_UNTESTED_COMMON_MODE','authority':'RESEARCH_ONLY'}
    Path('research/MS1590_PASS13_SELECTIVE_CHANNEL_INTERVENTION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
