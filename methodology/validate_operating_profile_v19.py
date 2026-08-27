from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_9.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_8.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=list(json.loads(P.read_text())['refinements_from_ms1253_1277'])
BOOL=['raw_observation_boundaries_supplied','opaque_action_tokens_supplied','opaque_effect_tokens_supplied','support_ceiling_supplied','history_lag_ceiling_supplied','top_supports_per_order_supplied','combination_budget_supplied','fixed_nomination_thresholds_supplied','exact_observed_effect_discordance_semantics_preserved','bounded_conflict_coverage_ranking_required','smallest_predictively_validated_support_order_required','untouched_pressure_and_nomination_validation_required','budget_exhaustion_abstains','support_ceiling_exhaustion_abstains','external_qualification_required_before_projection_admission','candidate_restart_zero_qualification_gain','frame_epoch_recheck_before_admission','episode_epoch_recheck_before_temporal_admission','post_admission_frame_drift_invalidates_projection','post_admission_episode_drift_invalidates_temporal_projection','projection_invalidation_stales_bound_contrast','predictive_currentness_window_size_supplied','predictive_currentness_accuracy_floor_supplied','predictive_currentness_consecutive_failure_windows_supplied','persistent_predictive_failure_may_stale_projection']
NONE=['effect_distance_metric','noise_rate_model','stochastic_conflict_semantics','simultaneous_hidden_context_discovery','recurring_regime_identity','automatic_regime_reactivation','general_stochastic_representation_learning','general_representation_language','unbounded_constructor_language','general_episode_time_construction','semantic_context_ontology','semantic_feature_ontology','self_qualification','general_operational_frame_construction']

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.8':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in REQ:
  if not p.get('refinements_from_ms1253_1277',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{});ci=p.get('current_integration',{});q=p.get('robust_constructor_and_currentness_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1277 or ci.get('integration_terminal_ms')!=1277:e.append('TERMINAL')
 if ci.get('ms1278_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1277-PREDICTIVE-DRIFT-CAUSE-AND-RECURRING-REGIME-CURRENTNESS__PRELINGUAL_LAW-CURRENTNESS-DECOMPOSITION':e.append('FRONTIER')
 for k in ('proposal_authority','semantic_projection_authority','truth_authority','answer_authority','predictive_failure_drift_cause_authority','predictive_failure_regime_identity_authority'):
  if q.get(k)!='NONE':e.append('AUTH:'+k)
 if q.get('qualification_authority')!='EXTERNAL_ONLY':e.append('QUALIFICATION_BOUNDARY')
 for k in BOOL:
  if q.get(k) is not True:e.append('POLICY:'+k)
 for k in NONE:
  if q.get(k)!='NOT_INTEGRATED':e.append('SILENT_PROMOTION:'+k)
 if 'C_ACTION_LIMITED' not in json.loads(G.read_text()).get('epistemic_classes',{}):e.append('GRAMMAR')
 return not e,e

def main():
 p=json.loads(P.read_text());ok,errs=validate(p);m=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;m.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1253_1277'][k]=False;m.append(('drop_'+k,x))
 for k in BOOL:
  x=copy.deepcopy(p);x['robust_constructor_and_currentness_policy'][k]=False;m.append(('break_'+k,x))
 for k in NONE:
  x=copy.deepcopy(p);x['robust_constructor_and_currentness_policy'][k]='INTEGRATED';m.append(('promote_'+k,x))
 for k in ('proposal_authority','semantic_projection_authority','truth_authority','answer_authority','predictive_failure_drift_cause_authority','predictive_failure_regime_identity_authority'):
  x=copy.deepcopy(p);x['robust_constructor_and_currentness_policy'][k]='MODEL_OUTPUT';m.append(('grant_'+k,x))
 specs=[('qualification',('robust_constructor_and_currentness_policy','qualification_authority','INTERNAL')),('language',('language_policy','cognitive_substrate','ACTIVE')),('start_next',('current_integration','ms1278_started',True)),('terminal_r',('current_integration','research_terminal_ms',1278)),('terminal_i',('current_integration','integration_terminal_ms',1278)),('frontier',('current_integration','selected_frontier','GENERAL_REGIME_LEARNING'))]
 for n,(sec,key,val) in specs:
  x=copy.deepcopy(p);x[sec][key]=val;m.append((n,x))
 x=copy.deepcopy(p);x['inherits']='NONE';m.append(('drop_ancestry',x))
 x=copy.deepcopy(p);x['parent_profile_sha256']='0'*64;m.append(('forge_parent_hash',x))
 rejected=[];escaped=[]
 for n,z in m:
  mok,me=validate(z);(escaped if mok else rejected).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.9','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(m),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
