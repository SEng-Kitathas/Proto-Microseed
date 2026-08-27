from __future__ import annotations
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T='tests/embodiment/test_ms1643_historical_admission_ingress.py'
families=[
 ('TEMP_LIVE_ACCESS_LOSS_PRESERVES_HISTORY','test_temporary_live_channel_loss_does_not_stale_historical_relation'),
 ('PROSPECTIVE_MAPPING_CHANGE_PRESERVES_OLD_HISTORY','test_prospective_live_mapping_change_does_not_retroactively_stale_history'),
 ('RETROSPECTIVE_INVALIDATION_CREATES_NEW_EPOCH_DEBT','test_retrospective_basis_failure_must_advance_epoch_and_stays_stale_after_requalification'),
 ('RESTART_CONTENT_ALIAS_BLOCKED','test_same_id_epoch_but_changed_basis_content_stales_relation'),
 ('OLD_BASIS_NOT_APPLICABLE_TO_NEW_MAPPING','test_old_historical_basis_cannot_admit_new_evidence_after_mapping_content_change'),
 ('SAME_MAPPING_CONTENT_RUNTIME_EPOCH_ALLOWED','test_same_mapping_content_new_runtime_epoch_can_reuse_applicable_historical_basis'),
 ('CORRECT_BINDING_DOES_NOT_PROVE_TRUTH_OR_COMPLETENESS','test_snapshot_binding_does_not_turn_false_but_current_mapping_into_truth'),
]
results=[]
for family,test in families:
    cp=subprocess.run(['python','-m','pytest','-q',f'{T}::{test}'],cwd=ROOT,env={**os.environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=25)
    results.append({'family':family,'test':test,'pass':cp.returncode==0,'tail':'\n'.join((cp.stdout+cp.stderr).splitlines()[-4:])})
out={'pass':'MS1649_PASS22','families':results,'passed':sum(r['pass'] for r in results),'total':len(results),
     'result':'SEVEN_FAMILY_HISTORICAL_ADMISSION_SEMANTICS_CLEAN' if all(r['pass'] for r in results) else 'BREADTH_GAP',
     'surviving_model':{
       'historical_admission_identity':'basis id + basis epoch + immutable basis content signature',
       'new_acquisition_applicability':'historical basis snapshot must match current acquisition-premise content signature',
       'live_access':'separate and non-retroactive',
       'prospective_mapping_change':'old history preserved; old basis cannot admit new evidence under changed mapping',
       'retrospective_falsification':'old dependent relation stale/history preserved; new epoch and fresh evidence required',
       'restart':'same content may reincarnate; same id+epoch with changed content may not',
     },
     'pal169_boundary':'Content-bound/current/authorized admission still does not establish exhaustive physical truth; a correctly bound but false/incomplete basis remains possible.',
     'authority':'RESEARCH_ONLY','next':'PROMOTION_AND_AUTHORSHIP_AUDIT__LIKELY_RESEARCH_SURVIVOR_ONLY_BECAUSE_GROUNDING/COMPLETENESS_REMAIN_EXTERNAL'}
(ROOT/'research/MS1649_PASS22_SEMANTIC_BREADTH_RECONCILIATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if not all(r['pass'] for r in results): raise SystemExit(1)
