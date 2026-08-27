from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_7.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_6.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=['PREDICTIVE_EQUIVALENCE_NE_SEMANTIC_FEATURE_IDENTITY', 'HIGH_VARIANCE_NE_USEFUL_EVIDENCE_COORDINATE', 'PASSIVE_PREDICTION_NE_ACTION_CONDITIONED_STATE_COORDINATE', 'TRAINING_CORRELATION_NE_HELDOUT_PROJECTION_VALIDITY', 'MINIMAL_SUFFICIENT_RAW_SUBSET_PREFERRED_OVER_REDUNDANT_DETAIL', 'FIXED_CONSTRUCTOR_GRAMMAR_BOUNDS_DISCOVERY_REACHABILITY', 'PAIRWISE_SUCCESS_NE_GENERAL_HIGHER_ORDER_REPRESENTATION_LANGUAGE', 'TOPOLOGY_GUIDANCE_NE_CONSTRUCTOR_ONTOLOGY', 'PROJECTION_PROPOSAL_NE_QUALIFICATION', 'PROJECTION_QUALIFICATION_NE_SEMANTIC_MEANING', 'PROJECTION_ADMISSION_NE_TRUTH_AUTHORITY', 'PROJECTION_ADMISSION_NE_BEARING_OR_ANSWER_AUTHORITY', 'RAW_OBSERVATION_BOUNDARIES_ARE_ASSISTANCE_ANCESTRY', 'OPAQUE_ACTION_TOKENS_ARE_ASSISTANCE_ANCESTRY', 'OPAQUE_EFFECT_TOKENS_ARE_ASSISTANCE_ANCESTRY', 'DISCOVERY_THRESHOLDS_ARE_ASSISTANCE_ANCESTRY', 'FRAME_CURRENTNESS_MUST_BE_RECHECKED_AT_ADMISSION', 'UNSEEN_RAW_CONFIGURATION_OWES_UNKNOWN_NOT_NEAREST_GUESS', 'PROPOSAL_REPLAY_NE_QUALIFICATION_GAIN', 'HELDOUT_SCOPE_GENERALIZATION_IS_QUALIFICATION_PRESSURE', 'PREDICTIVE_EQUIVALENCE_CAN_DISCOVER_NONADDITIVE_PARTITIONS_WITHIN_GRAMMAR', 'CONSTRUCTOR_DEPTH_EXPANSION_IS_EXTERNAL_ASSISTANCE_NOT_ENDOGENOUS_LANGUAGE_GROWTH', 'BOUNDED_PRESENT_STATE_PROJECTION_DISCOVERY_NE_TEMPORAL_HISTORY_STATE_DISCOVERY', 'BOUNDED_PROJECTION_DISCOVERY_NE_GENERAL_OPERATIONAL_FRAME_CONSTRUCTION', 'ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED_NE_SELF_QUALIFICATION']
BOOL_REQ=['raw_observation_boundaries_supplied', 'opaque_action_tokens_supplied', 'opaque_effect_tokens_supplied', 'fixed_subset_grammar_supplied', 'fixed_thresholds_supplied', 'action_conditioned_predictive_equivalence_required', 'heldout_validation_required_for_nomination', 'scope_validation_required', 'complexity_penalty_active', 'candidate_replay_deduplicated', 'unseen_raw_key_abstains', 'frame_epoch_recheck_before_admission', 'external_qualification_required_before_projection_admission', 'admitted_projection_preserves_candidate_hash', 'admitted_projection_preserves_qualification_evidence']
NONE_REQ=['general_higher_order_constructor_language', 'temporal_history_state_coordinate_discovery', 'general_operational_frame_construction', 'self_qualification', 'semantic_feature_ontology']
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.6':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in REQ:
  if not p.get('refinements_from_ms1203_1227',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{}); ci=p.get('current_integration',{}); q=p.get('projection_discovery_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1227 or ci.get('integration_terminal_ms')!=1227:e.append('TERMINAL')
 if ci.get('ms1228_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1227-PROJECTION-CONSTRUCTOR-REACHABILITY-AND-TEMPORAL-HISTORY__HIGHER_ORDER_PRELINGUAL_STATE-COORDINATE-GROWTH':e.append('FRONTIER')
 for k in ('proposal_authority','semantic_projection_authority','truth_authority','answer_authority'):
  if q.get(k)!='NONE':e.append('AUTH:'+k)
 if q.get('qualification_authority')!='EXTERNAL_ONLY':e.append('QUALIFICATION_BOUNDARY')
 for k in BOOL_REQ:
  if q.get(k) is not True:e.append('POLICY:'+k)
 for k in NONE_REQ:
  if q.get(k)!='NOT_INTEGRATED':e.append('SILENT_PROMOTION:'+k)
 g=json.loads(G.read_text())
 if 'C_ACTION_LIMITED' not in g.get('epistemic_classes',{}):e.append('GRAMMAR')
 return not e,e
def main():
 p=json.loads(P.read_text());ok,errs=validate(p);m=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;m.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1203_1227'][k]=False;m.append(('drop_'+k,x))
 specs=[('language',('language_policy','cognitive_substrate','ACTIVE')),('start_next',('current_integration','ms1228_started',True)),('terminal',('current_integration','research_terminal_ms',1228)),('frontier',('current_integration','selected_frontier','GENERAL_REPRESENTATION_LEARNING')),('proposal_truth',('projection_discovery_policy','proposal_authority','TRUTH')),('semantic',('projection_discovery_policy','semantic_projection_authority','FEATURE_IDENTITY')),('truth',('projection_discovery_policy','truth_authority','MODEL_OUTPUT')),('answer',('projection_discovery_policy','answer_authority','MODEL_OUTPUT')),('self_qual',('projection_discovery_policy','qualification_authority','INTERNAL'))]
 for n,(sec,key,val) in specs:
  x=copy.deepcopy(p);x[sec][key]=val;m.append((n,x))
 for k in BOOL_REQ:
  x=copy.deepcopy(p);x['projection_discovery_policy'][k]=False;m.append(('break_'+k,x))
 for k in NONE_REQ:
  x=copy.deepcopy(p);x['projection_discovery_policy'][k]='INTEGRATED';m.append(('promote_'+k,x))
 x=copy.deepcopy(p);x['inherits']='NONE';m.append(('drop_ancestry',x))
 rejected=[];escaped=[]
 for n,z in m:
  mok,me=validate(z);(escaped if mok else rejected).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.7','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(m),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
