from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_9.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_8.json'

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.8':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 q=p.get('qualified_reentry_policy',{})
 exact={
  'historical_projection_authority':'NONE','historical_registration_is_current_authority':False,
  'provider_and_executable_evidence_overlap':'FORBIDDEN','ready_status':'READY_FOR_EXISTING_REGISTRATION_PATH',
  'ready_status_authority':'NONE','current_authority_owner':'EXISTING_OPERATIONAL_REGISTRIES_ONLY',
  'persistent_ready_state':'FORBIDDEN','new_reentry_registry':'NOT_INTEGRATED','new_reentry_manager':'NOT_INTEGRATED',
  'snapshot_operational_restore':'NOT_INTEGRATED','automatic_reentry_loop':'NOT_INTEGRATED','self_qualification':'NOT_INTEGRATED',
  'post_registration_currentness':'EXISTING_INVALIDATION_PATHS_ONLY',
  'effect_bound_epoch_fence':'CONDITIONAL_EXTERNAL_ASSURANCE_NOT_LOCAL_AUTHORITY',
  'indefinite_automatic_reentry':'NOT_WARRANTED','compactor_or_index':'NOT_INTEGRATED','authority_gain':'NONE',
 }
 for k,v in exact.items():
  if q.get(k)!=v:e.append('REENTRY:'+k)
 for k in ('content_coherence_required','lifecycle_tombstone_required','provider_compatibility_external','executable_challenge_external',
           'diagnostic_scope_bounds_reentry','dependency_currentness_rechecked_from_existing_registries','existing_registration_path_required','end_goal_bearing_test_required'):
  if q.get(k) is not True:e.append('REENTRY:'+k)
 if q.get('whole_organism_behavioral_criterion')!='RESTART_TO_REENTRY_TO_EXISTING_REHEARSAL_ACTION_EXTERNAL_OUTCOME_REDELIBERATION':e.append('END_GOAL')
 ci=p.get('current_integration',{})
 if ci.get('canonical_entity_version')!='v2.9' or ci.get('research_terminal_ms')!=1527 or ci.get('integration_terminal_ms')!=1527:e.append('TERMINAL')
 if ci.get('ms1503_started') is not True or ci.get('ms1528_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1527-POST-REENTRY-WHOLE-ORGANISM-HOSTILE-EMBODIMENT':e.append('FRONTIER')
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p)
 parent=subprocess.run([sys.executable,str(R/'validate_operating_profile_v28.py')],cwd=R.parent,text=True,capture_output=True)
 try: pd=json.loads(parent.stdout)
 except Exception: pd={}
 parent_ok=parent.returncode==0 and pd.get('combined_hostile_mutants_rejected')==90
 specs=[
  ('history_authority','qualified_reentry_policy.historical_registration_is_current_authority',True),
  ('projection_authority','qualified_reentry_policy.historical_projection_authority','DERIVED_READ_ONLY'),
  ('drop_content','qualified_reentry_policy.content_coherence_required',False),
  ('drop_lifecycle','qualified_reentry_policy.lifecycle_tombstone_required',False),
  ('selfqual','qualified_reentry_policy.self_qualification','INTEGRATED'),
  ('manager','qualified_reentry_policy.new_reentry_manager','INTEGRATED'),
  ('registry','qualified_reentry_policy.new_reentry_registry','INTEGRATED'),
  ('snapshot','qualified_reentry_policy.snapshot_operational_restore','INTEGRATED'),
  ('persist_ready','qualified_reentry_policy.persistent_ready_state','ALLOWED'),
  ('provider_internal','qualified_reentry_policy.provider_compatibility_external',False),
  ('challenge_internal','qualified_reentry_policy.executable_challenge_external',False),
  ('evidence_overlap','qualified_reentry_policy.provider_and_executable_evidence_overlap','ALLOWED'),
  ('scope_promote','qualified_reentry_policy.diagnostic_scope_bounds_reentry',False),
  ('trust_dep_claim','qualified_reentry_policy.dependency_currentness_rechecked_from_existing_registries',False),
  ('parallel_admission','qualified_reentry_policy.existing_registration_path_required',False),
  ('ready_authority','qualified_reentry_policy.ready_status_authority','EFFECT'),
  ('auto_loop','qualified_reentry_policy.automatic_reentry_loop','INTEGRATED'),
  ('indefinite','qualified_reentry_policy.indefinite_automatic_reentry','WARRANTED'),
  ('hidden_compactor','qualified_reentry_policy.compactor_or_index','INTEGRATED'),
  ('drop_end_goal','qualified_reentry_policy.end_goal_bearing_test_required',False),
  ('frontier','current_integration.selected_frontier','MORE_REENTRY_MANAGER_RESEARCH'),
 ]
 escaped=[]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val)
  if validate(x)[0]:escaped.append(n)
 out={'schema':'microseed.maindev-operating-profile-validation.v2.9','baseline_pass':ok,'baseline_errors':errs,
      'inherited_parent_hostile_mutants':90,'inherited_parent_hostile_mutants_rejected':90 if parent_ok else 0,
      'new_hostile_mutants':len(specs),'new_hostile_mutants_rejected':len(specs)-len(escaped),
      'combined_hostile_mutants':90+len(specs),'combined_hostile_mutants_rejected':(90 if parent_ok else 0)+len(specs)-len(escaped),
      'escaped':escaped,'all_pass':ok and parent_ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_9_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
