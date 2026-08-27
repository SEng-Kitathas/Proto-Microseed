from __future__ import annotations
import copy,hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_6.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_5.json'

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.5':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 a=p.get('predictive_adaptation_policy',{})
 exact={'scope':'QUALIFIED_ACTION_OUTCOME_RELATION_PLUS_FRESH_POST_ADMISSION_ACTUAL_OUTCOMES','drift_witness_truth_authority':'NONE','drift_cause_authority':'NONE','semantic_regime_authority':'NONE','model_switch_authority':'NONE','replacement_training_source':'DRIFT_SCOPED_EXECUTED_ACTION_PLUS_ACTUAL_EXTERNAL_OUTCOME','replacement_candidate_authority':'MODEL_OUTPUT_ONLY','replacement_self_qualification':'FORBIDDEN','automatic_model_switch':'NOT_INTEGRATED','semantic_drift_classifier':'NOT_INTEGRATED','general_regime_identity':'NOT_INTEGRATED'}
 for k,v in exact.items():
  if a.get(k)!=v:e.append('ADAPT:'+k)
 for k in ('finite_window_size_supplied','minimum_accuracy_supplied','consecutive_failure_count_supplied','structural_currentness_separate_from_empirical_currentness','isolated_miss_does_not_force_stale','transient_failed_window_then_recovery_does_not_force_stale','drift_witness_persistent','historical_old_relation_preserved','recovery_does_not_reactivate_old_relation','independent_external_requalification_required'):
  if a.get(k) is not True:e.append('ADAPT:'+k)
 for k in ('replacement_may_feed_rehearsal_before_qualification','ambiguous_hidden_mixture_nominates_replacement'):
  if a.get(k) is not False:e.append('ADAPT:'+k)
 ci=p.get('current_integration',{})
 if ci.get('canonical_entity_version')!='v2.6' or ci.get('research_terminal_ms')!=1452 or ci.get('integration_terminal_ms')!=1452:e.append('TERMINAL')
 if ci.get('ms1428_started') is not True or ci.get('ms1453_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1452-DYNAMIC-PREDICTIVE-STATE-ABSTRACTION__MUTATE-FORK-SPLIT-FACTORIZE-DEFER':e.append('FRONTIER')
 return not e,e

def setpath(x,path,val):
 cur=x; ps=path.split('.')
 for k in ps[:-1]:cur=cur[k]
 cur[ps[-1]]=val

def main():
 p=json.loads(P.read_text());ok,errs=validate(p)
 parent=subprocess.run([sys.executable,str(R/'validate_operating_profile_v25.py')],cwd=R.parent,text=True,capture_output=True)
 try: pd=json.loads(parent.stdout)
 except Exception: pd={}
 parent_ok=parent.returncode==0 and pd.get('hostile_mutants_rejected')==53
 specs=[
 ('switch_auth','predictive_adaptation_policy.model_switch_authority','MODEL_SWITCH'),('cause_auth','predictive_adaptation_policy.drift_cause_authority','CAUSE'),('regime_auth','predictive_adaptation_policy.semantic_regime_authority','REGIME'),('truth','predictive_adaptation_policy.drift_witness_truth_authority','TRUTH'),('selfqual','predictive_adaptation_policy.replacement_self_qualification','ALLOWED'),('auto_switch','predictive_adaptation_policy.automatic_model_switch','INTEGRATED'),('feed_early','predictive_adaptation_policy.replacement_may_feed_rehearsal_before_qualification',True),('mixture_law','predictive_adaptation_policy.ambiguous_hidden_mixture_nominates_replacement',True),('structural_collapse','predictive_adaptation_policy.structural_currentness_separate_from_empirical_currentness',False),('history_rewrite','predictive_adaptation_policy.historical_old_relation_preserved',False),('recovery_reactivate','predictive_adaptation_policy.recovery_does_not_reactivate_old_relation',False),('frontier','current_integration.selected_frontier','AUTO_SWITCH')]
 escaped=[]
 for n,path,val in specs:
  x=copy.deepcopy(p);setpath(x,path,val)
  if validate(x)[0]:escaped.append(n)
 out={'schema':'microseed.maindev-operating-profile-validation.v2.6','baseline_pass':ok,'baseline_errors':errs,'inherited_parent_hostile_mutants':53,'inherited_parent_hostile_mutants_rejected':53 if parent_ok else 0,'new_hostile_mutants':len(specs),'new_hostile_mutants_rejected':len(specs)-len(escaped),'combined_hostile_mutants':53+len(specs),'combined_hostile_mutants_rejected':(53 if parent_ok else 0)+len(specs)-len(escaped),'escaped':escaped,'all_pass':ok and parent_ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_6_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
