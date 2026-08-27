from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_5.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_4.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=[
'REMEMBERED_UNKNOWN_NE_CURRENT_DEVELOPMENTAL_PRESSURE','QUESTION_KEY_NE_HYPOTHESIS_SET_CURRENTNESS',
'HYPOTHESIS_REVISION_NE_RETROACTIVE_QUESTION_REWRITE','NEW_EVIDENCE_NE_RELEVANT_EVIDENCE',
'ONE_PREMISE_DRIFT_NE_ALL_QUESTIONS_STALE','PROBE_CAPABILITY_CURRENT_NE_DISCRIMINATING_RELATION_CURRENT',
'RELEVANT_EVIDENCE_CAN_REQUEST_REVISIT_NE_ANSWER_AUTHORITY','EVIDENCE_CHURN_NE_REVISIT_PRESSURE',
'EVIDENCE_REPLAY_NE_NEW_REVISIT_TRIGGER','REVISIT_OUTCOME_NE_RETROACTIVE_DEFICIT_RESOLUTION',
'HISTORICAL_UNKNOWN_BACKLOG_NE_CURRENT_DEVELOPMENTAL_WORK','STALE_SUPPRESSION_NE_LIVENESS_LOSS',
'SURFACE_STATE_RETURN_NE_EPISTEMIC_HISTORY_REVERSION','COPIED_DEFICIT_HISTORY_NE_SHARED_FUTURE_CURRENTNESS',
'DURABLE_QUESTION_MEMORY_NE_AUTOMATIC_REACTIVATION','NUISANCE_CHANGE_NE_QUESTION_PREMISE_DRIFT',
'SIMILAR_SURFACE_NE_EPISTEMIC_PREMISE_CURRENTNESS','PROBE_ACCESS_DRIFT_NE_QUESTION_PREMISE_DRIFT',
'QUESTION_DEPENDENCY_TOPOLOGY_NE_COMPLETE_RELEVANCE_LANGUAGE','LOW_COST_NE_LAWFUL_DEVELOPMENTAL_PRESSURE',
'PERSISTENT_DEFICIT_NE_CURRENT_DEFICIT','LAWFUL_DEFICIT_CURRENTNESS_NE_ENDOGENOUS_RELEVANCE_SELECTION']

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.4':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE_REPLACED')
 for k in REQ:
  if not p.get('refinements_from_ms1153_1177',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{});ci=p.get('current_integration',{});ep=p.get('epistemic_deficit_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1177 or ci.get('integration_terminal_ms')!=1177:e.append('TERMINAL')
 if ci.get('ms1178_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1177-OPAQUE-EVIDENCE-TO-DEFICIT-RELEVANCE-BINDING__PRELINGUAL_REVISIT_SELECTION':e.append('FRONTIER')
 if ep.get('scope')!='C_ACTION_LIMITED_ONLY':e.append('DEFICIT_SCOPE')
 if ep.get('truth_authority')!='NONE' or ep.get('semantic_question_authority')!='NONE':e.append('AUTHORITY')
 if not ep.get('historical_persistence_ne_current_pressure'):e.append('HISTORY_CURRENTNESS_COLLAPSE')
 if not ep.get('typed_opaque_premise_currentness') or not ep.get('premise_drift_stales_old_deficit'):e.append('PREMISE_CURRENTNESS')
 if not ep.get('probe_access_loss_may_reopen_action_limited_when_premises_current'):e.append('PROBE_LOSS_SEMANTICS')
 if not ep.get('stale_is_not_resolved') or not ep.get('stale_excluded_from_development_pressure'):e.append('STALE_SEMANTICS')
 if not ep.get('relevant_evidence_only_requests_revisit'):e.append('REVISIT_AUTHORITY')
 if ep.get('relevance_binding')!='EXPLICIT_CONTENT_BOUND_INPUT_ONLY':e.append('RELEVANCE_BINDING')
 if ep.get('endogenous_relevance_classifier')!='NOT_INTEGRATED' or ep.get('general_revisit_scheduler')!='NOT_INTEGRATED':e.append('SILENT_PROMOTION')
 g=json.loads(G.read_text())
 if 'C_ACTION_LIMITED' not in g.get('epistemic_classes',{}):e.append('GRAMMAR_LOST')
 return not e,e

def main():
 p=json.loads(P.read_text());ok,errs=validate(p);muts=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1153_1177'][k]=False;muts.append(('drop_'+k,x))
 mutations=[
  ('language',('language_policy','cognitive_substrate','ACTIVE')),
  ('quiet_next',('current_integration','ms1178_started',True)),
  ('lie_terminal',('current_integration','research_terminal_ms',1178)),
  ('frontier',('current_integration','selected_frontier','GENERAL_ACTIVE_LEARNING')),
  ('grant_truth',('epistemic_deficit_policy','truth_authority','MODEL_OUTPUT')),
  ('history_is_pressure',('epistemic_deficit_policy','historical_persistence_ne_current_pressure',False)),
  ('drop_premise_anchors',('epistemic_deficit_policy','typed_opaque_premise_currentness',False)),
  ('premise_reopens',('epistemic_deficit_policy','premise_drift_stales_old_deficit',False)),
  ('probe_loss_stales',('epistemic_deficit_policy','probe_access_loss_may_reopen_action_limited_when_premises_current',False)),
  ('stale_resolves',('epistemic_deficit_policy','stale_is_not_resolved',False)),
  ('stale_pressure',('epistemic_deficit_policy','stale_excluded_from_development_pressure',False)),
  ('revisit_answers',('epistemic_deficit_policy','relevant_evidence_only_requests_revisit',False)),
  ('endogenous_relevance',('epistemic_deficit_policy','endogenous_relevance_classifier','INTEGRATED')),
  ('scheduler',('epistemic_deficit_policy','general_revisit_scheduler','INTEGRATED')),
  ('semantic_relevance',('epistemic_deficit_policy','relevance_binding','SEMANTIC_QUESTION_CLASSIFIER')),
 ]
 for n,(sec,key,val) in mutations:
  x=copy.deepcopy(p);x[sec][key]=val;muts.append((n,x))
 x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_ancestry',x))
 rej=[];esc=[]
 for n,m in muts:
  mok,me=validate(m); (esc if mok else rej).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.5','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(rej),'escaped':esc,'all_pass':ok and not esc}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
