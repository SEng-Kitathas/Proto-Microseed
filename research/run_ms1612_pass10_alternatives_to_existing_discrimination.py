from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

def main():
  with tempfile.TemporaryDirectory(prefix='ms1612-') as td:
    m=Microseed(Path(td))
    # Opaque handles, not causal truth labels. Their predictions are bounded by the supplied/tested control topology.
    h0=Hypothesis('REL-A',lambda p:'CONTROL-STABLE' if p=='NEG-CONTROL-CHECK' else 'SAME')
    h1=Hypothesis('REL-B',lambda p:'CONTROL-CHANGED' if p=='NEG-CONTROL-CHECK' else 'SAME')
    before=m.active_discrimination([h0,h1],['PASSIVE','NEG-CONTROL-CHECK'],[])
    after=m.active_discrimination([h0,h1],['PASSIVE','NEG-CONTROL-CHECK'],[(before['next_probe'],'CONTROL-CHANGED')])
    miss=m.active_discrimination([h0,h1],['NEG-CONTROL-CHECK'],[('NEG-CONTROL-CHECK','UNSEEN')])
  out={'pass':'MS1612_PASS10','before':before,'after_discriminating_evidence':after,'unexpected_result':miss,
       'result':'EXISTING_ACTIVE_DISCRIMINATION_CONSUMES_OPAQUE_RELATIONAL_ALTERNATIVES__UNEXPECTED_RESULT_IS_MODEL_SPACE_CHALLENGE_NOT_FORCED_CAUSE','authority':'RESEARCH_ONLY'}
  Path('research/MS1612_PASS10_ALTERNATIVES_TO_EXISTING_DISCRIMINATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
