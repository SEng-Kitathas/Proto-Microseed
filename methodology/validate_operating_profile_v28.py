from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_8.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_7.json'

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.7':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 a=p.get('composition_ancestry_preservation_policy',{})
 exact={
  'core_relation_growth':0,'new_multi_child_planner':'NOT_INTEGRATED','new_multi_child_registry':'NOT_INTEGRATED',
  'semantic_child_role_authority':'NONE','composition_self_qualification':'NOT_INTEGRATED',
  'admission_reuses_existing_epoch_validation':'REQUIRED','authority_gain':'NONE',
 }
 for k,v in exact.items():
  if a.get(k)!=v:e.append('COMPOSITION:'+k)
 for k in ('trace_topology_must_be_current','trace_topology_must_bind_executed_step_relation','trace_counterparty_must_be_current','trace_coordination_must_be_current',
           'coordination_participant_counterparty_ancestry_inherited','recurrent_candidate_requires_uniform_topology_ancestry',
           'recurrent_candidate_requires_uniform_counterparty_ancestry','recurrent_candidate_requires_uniform_coordination_ancestry',
           'candidate_operational_signature_preserves_existing_epoch_families','post_ticket_epoch_drift_blocks_admission',
           'post_admission_bound_epoch_drift_selectively_stales_composite','individual_child_currentness_not_composition_currentness',
           'local_green_not_compositional_green','derived_composition_not_qualified_composition','pairwise_success_not_higher_order_completeness',
           'intended_joint_effect_not_learning_label'):
  if a.get(k) is not True:e.append('COMPOSITION:'+k)
 ci=p.get('current_integration',{})
 if ci.get('canonical_entity_version')!='v2.8' or ci.get('research_terminal_ms')!=1502 or ci.get('integration_terminal_ms')!=1502:e.append('TERMINAL')
 if ci.get('ms1478_started') is not True or ci.get('ms1503_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1502-RICH-ONLINE-HOSTILE-EMBODIMENT__PERSISTENT-WHOLE-ORGANISM-SCALE-UP':e.append('FRONTIER')
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p)
 parent=subprocess.run([sys.executable,str(R/'validate_operating_profile_v27.py')],cwd=R.parent,text=True,capture_output=True)
 try: pd=json.loads(parent.stdout)
 except Exception: pd={}
 parent_ok=parent.returncode==0 and pd.get('combined_hostile_mutants_rejected')==77
 specs=[
  ('planner','composition_ancestry_preservation_policy.new_multi_child_planner','INTEGRATED'),
  ('registry','composition_ancestry_preservation_policy.new_multi_child_registry','INTEGRATED'),
  ('semantic_role','composition_ancestry_preservation_policy.semantic_child_role_authority','SEMANTIC_ROLE'),
  ('selfqual','composition_ancestry_preservation_policy.composition_self_qualification','INTEGRATED'),
  ('topology_stale','composition_ancestry_preservation_policy.trace_topology_must_be_current',False),
  ('topology_irrelevant','composition_ancestry_preservation_policy.trace_topology_must_bind_executed_step_relation',False),
  ('counterparty_stale','composition_ancestry_preservation_policy.trace_counterparty_must_be_current',False),
  ('coordination_stale','composition_ancestry_preservation_policy.trace_coordination_must_be_current',False),
  ('drop_inherited_cp','composition_ancestry_preservation_policy.coordination_participant_counterparty_ancestry_inherited',False),
  ('drop_candidate_epochs','composition_ancestry_preservation_policy.candidate_operational_signature_preserves_existing_epoch_families',False),
  ('parallel_admission','composition_ancestry_preservation_policy.admission_reuses_existing_epoch_validation','NEW_PARALLEL_VALIDATOR'),
  ('authority_gain','composition_ancestry_preservation_policy.authority_gain','PARENT_COMMAND_AUTHORITY'),
  ('frontier','current_integration.selected_frontier','MORE_COMPOSITION_MICRO_HARNESS'),
 ]
 escaped=[]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val)
  if validate(x)[0]:escaped.append(n)
 out={'schema':'microseed.maindev-operating-profile-validation.v2.8','baseline_pass':ok,'baseline_errors':errs,
      'inherited_parent_hostile_mutants':77,'inherited_parent_hostile_mutants_rejected':77 if parent_ok else 0,
      'new_hostile_mutants':len(specs),'new_hostile_mutants_rejected':len(specs)-len(escaped),
      'combined_hostile_mutants':77+len(specs),'combined_hostile_mutants_rejected':(77 if parent_ok else 0)+len(specs)-len(escaped),
      'escaped':escaped,'all_pass':ok and parent_ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_8_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
