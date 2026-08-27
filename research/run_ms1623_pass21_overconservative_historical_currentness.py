from __future__ import annotations
import json,tempfile
from pathlib import Path
from tests.embodiment.test_ms1620_evidence_premise_currentness import established

def main():
    td,m,c,rid=established()
    try:
        before=m.action_outcome_predictive_relation_status(rid)
        stale=sorted(m.invalidate_capability('OBS',reason='TEMPORARY_LIVE_CHANNEL_ACCESS_LOSS'))
        after=m.action_outcome_predictive_relation_status(rid)
    finally:
        td.cleanup()
    out={
      'pass':'MS1623_PASS21','before':before,'stale_closure':stale,'after_temporary_channel_loss':after,
      'result':'CURRENT_RESEARCH_CARRIER_IS_SAFE_BUT_OVERCONSERVATIVE_WITH_MS1598_MONOLITHIC_BASIS__LIVE_ACCESS_LOSS_TRANSITIVELY_STALES_HISTORICAL_LEARNING',
      'scar':'LIVE_OBSERVATION_ACCESS_LOSS != HISTORICAL_ADMISSION_BASIS_FAILURE',
      'promotion':'DEFER', 'authority':'RESEARCH_ONLY'
    }
    Path('research/MS1623_PASS21_OVERCONSERVATIVE_HISTORICAL_CURRENTNESS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
