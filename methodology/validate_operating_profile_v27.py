from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_7.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_6.json'

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.6':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 a=p.get('projection_conditioned_routing_policy',{})
 exact={
  'second_state_subsystem':'FORBIDDEN','selector_source':'EXISTING_EPISTEMIC_PROJECTION_RECORD',
  'selector_semantic_regime_authority':'NONE','routing_candidate_authority':'MODEL_OUTPUT_ONLY',
  'routing_candidate_truth_authority':'NONE','routing_candidate_qualification_authority':'NONE',
  'proposal_holdout_evidence_overlap':'FORBIDDEN','selected_relation_training_or_qualification_evidence_reuse':'FORBIDDEN',
  'unknown_or_scope_mismatch':'DEFER_UNKNOWN','automatic_state_split':'NOT_INTEGRATED',
  'automatic_model_switch':'NOT_INTEGRATED','semantic_regime_identity':'NOT_INTEGRATED','self_qualification':'NOT_INTEGRATED',
 }
 for k,v in exact.items():
  if a.get(k)!=v:e.append('ROUTING:'+k)
 for k in ('independent_external_qualification_required','shared_plus_delta_factorization','task_scope_required','action_scope_required','channel_scope_required','horizon_scope_required','projection_epoch_and_signature_currentness_required','structural_relation_currentness_required','global_empirical_stale_relation_may_be_scoped_requalified'):
  if a.get(k) is not True:e.append('ROUTING:'+k)
 for k in ('global_relation_reactivation_from_scoped_binding','merge_erases_historical_structure'):
  if a.get(k) is not False:e.append('ROUTING:'+k)
 ci=p.get('current_integration',{})
 if ci.get('canonical_entity_version')!='v2.7' or ci.get('research_terminal_ms')!=1477 or ci.get('integration_terminal_ms')!=1477:e.append('TERMINAL')
 if ci.get('ms1453_started') is not True or ci.get('ms1478_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1477-AUTONOMOUS-MULTI-CHILD-COMPOSITION__INTERACTION-AWARE-PARENT-PREDICTION-AND-REQUEST-SELECTION':e.append('FRONTIER')
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p)
 parent=subprocess.run([sys.executable,str(R/'validate_operating_profile_v26.py')],cwd=R.parent,text=True,capture_output=True)
 try: pd=json.loads(parent.stdout)
 except Exception: pd={}
 parent_ok=parent.returncode==0 and pd.get('combined_hostile_mutants_rejected')==65
 specs=[
  ('second_state','projection_conditioned_routing_policy.second_state_subsystem','ALLOWED'),
  ('semantic_regime','projection_conditioned_routing_policy.selector_semantic_regime_authority','REGIME'),
  ('candidate_truth','projection_conditioned_routing_policy.routing_candidate_truth_authority','TRUTH'),
  ('selfqual','projection_conditioned_routing_policy.self_qualification','INTEGRATED'),
  ('auto_split','projection_conditioned_routing_policy.automatic_state_split','INTEGRATED'),
  ('auto_switch','projection_conditioned_routing_policy.automatic_model_switch','INTEGRATED'),
  ('proposal_overlap','projection_conditioned_routing_policy.proposal_holdout_evidence_overlap','ALLOWED'),
  ('relation_overlap','projection_conditioned_routing_policy.selected_relation_training_or_qualification_evidence_reuse','ALLOWED'),
  ('global_reactivate','projection_conditioned_routing_policy.global_relation_reactivation_from_scoped_binding',True),
  ('scope_fallback','projection_conditioned_routing_policy.unknown_or_scope_mismatch','FALLBACK_GLOBAL'),
  ('history_erase','projection_conditioned_routing_policy.merge_erases_historical_structure',True),
  ('frontier','current_integration.selected_frontier','MORE_STATE_ABSTRACTION'),
 ]
 escaped=[]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val)
  if validate(x)[0]:escaped.append(n)
 out={'schema':'microseed.maindev-operating-profile-validation.v2.7','baseline_pass':ok,'baseline_errors':errs,'inherited_parent_hostile_mutants':65,'inherited_parent_hostile_mutants_rejected':65 if parent_ok else 0,'new_hostile_mutants':len(specs),'new_hostile_mutants_rejected':len(specs)-len(escaped),'combined_hostile_mutants':65+len(specs),'combined_hostile_mutants_rejected':(65 if parent_ok else 0)+len(specs)-len(escaped),'escaped':escaped,'all_pass':ok and parent_ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_7_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
