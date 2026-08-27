from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

def main():
    with tempfile.TemporaryDirectory(prefix='ms1608-') as td:
        m=Microseed(Path(td))
        causal=Hypothesis('CAUSAL_MEDIATION',lambda _: 'EFFECT_CHANGED+CONTROL_STABLE')
        exog=Hypothesis('EXOGENOUS_COVARIATION',lambda _: 'EFFECT_CHANGED+CONTROL_CHANGED')
        # Disturbance changes target consequence but lies outside the negative-control's sensitivity.
        r=m.active_discrimination([causal,exog],['P'],[('P','EFFECT_CHANGED+CONTROL_STABLE')])
    out={'pass':'MS1608_PASS06','hidden_fixture':'EXOGENOUS_DISTURBANCE_OUTSIDE_NEGATIVE_CONTROL_COVERAGE','organism_visible_result':r,
         'result':'NEGATIVE_CONTROL_FALSE_GREEN_WHEN_DISTURBANCE_LIES_OUTSIDE_TESTED_COVERAGE','scar':'NEGATIVE_CONTROL_STABILITY != UNIVERSAL_EXOGENOUS_ABSENCE','authority':'RESEARCH_ONLY'}
    Path('research/MS1608_PASS06_NEGATIVE_CONTROL_COVERAGE_HOSTILE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
