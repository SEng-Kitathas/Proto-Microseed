from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent; P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_2.json'; PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_1.json'; BASE=json.loads(P.read_text())
def validate(p):
 e=[]
 if p.get('inherits')!='microseed.maindev-operating-profile.v2.1': e.append('ANCESTRY')
 if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest(): e.append('PARENT_HASH')
 if p.get('core_shape_unchanged') is not True:e.append('CORE')
 for k in BASE.get('refinements_from_ms1328_1352',{}):
  if p.get('refinements_from_ms1328_1352',{}).get(k) is not True:e.append('DROP:'+k)
 r=p.get('counterfactual_rehearsal_policy',{})
 for k in ('external_qualification_required_before_admission','currentness_recheck_required','feasibility_refusal_unknown_preserved','ambiguous_transition_abstains','finite_horizon_supplied','node_budget_supplied'):
  if r.get(k) is not True:e.append('REHEARSAL:'+k)
 for k in ('execution_authority','truth_authority','qualification_authority','semantic_goal_authority','scheduling_authority'):
  if r.get(k)!='NONE':e.append('AUTH:'+k)
 for k in ('general_planner','general_counterfactual_world_model','endogenous_horizon','general_action_generation','self_qualification'):
  if r.get(k)!='NOT_INTEGRATED':e.append('PROMOTION:'+k)
 a=p.get('architectural_interrupt_policy',{})
 if a.get('hypothesis_status')!='OARR_SELECTED_NOT_INTEGRATED':e.append('INTERRUPT_STATUS')
 if a.get('coarse_commitment_candidates')!=['YES','NO','UNKNOWN']:e.append('TERNARY')
 if a.get('binding_sidecar_candidates')!=['BOUND','NULL']:e.append('NULL_BINDING')
 if a.get('refactor_before_further_buildout_if_survives') is not True:e.append('REFACTOR_RULE')
 ci=p.get('current_integration',{})
 if ci.get('research_terminal_ms')!=1352 or ci.get('integration_terminal_ms')!=1352:e.append('TERMINAL')
 if ci.get('ms1353_started') is not False:e.append('HARD_STOP')
 if ci.get('selected_frontier')!='ATTN-MS1352-TERNARY-RELATIONAL-COMMITMENT-NULL-BINDING__ARCHITECTURAL-COMPRESSION-OARR':e.append('FRONTIER')
 return not e,e
def main():
 p=json.loads(P.read_text()); ok,errs=validate(p); muts=[]
 specs=[('core',('core_shape_unchanged',False)),('start',('current_integration.ms1353_started',True)),('terminal',('current_integration.research_terminal_ms',1353)),('frontier',('current_integration.selected_frontier','GENERAL_PLANNER')),('ternary',('architectural_interrupt_policy.coarse_commitment_candidates',['YES','NO'])),('null',('architectural_interrupt_policy.binding_sidecar_candidates',['BOUND'])),('premature',('architectural_interrupt_policy.hypothesis_status','INTEGRATED'))]
 for n,(path,val) in specs:
  x=copy.deepcopy(p); cur=x; parts=path.split('.')
  for q in parts[:-1]:cur=cur[q]
  cur[parts[-1]]=val; muts.append((n,x))
 for k in ('execution_authority','truth_authority','qualification_authority','semantic_goal_authority','scheduling_authority'):
  x=copy.deepcopy(p);x['counterfactual_rehearsal_policy'][k]='INTERNAL';muts.append(('grant_'+k,x))
 for k in ('general_planner','general_counterfactual_world_model','endogenous_horizon','general_action_generation','self_qualification'):
  x=copy.deepcopy(p);x['counterfactual_rehearsal_policy'][k]='INTEGRATED';muts.append(('promote_'+k,x))
 for k in BASE['refinements_from_ms1328_1352']:
  x=copy.deepcopy(p);x['refinements_from_ms1328_1352'][k]=False;muts.append(('drop_'+k,x))
 escaped=[]
 for n,x in muts:
  if validate(x)[0]:escaped.append(n)
 out={'schema':'microseed.maindev-operating-profile-validation.v2.2','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(muts)-len(escaped),'escaped':escaped,'all_pass':ok and not escaped}
 (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_2_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2)); return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
