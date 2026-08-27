from __future__ import annotations
import json,subprocess,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];MOD=ROOT/'microseed/development/epistemic_program.py';orig=MOD.read_text()
mutants=[
 ('DROP_CONTROL_STATE_CONTINUITY',"    if intent.start_state_id != expected_state or intent.control_state_evidence_id != expected_state_evidence:\n        return replace(trial,status='INVALID',invalid_reason='PROGRAM_CONTROL_STATE_CONTINUITY_VIOLATION')\n",'', 'test_wrong_start_state_evidence_invalidates_even_with_correct_action'),
 ('DROP_COMPONENT_CONTENT_SIGNATURE',"        if capabilities.epochs.get(cid)!=current_epochs[cid] or c.computed_signature_sha256()!=current_sigs[cid]:\n","        if capabilities.epochs.get(cid)!=current_epochs[cid]:\n",'test_capability_content_signature_drift_blocks_use_even_if_epoch_is_forged_unchanged'),
 ('DROP_FRAME_CURRENTNESS',"    for fid,epoch in trial.frame_epochs:\n        if current_frame_epochs.get(fid)!=epoch:\n            return replace(trial,status='INVALID',invalid_reason=f'PROGRAM_FRAME_DRIFT:{fid}')\n",'', 'test_frame_drift_between_steps_invalidates_trial'),
 ('ALLOW_NON_EFFECT_COMPONENT',"        if c.authority!=Authority.EFFECT: return f'CAPABILITY_NOT_EFFECT_AUTHORIZED:{cid}'\n",'', 'test_begin_rejects_non_effect_component'),
 ('COMPLETE_AFTER_ONE_STEP',"    return replace(trial,step_records=records,status='COMPLETE' if len(records)==len(trial.steps) else 'OPEN')\n","    return replace(trial,step_records=records,status='COMPLETE')\n",'test_two_different_step_proposals_bind_into_one_trial'),
 ('DROP_AUTHORITY_ESCALATION_GUARD',"        if any(x!='NONE' for x in (self.proposal_authority,self.qualification_authority,self.truth_authority,self.execution_authority,self.semantic_action_authority)):\n            raise ValueError('EPISTEMIC_PROGRAM_TRIAL_AUTHORITY_ESCALATION')\n",'', 'test_program_trial_object_rejects_truth_or_execution_authority_escalation'),
]
results={}
try:
 for name,old,new,test in mutants:
  if old not in orig: raise RuntimeError(f'anchor absent:{name}')
  MOD.write_text(orig.replace(old,new,1))
  node=f'tests/embodiment/test_ms1682_epistemic_program_trial_research.py::{test}'
  p=subprocess.run([sys.executable,'-m','pytest','-q',node],cwd=ROOT,env={**os.environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=8)
  results[name]={'rejected':p.returncode!=0,'returncode':p.returncode,'test':test,'tail':'\n'.join((p.stdout+p.stderr).splitlines()[-5:])}
  MOD.write_text(orig)
finally: MOD.write_text(orig)
assert all(v['rejected'] for v in results.values()),results
out={'milestone':'MS1698','pass':21,'mutants':results,'rejected':len(results),'total':len(results),'disposition':'EPISTEMIC_PROGRAM_CARRIER_HOSTILE_MUTANTS_REJECTED'}
(ROOT/'research/MS1698_PASS21_EPISTEMIC_PROGRAM_MUTANTS.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
