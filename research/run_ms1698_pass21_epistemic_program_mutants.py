from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'microseed/development/epistemic_program.py'
TEST='tests/embodiment/test_ms1682_epistemic_program_trial_research.py'
orig=MOD.read_text()
mutants={
 'DROP_CONTROL_STATE_CONTINUITY':("    if intent.start_state_id != expected_state or intent.control_state_evidence_id != expected_state_evidence:\n        return replace(trial,status='INVALID',invalid_reason='PROGRAM_CONTROL_STATE_CONTINUITY_VIOLATION')\n",''),
 'DROP_COMPONENT_CONTENT_SIGNATURE':("        if capabilities.epochs.get(cid)!=current_epochs[cid] or c.computed_signature_sha256()!=current_sigs[cid]:\n", "        if capabilities.epochs.get(cid)!=current_epochs[cid]:\n"),
 'DROP_FRAME_CURRENTNESS':("    for fid,epoch in trial.frame_epochs:\n        if current_frame_epochs.get(fid)!=epoch:\n            return replace(trial,status='INVALID',invalid_reason=f'PROGRAM_FRAME_DRIFT:{fid}')\n",''),
 'ALLOW_NON_EFFECT_COMPONENT':("        if c.authority!=Authority.EFFECT: return f'CAPABILITY_NOT_EFFECT_AUTHORIZED:{cid}'\n",''),
 'COMPLETE_AFTER_ONE_STEP':("    return replace(trial,step_records=records,status='COMPLETE' if len(records)==len(trial.steps) else 'OPEN')\n", "    return replace(trial,step_records=records,status='COMPLETE')\n"),
 'DROP_AUTHORITY_ESCALATION_GUARD':("        if any(x!='NONE' for x in (self.proposal_authority,self.qualification_authority,self.truth_authority,self.execution_authority,self.semantic_action_authority)):\n            raise ValueError('EPISTEMIC_PROGRAM_TRIAL_AUTHORITY_ESCALATION')\n",''),
}
results={}
try:
 for name,(old,new) in mutants.items():
  if old not in orig: raise RuntimeError(f'mutation anchor absent:{name}')
  MOD.write_text(orig.replace(old,new,1))
  p=subprocess.run([sys.executable,'-m','pytest','-q',TEST],cwd=ROOT,env={**__import__('os').environ,'PYTHONPATH':'.'},capture_output=True,text=True,timeout=20)
  results[name]={'rejected':p.returncode!=0,'returncode':p.returncode,'tail':'\n'.join((p.stdout+p.stderr).splitlines()[-8:])}
  MOD.write_text(orig)
finally:
 MOD.write_text(orig)
assert all(x['rejected'] for x in results.values()),results
out={'milestone':'MS1698','pass':21,'mutants':results,'rejected':sum(x['rejected'] for x in results.values()),'total':len(results),'disposition':'EPISTEMIC_PROGRAM_CARRIER_HOSTILE_MUTANTS_REJECTED'}
(ROOT/'research/MS1698_PASS21_EPISTEMIC_PROGRAM_MUTANTS.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
