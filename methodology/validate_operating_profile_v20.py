from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_0.json';PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_9.json';G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
BASE=json.loads(P.read_text());REQ=list(BASE['refinements_from_ms1278_1302'])
BOOL=['alternative_structure_accuracy_floor_supplied','alternative_structure_advantage_floor_supplied','alternative_candidate_external_qualification_required','historical_projection_must_be_stale_for_recurrence_test','recurrence_window_size_supplied','recurrence_accuracy_floor_supplied','recurrence_action_baseline_lift_supplied','recurrence_consecutive_window_count_supplied','recurrence_sample_order_supplied','external_requalification_required_for_reactivation','reactivation_advances_projection_epoch','reactivation_preserves_old_contrast_staleness','frame_epoch_recheck_required','episode_epoch_recheck_required_for_temporal_projection','restart_preserves_witness_without_identity_gain']
NONE=['general_drift_cause_classifier','noise_process_identity','semantic_regime_identity','global_historical_regime_search','automatic_model_switcher','automatic_old_contrast_reactivation','semantic_context_ontology','self_qualification','general_active_learning_planner']
AUTH=['truth_authority','drift_cause_authority','noise_semantics_authority','regime_identity_authority','reactivation_authority_from_witness','scheduling_authority','alternative_admission_authority']
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.9':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in REQ:
  if p.get('refinements_from_ms1278_1302',{}).get(k) is not True:e.append('DROP:'+k)
 l=p.get('language_policy',{});q=p.get('drift_recurrence_policy',{});ci=p.get('current_integration',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 for k in BOOL:
  if q.get(k) is not True:e.append('POLICY:'+k)
 for k in NONE:
  if q.get(k)!='NOT_INTEGRATED':e.append('SILENT_PROMOTION:'+k)
 for k in AUTH:
  if q.get(k)!='NONE':e.append('AUTH:'+k)
 if q.get('qualification_authority')!='EXTERNAL_ONLY':e.append('QUALIFICATION')
 if ci.get('research_terminal_ms')!=1302 or ci.get('integration_terminal_ms')!=1302:e.append('TERMINAL')
 if ci.get('ms1303_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1302-DISCRIMINATING-INTERVENTION-FOR-DRIFT-CAUSE-IDENTIFIABILITY__PRELINGUAL-CHANGE-CAUSE-PROBING':e.append('FRONTIER')
 if 'C_ACTION_LIMITED' not in json.loads(G.read_text()).get('epistemic_classes',{}):e.append('GRAMMAR')
 # inherited hard ceilings must still exist verbatim
 inh=p.get('inherited_robust_constructor_and_currentness_policy',{})
 for k in ('effect_distance_metric','noise_rate_model','recurring_regime_identity','self_qualification'):
  if inh.get(k)!='NOT_INTEGRATED':e.append('INHERITED_PROMOTION:'+k)
 for k in ('predictive_failure_drift_cause_authority','predictive_failure_regime_identity_authority'):
  if inh.get(k)!='NONE':e.append('INHERITED_AUTH:'+k)
 return not e,e
def main():
 p=json.loads(P.read_text());ok,errs=validate(p);mut=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;mut.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1278_1302'][k]=False;mut.append(('drop_'+k,x))
 for k in BOOL:
  x=copy.deepcopy(p);x['drift_recurrence_policy'][k]=False;mut.append(('break_'+k,x))
 for k in NONE:
  x=copy.deepcopy(p);x['drift_recurrence_policy'][k]='INTEGRATED';mut.append(('promote_'+k,x))
 for k in AUTH:
  x=copy.deepcopy(p);x['drift_recurrence_policy'][k]='MODEL_OUTPUT';mut.append(('grant_'+k,x))
 for k in ('effect_distance_metric','noise_rate_model','recurring_regime_identity','self_qualification'):
  x=copy.deepcopy(p);x['inherited_robust_constructor_and_currentness_policy'][k]='INTEGRATED';mut.append(('break_inherited_'+k,x))
 for k in ('predictive_failure_drift_cause_authority','predictive_failure_regime_identity_authority'):
  x=copy.deepcopy(p);x['inherited_robust_constructor_and_currentness_policy'][k]='MODEL_OUTPUT';mut.append(('break_inherited_'+k,x))
 specs=[('qualification',('drift_recurrence_policy','qualification_authority','INTERNAL')),('language',('language_policy','cognitive_substrate','ACTIVE')),('start_next',('current_integration','ms1303_started',True)),('terminal_r',('current_integration','research_terminal_ms',1303)),('terminal_i',('current_integration','integration_terminal_ms',1303)),('frontier',('current_integration','selected_frontier','GENERAL_REGIME_CLASSIFIER'))]
 for n,(sec,key,val) in specs:
  x=copy.deepcopy(p);x[sec][key]=val;mut.append((n,x))
 x=copy.deepcopy(p);x['inherits']='NONE';mut.append(('drop_ancestry',x));x=copy.deepcopy(p);x['parent_profile_sha256']='0'*64;mut.append(('forge_parent_hash',x))
 rejected=[];escaped=[]
 for n,z in mut:
  mok,me=validate(z);(escaped if mok else rejected).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v2.0','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(mut),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_0_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
