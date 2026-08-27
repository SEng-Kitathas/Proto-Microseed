from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_3.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_2_1.json'; G=R/'CAUSAL_IDENTIFIABILITY_PRESSURE_GRAMMAR_V1_0.json'
REQ=['TEMPORAL_COHERENCE_PLUS_RECURRENCE_NE_DISTRIBUTED_COMPETENCE','DISCRIMINATOR_EXISTS_IN_WORLD_NE_CURRENT_PHENOTYPE_ACCESS','CURRENT_UNKNOWN_NE_STRUCTURAL_NONIDENTIFIABILITY','HIGH_NUISANCE_NE_CAUSAL_AMBIGUITY','SURFACE_SIMILARITY_NE_CAUSAL_LAW_CURRENTNESS','PREDICTION_RESIDUAL_NE_EPISODE_BOUNDARY_AUTHORITY','EPISODE_SCHEMA_CURRENT_NE_DISTRIBUTED_EPISODE_PREMISES_CURRENT','QUALIFICATION_TICKET_CURRENT_NE_DISTRIBUTED_EPISODE_PREMISES_CURRENT','RECURRENT_DISTRIBUTED_EPISODE_NE_CAPABILITY_AUTHORITY','TEMPORARY_REFUSAL_NE_DISTRIBUTED_EPISODE_DRIFT','PREDICTIVE_EQUIVALENCE_NE_UNIQUE_EPISODE_BOUNDARY','PAIRWISE_TEMPORAL_RELATIONS_NE_GENERAL_DISTRIBUTED_EPISODE_LANGUAGE','LEARNED_TOPOLOGY_CAN_GUIDE_SEARCH_NE_DEFINES_SEARCH_LANGUAGE','episode_schema_coordination_currentness_must_be_first_class_when_load_bearing','action_limited_unknown_may_generate_missing_discriminator_developmental_pressure_but_not_truth']
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v1.2.1':e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest():e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE_REPLACED')
 for k in REQ:
  if not p.get('refinements_from_ms1103_1127',{}).get(k):e.append('DROP:'+k)
 l=p.get('language_policy',{});ci=p.get('current_integration',{})
 if l.get('active_phase')!='PRELINGUAL' or l.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
 if ci.get('research_terminal_ms')!=1127 or ci.get('integration_terminal_ms')!=1127:e.append('TERMINAL')
 if ci.get('ms1128_started') is not False:e.append('HARD_STOP')
 if not str(ci.get('selected_frontier','')).startswith('ATTN-MS1127-ACTION-LIMITED-UNKNOWN'):e.append('FRONTIER')
 if 'ENDOGENOUS_DISCRIMINATOR_CAPABILITY_GROWTH' not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED')
 g=json.loads(G.read_text());
 if 'C_ACTION_LIMITED' not in g.get('epistemic_classes',{}):e.append('GRAMMAR_LOST')
 return not e,e
def main():
 p=json.loads(P.read_text());ok,errs=validate(p);rej=[];esc=[]
 muts=[]
 x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core',x))
 for k in REQ:
  x=copy.deepcopy(p);x['refinements_from_ms1103_1127'][k]=False;muts.append(('drop_'+k,x))
 x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';muts.append(('language',x))
 x=copy.deepcopy(p);x['current_integration']['ms1128_started']=True;muts.append(('quiet_next',x))
 x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1128;muts.append(('lie_terminal',x))
 x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_EPISODE_ONLY';muts.append(('frontier',x))
 x=copy.deepcopy(p);x['current_integration']['integration_debt_open']=[];muts.append(('erase_debt',x))
 x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_ancestry',x))
 for n,m in muts:
  mok,me=validate(m)
  (esc if mok else rej).append(n if mok else {'mutant':n,'errors':me})
 out={'schema':'microseed.maindev-operating-profile-validation.v1.3','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(rej),'escaped':esc,'all_pass':ok and not esc}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
