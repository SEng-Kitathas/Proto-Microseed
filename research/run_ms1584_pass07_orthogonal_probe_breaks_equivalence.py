from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Microseed
from microseed.cognition.hypothesis import Hypothesis

def main():
  with tempfile.TemporaryDirectory(prefix='ms1584-p7-') as td:
    m=Microseed(Path(td))
    # Same-stream observations cannot distinguish these. Orthogonal selective intervention can.
    h_actual=Hypothesis('STREAM-ACTUAL',lambda probe: 'SHIFT' if probe=='ORTHOGONAL_PHYSICAL_PERTURB' else 'SAME')
    h_feed=Hypothesis('STREAM-PREDICTION_FEED',lambda probe: 'UNCHANGED' if probe=='ORTHOGONAL_PHYSICAL_PERTURB' else 'SAME')
    before=m.active_discrimination([h_actual,h_feed],['SAME_STREAM_CHECK','ORTHOGONAL_PHYSICAL_PERTURB'],[])
    probe=before['next_probe']
    actual='SHIFT'  # supplied by fixture; its grounding is the next question, not assumed solved here.
    after=m.active_discrimination([h_actual,h_feed],['SAME_STREAM_CHECK','ORTHOGONAL_PHYSICAL_PERTURB'],[(probe,actual)])
    out={'pass':'MS1584_PASS07','before':before,'probe_result_fixture_boundary':actual,'after':after,'result':'ORTHOGONAL_CAUSAL_INTERVENTION_CAN_BREAK_SAME_STREAM_EQUIVALENCE__EXISTING_DISCRIMINATION_CONSUMES_IT','boundary':'PROBE_RESULT_GROUNDING_STILL_UNRESOLVED','authority':'RESEARCH_ONLY'}
    Path('research/MS1584_PASS07_ORTHOGONAL_PROBE_BREAKS_EQUIVALENCE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
