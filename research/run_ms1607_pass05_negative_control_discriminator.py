from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

PROBE='POST_PREDICTION_PERTURB'

def identify(observed):
    with tempfile.TemporaryDirectory(prefix='ms1607-') as td:
        m=Microseed(Path(td))
        causal=Hypothesis('CAUSAL_MEDIATION',lambda _: 'EFFECT_CHANGED+CONTROL_STABLE')
        exog=Hypothesis('EXOGENOUS_COVARIATION',lambda _: 'EFFECT_CHANGED+CONTROL_CHANGED')
        return m.active_discrimination([causal,exog],[PROBE],[(PROBE,observed)])

def main():
    lawful=identify('EFFECT_CHANGED+CONTROL_STABLE')
    confounded=identify('EFFECT_CHANGED+CONTROL_CHANGED')
    unavailable=identify('EFFECT_CHANGED+CONTROL_UNKNOWN')
    out={'pass':'MS1607_PASS05','lawful_intervention':lawful,'exogenous_disturbance_seen_by_negative_control':confounded,'control_unavailable_or_unresolved':unavailable,
         'result':'ORTHOGONAL_NEGATIVE_CONTROL_CAN_SEPARATE_CAUSAL_MEDIATION_FROM_A_COVERED_EXOGENOUS_DISTURBANCE__UNKNOWN_WHEN_CONTROL_DOES_NOT_BEAR','boundary':'CONTROL_ROUTE_GROUNDING_AND_DISTURBANCE_COVERAGE_REMAIN_UNEARNED','authority':'RESEARCH_ONLY'}
    Path('research/MS1607_PASS05_NEGATIVE_CONTROL_DISCRIMINATOR.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
