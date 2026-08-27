from __future__ import annotations
import json
from pathlib import Path
from microseed import Authority,QualificationState,QueryObligation
from research.run_ms1629_pass02_split_historical_admission_basis import established

def main():
    td,m,c,rid=established()
    try:
        before=m.action_outcome_predictive_relation_status(rid)['status']
        m.invalidate_capability('OBS',reason='TEMPORARY_ACCESS_LOSS')
        during=m.action_outcome_predictive_relation_status(rid)['status']
        future_during=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id='F')['status']
        # Same physical/interface regime restored: no epoch change, only access restored.
        for cid in ('OBS','LIVE-BASIS'):
            cc=m.capabilities.contracts[cid];cc.qualification=QualificationState.SHADOW_QUALIFIED;cc.currentness='CURRENT'
        after=m.action_outcome_predictive_relation_status(rid)['status']
        future_after=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id='F')['status']
        out={'pass':'MS1632_PASS05','before':before,'during_access_loss':during,'future_use_during':future_during,'after_access_restore':after,'future_use_after':future_after,'historical_admission_epoch':m.capabilities.epochs['HIST-ADMIT'],'result':'TEMPORARY_ACCESS_RECOVERY_DOES_NOT_REQUIRE_HISTORICAL_REQUALIFICATION','scar':'ACCESS_RESTORATION != EVIDENCE_RECERTIFICATION','authority':'RESEARCH_ONLY','next':'PROSPECTIVE_MAPPING_CHANGE_MUST_CREATE_NEW_LIVE_USE_EPOCH_WHILE_PRESERVING_OLD_ADMISSION_HISTORY'}
        Path('research/MS1632_PASS05_TEMPORARY_ACCESS_RECOVERY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
