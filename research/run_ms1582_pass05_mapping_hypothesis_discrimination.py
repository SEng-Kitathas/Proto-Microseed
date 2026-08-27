from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

def main():
  with tempfile.TemporaryDirectory(prefix='ms1582-p5-') as td:
    m=Microseed(Path(td))
    probes=('PLUS','MINUS')
    h_id=Hypothesis('MAP-ID',lambda p:{'PLUS':'+','MINUS':'-'}[p])
    h_flip=Hypothesis('MAP-FLIP',lambda p:{'PLUS':'-','MINUS':'+'}[p])
    before=m.active_discrimination([h_id,h_flip],list(probes),[])
    chosen=before['next_probe']
    # Actual result is externally supplied to the generic discriminator; this pass tests downstream composition only.
    actual='+' if chosen=='PLUS' else '-'
    after=m.active_discrimination([h_id,h_flip],list(probes),[(chosen,actual)])
    same_prediction_h1=Hypothesis('COMMON-A',lambda p:'X')
    same_prediction_h2=Hypothesis('COMMON-B',lambda p:'X')
    nondisc=m.active_discrimination([same_prediction_h1,same_prediction_h2],['P'],[])
    out={
      'pass':'MS1582_PASS05',
      'before':before,'actual_probe_result_supplied_at_fixture_boundary':actual,'after':after,
      'zero_disagreement_case':nondisc,
      'result':'EXISTING_ACTIVE_DISCRIMINATION_CAN_TEST_BOUNDED_MAPPING_ALTERNATIVES__BUT_REQUIRES_GROUNDED_PROBE_RESULT_AND_PREEXISTING_HYPOTHESES',
      'authority':'RESEARCH_ONLY'
    }
    Path('research/MS1582_PASS05_MAPPING_HYPOTHESIS_DISCRIMINATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
