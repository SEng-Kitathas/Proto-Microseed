from __future__ import annotations
import json
from pathlib import Path
from microseed import QualificationState
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        m.invalidate_capability('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_FALSIFIED')
        stale=m.action_outcome_predictive_relation_status(rid)
        # Hostile external boundary carelessly requalifies the same capability object without epoch advance.
        h=m.capabilities.contracts['HIST-ADMIT'];h.qualification=QualificationState.SHADOW_QUALIFIED;h.currentness='CURRENT'
        resurrected=m.action_outcome_predictive_relation_status(rid)
        out={'pass':'MS1637_PASS10','basis_epoch':m.capabilities.epochs['HIST-ADMIT'],'after_failure':stale,'after_same_epoch_requalification':resurrected,
             'result':'FALSE_GREEN__SAME_EPOCH_REQUALIFICATION_CAN_RESURRECT_BASIS_INVALIDATED_HISTORICAL_RELATION' if resurrected['status']=='CURRENT_PREDICTIVE_RELATION' else 'NO_RESURRECTION',
             'scar':'BASIS_FAILURE_REQUIRES_EPOCH_ADVANCE__STALE_FLAG_ALONE_DOES_NOT_ENFORCE_FRESH_DEBT','next':'TEST_EXISTING_CHANGE_CAPABILITY_DEPENDENCY_AS_GENERIC_EPOCH_ADVANCING_FAILURE_PATH_BEFORE_NEW_API','authority':'RESEARCH_ONLY'}
        Path('research/MS1637_PASS10_SAME_EPOCH_RESURRECTION_HOSTILE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':main()
