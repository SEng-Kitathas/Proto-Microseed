from __future__ import annotations
import json
from pathlib import Path
from microseed import Authority,QualificationState,QueryObligation
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        before={'relation':m.action_outcome_predictive_relation_status(rid)['status'],'obs_epoch':m.capabilities.epochs['OBS'],'live_epoch':m.capabilities.epochs['LIVE-BASIS'],'hist_epoch':m.capabilities.epochs['HIST-ADMIT']}
        m.capabilities.change_dependency('OBS',reason='PROSPECTIVE_MAPPING_CHANGE')
        # Repaired/new current mapping gets fresh OBS epoch. The current-use basis also pays a fresh epoch.
        obs=m.capabilities.contracts['OBS'];obs.qualification=QualificationState.SHADOW_QUALIFIED;obs.currentness='CURRENT'
        m.capabilities.change_dependency('LIVE-BASIS',reason='DEPENDENCY_MAPPING_EPOCH_CHANGED')
        live=m.capabilities.contracts['LIVE-BASIS'];live.qualification=QualificationState.SHADOW_QUALIFIED;live.currentness='CURRENT'
        after={'relation':m.action_outcome_predictive_relation_status(rid)['status'],'obs_epoch':m.capabilities.epochs['OBS'],'live_epoch':m.capabilities.epochs['LIVE-BASIS'],'hist_epoch':m.capabilities.epochs['HIST-ADMIT'],'future_live_use':m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id='F')['status']}
        out={'pass':'MS1633_PASS06','before':before,'after_new_mapping_live_epoch':after,'result':'PROSPECTIVE_MAPPING_CHANGE_CAN_ROTATE_LIVE_USE_EPOCH_WITHOUT_REWRITING_HISTORICAL_ADMISSION_EPOCH','scar':'NEW_LIVE_MAPPING_EPOCH != RETROSPECTIVE_INVALIDATION_OF_OLD_EVIDENCE','nonclaim':'compatibility/translation of old learned relation into new observation semantics remains separately gated; current rehearsal already refuses premise-bearing relations','authority':'RESEARCH_ONLY','next':'QUARRY_EXISTING_DEFICIT_LIFECYCLE_FOR_CURRENT_REUSE_UNDER_NEW_MAPPING_WITH_HISTORY_PRESERVED'}
        Path('research/MS1633_PASS06_PROSPECTIVE_MAPPING_EPOCH.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
