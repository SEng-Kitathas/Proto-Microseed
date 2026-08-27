from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_4.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_3.json'; BASE=json.loads(P.read_text())
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.3':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 b=p.get('bounded_control_loop_policy',{})
 exact={'action_commitment_semantics':'TRCH_PREMISE_LICENSING_NOT_EXECUTION_OR_TRUTH','open_loop_multistep_execution':'FORBIDDEN','control_state_observation_authority':'OBSERVATION_ONLY','effect_capability_authority_required':'EFFECT','effect_query_obligation_required_authority':'EFFECT','outcome_evidence_self_qualification':'FORBIDDEN','execution_authority_from_commitment':'NONE','truth_authority_from_commitment':'NONE','semantic_intention_authority':'NONE','general_policy':'NOT_INTEGRATED','general_planner':'NOT_INTEGRATED','continuous_controller':'NOT_INTEGRATED','endogenous_action_vocabulary':'NOT_INTEGRATED','endogenous_state_bucket_construction':'NOT_INTEGRATED'}
 for k,v in exact.items():
  if b.get(k)!=v:e.append('CONTROL:'+k)
 for k in ('binding_applicability_gates_preserved','one_action_per_deliberation','fresh_redeliberation_after_each_observed_outcome','stepwise_prediction_ancestry_required','current_opaque_control_state_witness_required','effect_capability_external_qualification_required','content_bound_external_outcome_observation_required','actual_outcome_updates_current_opaque_state','actual_outcome_updates_current_regulatory_value','prediction_match_is_commitment_not_truth','prediction_mismatch_forces_redeliberation','restart_preserves_history'):
  if b.get(k) is not True:e.append('CONTROL:'+k)
 if b.get('handler_result_is_observation') is not False:e.append('HANDLER_OBSERVATION')
 if b.get('restart_restores_execution_access') is not False:e.append('RESTART_ACCESS')
 if b.get('action_commitment_values')!=['YES','NO','UNKNOWN']:e.append('TERNARY_ACTION')
 for k in BASE.get('refinements_from_ms1378_1402',{}):
  if p.get('refinements_from_ms1378_1402',{}).get(k) is not True:e.append('DROP:'+k)
 # preserve v2.3 TRCH core
 t=p.get('relational_commitment_policy',{})
 if t.get('commitment_values')!=['YES','NO','UNKNOWN'] or t.get('binding_values')!=['YES','NO','UNKNOWN'] or t.get('applicability_values')!=['YES','NO','UNKNOWN']:e.append('TRCH_CORE')
 if t.get('commitment_semantics')!='QUERY_RELATIVE_PREMISE_LICENSING_NOT_WORLD_TRUTH':e.append('TRCH_SEMANTICS')
 ci=p.get('current_integration',{})
 if ci.get('research_terminal_ms')!=1402 or ci.get('integration_terminal_ms')!=1402:e.append('TERMINAL')
 if ci.get('ms1403_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1402-ACTION-OUTCOME-TO-PREDICTIVE-RELATION-UPDATE__WHOLE-SYSTEM-EXPERIENCE-LEARNING-CLOSURE':e.append('FRONTIER')
 if p.get('language_policy',{}).get('active_phase')!='PRELINGUAL':e.append('LANGUAGE')
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p);m=[]
 specs=[
 ('commit_truth','bounded_control_loop_policy.action_commitment_semantics','WORLD_TRUTH'),('open_loop','bounded_control_loop_policy.open_loop_multistep_execution','ALLOWED'),('handler_obs','bounded_control_loop_policy.handler_result_is_observation',True),('effect_from_commit','bounded_control_loop_policy.execution_authority_from_commitment','EFFECT'),('truth_from_commit','bounded_control_loop_policy.truth_authority_from_commitment','TRUTH'),('selfqual','bounded_control_loop_policy.outcome_evidence_self_qualification','ALLOWED'),('policy','bounded_control_loop_policy.general_policy','INTEGRATED'),('planner','bounded_control_loop_policy.general_planner','INTEGRATED'),('continuous','bounded_control_loop_policy.continuous_controller','INTEGRATED'),('semantic_intent','bounded_control_loop_policy.semantic_intention_authority','INTERNAL'),('endogenous_actions','bounded_control_loop_policy.endogenous_action_vocabulary','INTEGRATED'),('endogenous_state','bounded_control_loop_policy.endogenous_state_bucket_construction','INTEGRATED'),('wrong_obs_auth','bounded_control_loop_policy.control_state_observation_authority','MODEL_OUTPUT_ONLY'),('weak_effect','bounded_control_loop_policy.effect_capability_authority_required','DERIVED_READ_ONLY'),('weak_obligation','bounded_control_loop_policy.effect_query_obligation_required_authority','NONE'),('restart_access','bounded_control_loop_policy.restart_restores_execution_access',True),('terminal','current_integration.research_terminal_ms',1403),('start','current_integration.ms1403_started',True),('frontier','current_integration.selected_frontier','GENERAL_AUTONOMOUS_POLICY'),('language','language_policy.active_phase','LINGUISTIC')]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val);m.append((n,x))
 for k in ('binding_applicability_gates_preserved','one_action_per_deliberation','fresh_redeliberation_after_each_observed_outcome','stepwise_prediction_ancestry_required','current_opaque_control_state_witness_required','effect_capability_external_qualification_required','content_bound_external_outcome_observation_required','actual_outcome_updates_current_opaque_state','actual_outcome_updates_current_regulatory_value','prediction_match_is_commitment_not_truth','prediction_mismatch_forces_redeliberation','restart_preserves_history'):
  x=copy.deepcopy(p);x['bounded_control_loop_policy'][k]=False;m.append(('drop_'+k,x))
 for k in BASE['refinements_from_ms1378_1402']:
  x=copy.deepcopy(p);x['refinements_from_ms1378_1402'][k]=False;m.append(('drop_refinement_'+k,x))
 # TRCH regression mutants
 for path,val in [('relational_commitment_policy.commitment_values',['YES','NO']),('relational_commitment_policy.binding_values',['BOUND','NULL']),('relational_commitment_policy.applicability_values',['APPLICABLE','INAPPLICABLE']),('relational_commitment_policy.commitment_semantics','WORLD_TRUTH')]:
  x=copy.deepcopy(p);setpath(x,path,val);m.append(('trch_'+path.split('.')[-1],x))
 escaped=[n for n,x in m if validate(x)[0]]
 out={'schema':'microseed.maindev-operating-profile-validation.v2.4','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(m),'hostile_mutants_rejected':len(m)-len(escaped),'escaped':escaped,'all_pass':ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_4_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
