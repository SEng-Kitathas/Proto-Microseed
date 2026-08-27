from __future__ import annotations
import json
from pathlib import Path
from microseed import QualificationState
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        changed=sorted(m.change_capability_dependency('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_BASIS_FAILED'))
        after=m.action_outcome_predictive_relation_status(rid)
        h=m.capabilities.contracts['HIST-ADMIT'];h.qualification=QualificationState.SHADOW_QUALIFIED;h.currentness='CURRENT'
        after_same_handle_requalified=m.action_outcome_predictive_relation_status(rid)
        out={'pass':'MS1638_PASS11','changed':changed,'basis_epoch':m.capabilities.epochs['HIST-ADMIT'],'after_epoch_advancing_failure':after,'after_requalifying_same_handle_new_epoch':after_same_handle_requalified,
             'result':'EXISTING_EPOCH_ADVANCING_CAPABILITY_CHANGE_PREVENTS_OLD_RELATION_RESURRECTION','scar':'BASIS_INVALIDATION_WITH_FRESH_DEBT_MUST_ADVANCE_EPOCH','nonclaim':'API name change_capability_dependency is generic/awkward but mechanism suffices; no new registry or state is justified','authority':'RESEARCH_ONLY','next':'ATTACK_OLD_CANDIDATE_REQUALIFICATION_UNDER_NEW_BASIS_EPOCH'}
        Path('research/MS1638_PASS11_EPOCH_ADVANCING_BASIS_FAILURE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':main()
