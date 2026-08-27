from __future__ import annotations
import json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,QualificationState,QueryObligation
from tests.embodiment.test_ms1643_historical_admission_ingress import install,call
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

def main():
    with tempfile.TemporaryDirectory(prefix='ms1644-') as td:
        m,_=seeded(Path(td));install(m)
        # One valid acquisition under original OBS/LIVE configuration.
        e0,_=prepare(m,'OLD');assert call(m,e0,'OLD')['status']=='ACTION_OUTCOME_OBSERVED'
        old_hist_sig=m.capabilities.contracts['HIST-ADMIT'].computed_signature_sha256()
        # Prospective observation mapping change; old historical basis remains historically valid for OLD evidence.
        m.change_capability_dependency('OBS',reason='NEW_OBSERVATION_MAPPING')
        obs=m.capabilities.contracts['OBS'];obs.purpose='NEW OBSERVATION MAPPING';obs.boundary={'mapping':'V2'};obs.qualification=QualificationState.SHADOW_QUALIFIED;obs.currentness='CURRENT'
        m.change_capability_dependency('LIVE-BASIS',reason='NEW_OBSERVATION_MAPPING')
        live=m.capabilities.contracts['LIVE-BASIS'];live.qualification=QualificationState.SHADOW_QUALIFIED;live.currentness='CURRENT'
        # Hostile: reuse the OLD historical-admission basis for a new acquisition under the changed mapping.
        e1,_=prepare(m,'NEW');r=call(m,e1,'NEW')
        ev=m.evidence.get('E-NEW')['payload'] if r.get('status')=='ACTION_OUTCOME_OBSERVED' else None
        out={'pass':'MS1644_PASS17','old_historical_basis_signature':old_hist_sig,'new_observation_epoch':m.capabilities.epochs['OBS'],'new_live_basis_epoch':m.capabilities.epochs['LIVE-BASIS'],'old_hist_basis_epoch':m.capabilities.epochs['HIST-ADMIT'],'new_acquisition_with_old_hist_basis':r,'new_evidence_premise':None if ev is None else {'epochs':ev.get('evidence_premise_epochs'),'signatures':ev.get('evidence_premise_signatures')},
             'result':'FALSE_GREEN__CURRENT_HISTORICAL_BASIS_CAN_BE_REUSED_FOR_NEW_ACQUISITION_AFTER_PROSPECTIVE_MAPPING_CHANGE' if r.get('status')=='ACTION_OUTCOME_OBSERVED' else 'OLD_BASIS_REUSE_BLOCKED','scar':'HISTORICAL_BASIS_VALID_FOR_OLD_EVIDENCE != HISTORICAL_BASIS_APPLICABLE_TO_NEW_ACQUISITION','next':'QUARRY_GENERIC_SNAPSHOT_BINDING_OF_ADMISSION_BASIS_TO_EXACT_ACQUISITION_PREMISES','authority':'RESEARCH_ONLY'}
        Path('research/MS1644_PASS17_OLD_ADMISSION_BASIS_REUSE_HOSTILE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
