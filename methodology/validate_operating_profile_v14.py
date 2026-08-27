from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_4.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_3.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=['ZERO_DISAGREEMENT_CANDIDATE_NE_DISCRIMINATING_PROBE','ACTION_LIMITED_UNKNOWN_NE_STRUCTURAL_NONIDENTIFIABILITY','MISSING_DISCRIMINATOR_REQUIREMENT_NE_SEMANTIC_ACTION_NAME','EPISTEMIC_NEED_CAN_GUIDE_SEARCH_NE_TRUTH_AUTHORITY','DISCRIMINATOR_RECURRENCE_NE_DISCRIMINATOR_AUTHORITY','PROPOSAL_EVIDENCE_NE_QUALIFICATION_EVIDENCE','CAPABILITY_GROWTH_CAN_CHANGE_IDENTIFIABILITY_WITHOUT_RETROACTIVE_TRUTH','LATER_RESOLUTION_NE_RETROACTIVE_REWRITE','STRUCTURAL_NONIDENTIFIABILITY_NE_MISSING_CAPABILITY','AVAILABLE_DISCRIMINATOR_NE_NEED_FOR_DUPLICATE_GROWTH','LOW_PROBE_COST_NE_GOOD_EPISTEMIC_SCHEDULING','DISCRIMINATOR_CAPABILITY_CURRENT_NE_DISCRIMINATING_RELATION_CURRENT','DISCRIMINATOR_KNOWLEDGE_NE_CURRENT_EXECUTION_ACCESS','TEMPORARY_PROBE_REFUSAL_NE_DISCRIMINATOR_RELATION_DRIFT','LOCAL_PRIMITIVES_CURRENT_NE_DISTRIBUTED_DISCRIMINATOR_CURRENT','SEARCH_TOPOLOGY_NE_SEARCH_LANGUAGE','PAIRWISE_DISCOVERY_LANGUAGE_NE_GENERAL_DISCRIMINATOR_LANGUAGE','QUERY_OBLIGATION_NE_PERSISTENT_EPISTEMIC_DEFICIT','PROBE_AVAILABLE_NE_QUESTION_RESOLVED','EPISTEMIC_DEFICIT_CAN_DRIVE_DEVELOPMENT_NE_EPISTEMIC_AUTHORITY']
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.3':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE_REPLACED')
 for k in REQ:
  if not p.get('refinements_from_ms1128_1152',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{}); ci=p.get('current_integration',{}); ep=p.get('epistemic_deficit_policy',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1152 or ci.get('integration_terminal_ms')!=1152:e.append('TERMINAL')
 if ci.get('ms1153_started') is not False:e.append('HARD_STOP')
 if not str(ci.get('selected_frontier','')).startswith('ATTN-MS1152-EPISTEMIC-DEFICIT-CURRENTNESS'):e.append('FRONTIER')
 if ep.get('scope')!='C_ACTION_LIMITED_ONLY':e.append('DEFICIT_SCOPE')
 if ep.get('truth_authority')!='NONE' or ep.get('semantic_question_authority')!='NONE':e.append('AUTHORITY')
 if not ep.get('probe_available_does_not_resolve') or not ep.get('probe_evidence_only_requests_revisit') or not ep.get('historical_unknown_not_rewritten'):e.append('RESOLUTION_FIREWALL')
 g=json.loads(G.read_text());
 if 'C_ACTION_LIMITED' not in g.get('epistemic_classes',{}):e.append('GRAMMAR_LOST')
 return not e,e
def main():
 p=json.loads(P.read_text());ok,errs=validate(p); muts=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1128_1152'][k]=False;muts.append(('drop_'+k,x))
 x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';muts.append(('language',x))
 x=copy.deepcopy(p);x['current_integration']['ms1153_started']=True;muts.append(('quiet_next',x))
 x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1153;muts.append(('lie_terminal',x))
 x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_ACTIVE_LEARNING_ONLY';muts.append(('frontier',x))
 x=copy.deepcopy(p);x['epistemic_deficit_policy']['truth_authority']='MODEL_OUTPUT';muts.append(('grant_truth',x))
 x=copy.deepcopy(p);x['epistemic_deficit_policy']['probe_available_does_not_resolve']=False;muts.append(('auto_resolve_on_probe',x))
 x=copy.deepcopy(p);x['epistemic_deficit_policy']['historical_unknown_not_rewritten']=False;muts.append(('rewrite_unknown',x))
 x=copy.deepcopy(p);x['epistemic_deficit_policy']['scope']='ALL_UNKNOWN';muts.append(('collapse_unknown_classes',x))
 x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_ancestry',x))
 rej=[];esc=[]
 for n,m in muts:
  mok,me=validate(m)
  (esc if mok else rej).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.4','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(rej),'escaped':esc,'all_pass':ok and not esc}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
