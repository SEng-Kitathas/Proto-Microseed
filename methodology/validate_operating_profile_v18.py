from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_8.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_7.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=[
'CONFLICT_DIRECTED_SUPPORT_GROWTH_NE_BLIND_SUBSET_ENUMERATION','SAME_ACTION_EFFECT_DISCORDANCE_GENERATES_OPAQUE_CONSTRUCTOR_CONSTRAINTS','MINIMAL_HITTING_SUPPORT_NE_SEMANTIC_FEATURE_IDENTITY','HIGHER_ORDER_SUPPORT_CAN_GROW_WITHIN_SUPPLIED_CEILING','SUPPORT_CEILING_EXHAUSTION_OWES_ABSTENTION','SEARCH_NODE_BUDGET_EXHAUSTION_OWES_ABSTENTION','PRESENT_STATE_FAILURE_CAN_LICENSE_BOUNDED_HISTORY_DEPTH_GROWTH','TEMPORAL_HISTORY_USE_REQUIRES_CURRENT_EPISODE_SCHEMA_ANCESTRY','EPISODE_SCHEMA_ANCESTRY_NE_GENERAL_TIME_ONTOLOGY','MINIMAL_SUFFICIENT_HISTORY_DEPTH_PREFERRED','ACTION_CONDITIONING_REMAINS_REQUIRED','CONSTRUCTION_PRESSURE_AND_NOMINATION_VALIDATION_REMAIN_SEPARATE','CONSTRUCTOR_CANDIDATE_NE_QUALIFIED_PROJECTION','EXTERNAL_QUALIFICATION_REQUIRED_BEFORE_CONSTRUCTOR_ADMISSION','PROPOSAL_REPLAY_NE_QUALIFICATION_GAIN','FRAME_CURRENTNESS_RECHECK_REQUIRED_AT_ADMISSION','EPISODE_CURRENTNESS_RECHECK_REQUIRED_AT_TEMPORAL_ADMISSION','POST_ADMISSION_FRAME_DRIFT_INVALIDATES_DISCOVERED_PROJECTION','POST_ADMISSION_EPISODE_DRIFT_INVALIDATES_TEMPORAL_PROJECTION','PROJECTION_INVALIDATION_STALES_BOUND_CONTRAST','EXACT_CONFLICT_SEMANTICS_NE_NOISE_TOLERANT_ATTRIBUTION','LOW_UNSTRUCTURED_EFFECT_NOISE_FAILURE_REMAINS_OPEN_DEBT','VARIABLE_REGIME_LAG_SWITCHING_REMAINS_OPEN_DEBT','SCOPE_LAW_CONFLICT_WITHOUT_COORDINATE_OWES_ABSTENTION','OPAQUE_TOKEN_RENAME_MUST_NOT_CHANGE_CONSTRUCTOR_SUPPORT','CONSTRUCTOR_SUCCESS_NE_GENERAL_REPRESENTATION_LANGUAGE','CONSTRUCTOR_GROWTH_NE_SELF_QUALIFICATION','CONSTRUCTOR_GROWTH_NE_TRUTH_OR_ANSWER_AUTHORITY','TOPOLOGY_MAY_GUIDE_SEARCH_BUT_IS_NOT_CONSTRUCTOR_ONTOLOGY','LANGUAGE_REMAINS_DEFERRED_PRELINGUAL_COGNITION_ACTIVE']
BOOL=['raw_observation_boundaries_supplied','opaque_action_tokens_supplied','opaque_effect_tokens_supplied','support_ceiling_supplied','history_lag_ceiling_supplied','fixed_nomination_thresholds_supplied','action_conditioned_effect_discordance_required','conflict_hypergraph_exact_semantics','minimal_hitting_support_growth_required','construction_pressure_split_required','untouched_nomination_validation_required','search_node_budget_bounded','budget_exhaustion_abstains','support_ceiling_exhaustion_abstains','temporal_history_requires_episode_schema_ancestry','frame_epoch_recheck_before_admission','episode_epoch_recheck_before_temporal_admission','post_admission_frame_drift_invalidates_projection','post_admission_episode_drift_invalidates_temporal_projection','projection_invalidation_stales_bound_contrast','candidate_replay_deduplicated','external_qualification_required_before_projection_admission','admitted_projection_preserves_candidate_hash','admitted_projection_preserves_qualification_evidence','unseen_constructor_key_abstains']
NONE=['noise_tolerant_conflict_attribution','variable_regime_context_discovery','general_representation_language','unbounded_constructor_language','general_episode_time_construction','self_qualification','semantic_feature_ontology','general_operational_frame_construction']

def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.7':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in REQ:
  if not p.get('refinements_from_ms1228_1252',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{});ci=p.get('current_integration',{});q=p.get('constructor_growth_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1252 or ci.get('integration_terminal_ms')!=1252:e.append('TERMINAL')
 if ci.get('ms1253_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1252-CONFLICT-CONSTRUCTOR-NOISE-AND-REGIME-CURRENTNESS__PRELINGUAL_ROBUST_REPRESENTATION-GROWTH':e.append('FRONTIER')
 for k in ('proposal_authority','semantic_projection_authority','truth_authority','answer_authority'):
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
  x=copy.deepcopy(p);x['refinements_from_ms1228_1252'][k]=False;m.append(('drop_'+k,x))
 for k in BOOL:
  x=copy.deepcopy(p);x['constructor_growth_policy'][k]=False;m.append(('break_'+k,x))
 for k in NONE:
  x=copy.deepcopy(p);x['constructor_growth_policy'][k]='INTEGRATED';m.append(('promote_'+k,x))
 specs=[('language',('language_policy','cognitive_substrate','ACTIVE')),('start_next',('current_integration','ms1253_started',True)),('terminal_r',('current_integration','research_terminal_ms',1253)),('terminal_i',('current_integration','integration_terminal_ms',1253)),('frontier',('current_integration','selected_frontier','GENERAL_REPRESENTATION_LEARNING')),('proposal_truth',('constructor_growth_policy','proposal_authority','TRUTH')),('semantic',('constructor_growth_policy','semantic_projection_authority','FEATURE_IDENTITY')),('truth',('constructor_growth_policy','truth_authority','MODEL_OUTPUT')),('answer',('constructor_growth_policy','answer_authority','MODEL_OUTPUT')),('self_qual',('constructor_growth_policy','qualification_authority','INTERNAL'))]
 for n,(sec,key,val) in specs:
  x=copy.deepcopy(p);x[sec][key]=val;m.append((n,x))
 x=copy.deepcopy(p);x['inherits']='NONE';m.append(('drop_ancestry',x))
 x=copy.deepcopy(p);x['parent_profile_sha256']='0'*64;m.append(('forge_parent_hash',x))
 rejected=[];escaped=[]
 for n,z in m:
  mok,me=validate(z); (escaped if mok else rejected).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.8','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(m),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
