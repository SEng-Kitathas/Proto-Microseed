from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_5.json'
PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_4.json'

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.4':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 a=p.get('action_outcome_predictive_learning_policy',{})
 exact={
  'training_source':'EXECUTED_ACTION_PLUS_CONTENT_BOUND_EXTERNAL_ACTUAL_OUTCOME',
  'intended_or_predicted_outcome_role':'PROVENANCE_ONLY_NOT_LEARNING_LABEL',
  'candidate_authority':'MODEL_OUTPUT_ONLY','candidate_truth_authority':'NONE','candidate_causal_theorem_authority':'NONE','candidate_qualification_authority':'NONE',
  'proposal_qualification_evidence_overlap':'FORBIDDEN','qualified_relation_authority':'EVIDENCE_BOUND_PREDICTIVE_RELATION_ONLY',
  'qualified_relation_truth_authority':'NONE','qualified_relation_causal_theorem_authority':'NONE','qualified_relation_execution_authority':'NONE','qualified_relation_semantic_goal_authority':'NONE',
  'automatic_model_rewrite':'NOT_INTEGRATED','automatic_model_switch':'NOT_INTEGRATED','general_causal_learner':'NOT_INTEGRATED','general_world_model_learner':'NOT_INTEGRATED','semantic_goal_learning':'NOT_INTEGRATED','self_qualification':'NOT_INTEGRATED','intention_as_learning_label':'FORBIDDEN',
 }
 for k,v in exact.items():
  if a.get(k)!=v:e.append('LEARNING:'+k)
 for k in ('failed_intention_can_be_successful_learning_event','actual_outcome_only','passive_cooccurrence_not_action_law','one_outcome_not_law','minimum_support_supplied','minimum_consistency_supplied','hidden_mixture_abstains_without_observable_partition','independent_external_qualification_required','qualification_holdout_content_bound','currentness_recheck_required','historical_relation_preserved_across_drift','qualified_relation_may_feed_bounded_rehearsal','prediction_error_is_model_pressure_not_model_authority'):
  if a.get(k) is not True:e.append('LEARNING:'+k)
 if a.get('proposal_only_candidate_may_feed_rehearsal') is not False:e.append('PROPOSAL_REHEARSAL')
 if a.get('currentness_ancestry')!=['CAPABILITY','FRAME','EPISODE','VALUE','TOPOLOGY','COORDINATION']:e.append('CURRENTNESS_ANCESTRY')
 # preserve v2.4 authority/control-loop boundary
 b=p.get('bounded_control_loop_policy',{})
 for k,v in {
  'action_commitment_semantics':'TRCH_PREMISE_LICENSING_NOT_EXECUTION_OR_TRUTH','open_loop_multistep_execution':'FORBIDDEN',
  'execution_authority_from_commitment':'NONE','truth_authority_from_commitment':'NONE','outcome_evidence_self_qualification':'FORBIDDEN',
  'general_policy':'NOT_INTEGRATED','general_planner':'NOT_INTEGRATED','semantic_intention_authority':'NONE','control_state_observation_authority':'OBSERVATION_ONLY',
 }.items():
  if b.get(k)!=v:e.append('CONTROL:'+k)
 if b.get('handler_result_is_observation') is not False:e.append('HANDLER_OBSERVATION')
 if b.get('content_bound_external_outcome_observation_required') is not True:e.append('EXTERNAL_OUTCOME')
 if b.get('restart_restores_execution_access') is not False:e.append('RESTART_ACCESS')
 t=p.get('relational_commitment_policy',{})
 if t.get('commitment_values')!=['YES','NO','UNKNOWN'] or t.get('commitment_semantics')!='QUERY_RELATIVE_PREMISE_LICENSING_NOT_WORLD_TRUTH':e.append('TRCH')
 ai=p.get('architectural_interrupt_policy',{})
 if ai.get('authority_as_truth')!='FORBIDDEN' or ai.get('recency_as_truth')!='FORBIDDEN' or ai.get('premise_support_loss_implies_null')!='FORBIDDEN':e.append('TRCH_AUTHORITY')
 ci=p.get('current_integration',{})
 if ci.get('canonical_entity_version')!='v2.5':e.append('VERSION')
 if ci.get('research_terminal_ms')!=1427 or ci.get('integration_terminal_ms')!=1427:e.append('TERMINAL')
 if ci.get('ms1403_started') is not True or ci.get('ms1428_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1427-LEARNED-PREDICTIVE-LAW-DRIFT-AND-RELEARNING__WHOLE-SYSTEM-ADAPTIVE-DEVELOPMENTAL-CLOSURE':e.append('FRONTIER')
 if p.get('language_policy',{}).get('active_phase')!='PRELINGUAL':e.append('LANGUAGE')
 for k,v in p.get('refinements_from_ms1403_1427',{}).items():
  if v is not True:e.append('DROP:'+k)
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p);m=[]
 specs=[
  ('intent_label','action_outcome_predictive_learning_policy.intended_or_predicted_outcome_role','LEARNING_LABEL'),
  ('training_model','action_outcome_predictive_learning_policy.training_source','PREDICTED_OUTCOME'),
  ('candidate_truth','action_outcome_predictive_learning_policy.candidate_truth_authority','TRUTH'),
  ('candidate_causal','action_outcome_predictive_learning_policy.candidate_causal_theorem_authority','THEOREM'),
  ('candidate_qual','action_outcome_predictive_learning_policy.candidate_qualification_authority','SELF'),
  ('candidate_effect','action_outcome_predictive_learning_policy.candidate_authority','EFFECT'),
  ('overlap','action_outcome_predictive_learning_policy.proposal_qualification_evidence_overlap','ALLOWED'),
  ('rel_truth','action_outcome_predictive_learning_policy.qualified_relation_truth_authority','TRUTH'),
  ('rel_causal','action_outcome_predictive_learning_policy.qualified_relation_causal_theorem_authority','THEOREM'),
  ('rel_effect','action_outcome_predictive_learning_policy.qualified_relation_execution_authority','EFFECT'),
  ('rel_goal','action_outcome_predictive_learning_policy.qualified_relation_semantic_goal_authority','INTERNAL'),
  ('rewrite','action_outcome_predictive_learning_policy.automatic_model_rewrite','INTEGRATED'),
  ('switch','action_outcome_predictive_learning_policy.automatic_model_switch','INTEGRATED'),
  ('causal_learner','action_outcome_predictive_learning_policy.general_causal_learner','INTEGRATED'),
  ('world_model','action_outcome_predictive_learning_policy.general_world_model_learner','INTEGRATED'),
  ('semantic_goal','action_outcome_predictive_learning_policy.semantic_goal_learning','INTEGRATED'),
  ('selfqual','action_outcome_predictive_learning_policy.self_qualification','INTEGRATED'),
  ('intention_label_gate','action_outcome_predictive_learning_policy.intention_as_learning_label','ALLOWED'),
  ('proposal_into_rehearsal','action_outcome_predictive_learning_policy.proposal_only_candidate_may_feed_rehearsal',True),
  ('commit_truth','bounded_control_loop_policy.action_commitment_semantics','WORLD_TRUTH'),
  ('commit_effect','bounded_control_loop_policy.execution_authority_from_commitment','EFFECT'),
  ('truth_from_commit','bounded_control_loop_policy.truth_authority_from_commitment','TRUTH'),
  ('open_loop','bounded_control_loop_policy.open_loop_multistep_execution','ALLOWED'),
  ('handler_obs','bounded_control_loop_policy.handler_result_is_observation',True),
  ('outcome_selfqual','bounded_control_loop_policy.outcome_evidence_self_qualification','ALLOWED'),
  ('policy','bounded_control_loop_policy.general_policy','INTEGRATED'),
  ('planner','bounded_control_loop_policy.general_planner','INTEGRATED'),
  ('semantic_intent','bounded_control_loop_policy.semantic_intention_authority','INTERNAL'),
  ('obs_auth','bounded_control_loop_policy.control_state_observation_authority','MODEL_OUTPUT_ONLY'),
  ('restart_access','bounded_control_loop_policy.restart_restores_execution_access',True),
  ('trch_binary','relational_commitment_policy.commitment_values',['YES','NO']),
  ('trch_truth','relational_commitment_policy.commitment_semantics','WORLD_TRUTH'),
  ('authority_truth','architectural_interrupt_policy.authority_as_truth','ALLOWED'),
  ('recency_truth','architectural_interrupt_policy.recency_as_truth','ALLOWED'),
  ('support_null','architectural_interrupt_policy.premise_support_loss_implies_null','ALLOWED'),
  ('version','current_integration.canonical_entity_version','v2.4'),
  ('terminal_r','current_integration.research_terminal_ms',1428),
  ('terminal_i','current_integration.integration_terminal_ms',1428),
  ('start1403','current_integration.ms1403_started',False),
  ('start1428','current_integration.ms1428_started',True),
  ('frontier','current_integration.selected_frontier','AUTO_MODEL_SWITCH'),
  ('language','language_policy.active_phase','LINGUISTIC'),
 ]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val);m.append((n,x))
 bools=['failed_intention_can_be_successful_learning_event','actual_outcome_only','passive_cooccurrence_not_action_law','one_outcome_not_law','minimum_support_supplied','minimum_consistency_supplied','hidden_mixture_abstains_without_observable_partition','independent_external_qualification_required','qualification_holdout_content_bound','currentness_recheck_required','historical_relation_preserved_across_drift']
 for k in bools:
  x=copy.deepcopy(p);x['action_outcome_predictive_learning_policy'][k]=False;m.append(('drop_'+k,x))
 # total deliberately fixed at 53 for the recovered v2.5 campaign contract
 assert len(m)==53, len(m)
 escaped=[n for n,x in m if validate(x)[0]]
 out={'schema':'microseed.maindev-operating-profile-validation.v2.5','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(m),'hostile_mutants_rejected':len(m)-len(escaped),'escaped':escaped,'all_pass':ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_5_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
