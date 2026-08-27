from __future__ import annotations
import json
from pathlib import Path
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        r=m.action_outcome_learning.relations[rid]
        status=m.action_outcome_predictive_relation_status(rid)
        rehearsal=r.as_rehearsal_relation()
        out={'pass':'MS1635_PASS08','relation_status':status,'evidence_premise_epochs':[list(x) for x in r.evidence_premise_epochs],'rehearsal_conversion':None if rehearsal is None else rehearsal.serializable(),
             'result':'HISTORICAL_ADMISSION_VALIDITY_DOES_NOT_CURRENTLY_LAUNDER_INTO_REHEARSAL_OR_EXECUTION_AUTHORITY','scar':'HISTORICAL_VALIDITY != CURRENT_USE_LICENSE','note':'current relation object has predictive authority only; premise-bearing relation refuses rehearsal conversion','authority':'RESEARCH_ONLY','next':'ATTACK_RETROSPECTIVE_FALSIFICATION_SEMANTICS__STALE_VS_CHALLENGED_AND_HISTORY_PRESERVATION'}
        Path('research/MS1635_PASS08_NO_USE_LAUNDERING.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
