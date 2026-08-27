from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_6.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_5.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=['SHARED_CURRENTNESS_ANCESTRY_NE_EPISTEMIC_BEARING', 'TEMPORAL_PROXIMITY_NE_DEFICIT_RELEVANCE', 'SURPRISE_NE_DEFICIT_SPECIFIC_BEARING', 'TOPOLOGY_GUIDANCE_NE_RELEVANCE_AUTHORITY', 'OBSERVED_CHANNEL_NE_DISCRIMINATING_CHANNEL', 'CONTRAST_BINDING_IDENTITY_MUST_BE_CONTENT_BOUND', 'DISCRIMINATING_EVIDENCE_BEARING_NE_TRUTH_AUTHORITY', 'MODEL_SPACE_CHALLENGE_NE_AUTONOMOUS_HYPOTHESIS_REPLACEMENT', 'MODEL_SUPPORT_NE_AMBIGUITY_RELEVANCE', 'EVIDENCE_REPLAY_NE_NEW_BEARING_WITNESS', 'OLD_CONTRAST_BINDING_NE_NEW_HYPOTHESIS_SPACE', 'HYPOTHESIS_CURRENT_NE_PROJECTION_BINDING_CURRENT', 'CORRELATION_NE_EPISTEMIC_BEARING', 'EPISTEMIC_BEARING_NE_ACTIVE_PROBE_EXECUTION', 'PASSIVE_SURFACE_MATCH_NE_ACTION_CONDITIONED_DISCRIMINATION', 'NUISANCE_ENTROPY_NE_DEFICIT_RELEVANCE', 'LOW_SURPRISE_NE_LOW_EPISTEMIC_BEARING', 'ONE_EVIDENCE_NE_ALL_DEFICITS_RELEVANT', 'LOW_COST_NE_LAWFUL_REVISIT_CANDIDATE', 'CONTRAST_CONTENT_AND_CURRENTNESS_GUARDS_ARE_JOINTLY_LOAD_BEARING', 'CONTENT_BOUND_HASH_NE_VERIFIED_RELEVANCE_RELATION', 'MINIMUM_RELEVANCE_BRIDGE_IS_CONTRAST_WITNESS_NOT_QUESTION_ONTOLOGY', 'RELEVANCE_SHORTCUTS_FAIL_UNDER_BOUNDARY_ATTACK', 'BOUNDED_RELEVANCE_RECOGNITION_NE_GENERAL_EPISTEMIC_PLANNER', 'BOUNDED_EVIDENCE_BEARING_NE_ENDOGENOUS_PROJECTION_DISCOVERY']
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.5':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in REQ:
  if not p.get('refinements_from_ms1178_1202',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{}); ci=p.get('current_integration',{}); ep=p.get('epistemic_bearing_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1202 or ci.get('integration_terminal_ms')!=1202:e.append('TERMINAL')
 if ci.get('ms1203_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1202-OPAQUE-CONTRAST-PROJECTION-GROUNDING-AND-DISCOVERY__PRELINGUAL_EVIDENCE_COORDINATE_FORMATION':e.append('FRONTIER')
 for k in ('truth_authority','answer_authority','semantic_question_authority'):
  if ep.get(k)!='NONE':e.append('AUTH:'+k)
 if ep.get('raw_projection_discovery')!='NOT_INTEGRATED' or ep.get('general_revisit_scheduler')!='NOT_INTEGRATED' or ep.get('general_active_learning_planner')!='NOT_INTEGRATED':e.append('SILENT_PROMOTION')
 for k in ('projection_currentness_first_class','contrast_exact_hypothesis_digest_required','contrast_content_signature_required','projection_epoch_match_required','action_condition_match_required_when_bound','discriminates_live_set_requests_revisit','model_space_challenge_requests_revisit_without_replacement_model','consensus_nondiscriminating_does_not_request_revisit','evidence_replay_deduplicated_per_binding','one_evidence_requires_deficit_specific_binding','bearing_is_not_resolution'):
  if ep.get(k) is not True:e.append('POLICY:'+k)
 g=json.loads(G.read_text())
 if 'C_ACTION_LIMITED' not in g.get('epistemic_classes',{}):e.append('GRAMMAR')
 return not e,e
def main():
 p=json.loads(P.read_text()); ok,errs=validate(p); muts=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1178_1202'][k]=False;muts.append(('drop_'+k,x))
 specs=[('language',('language_policy','cognitive_substrate','ACTIVE')),('start_next',('current_integration','ms1203_started',True)),('terminal',('current_integration','research_terminal_ms',1203)),('frontier',('current_integration','selected_frontier','GENERAL_ACTIVE_LEARNING')),('truth',('epistemic_bearing_policy','truth_authority','MODEL_OUTPUT')),('answer',('epistemic_bearing_policy','answer_authority','MODEL_OUTPUT')),('semantics',('epistemic_bearing_policy','semantic_question_authority','TOPIC')),('projection_discovery',('epistemic_bearing_policy','raw_projection_discovery','INTEGRATED')),('scheduler',('epistemic_bearing_policy','general_revisit_scheduler','INTEGRATED')),('planner',('epistemic_bearing_policy','general_active_learning_planner','INTEGRATED'))]
 for n,(sec,key,val) in specs:
  x=copy.deepcopy(p);x[sec][key]=val;muts.append((n,x))
 for k in ('projection_currentness_first_class','contrast_exact_hypothesis_digest_required','contrast_content_signature_required','projection_epoch_match_required','action_condition_match_required_when_bound','discriminates_live_set_requests_revisit','model_space_challenge_requests_revisit_without_replacement_model','consensus_nondiscriminating_does_not_request_revisit','evidence_replay_deduplicated_per_binding','one_evidence_requires_deficit_specific_binding','bearing_is_not_resolution'):
  x=copy.deepcopy(p);x['epistemic_bearing_policy'][k]=False;muts.append(('break_'+k,x))
 x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_ancestry',x))
 rejected=[];escaped=[]
 for n,m in muts:
  mok,me=validate(m); (escaped if mok else rejected).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.6','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
 print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
