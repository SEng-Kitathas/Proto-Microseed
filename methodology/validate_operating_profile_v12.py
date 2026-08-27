from __future__ import annotations
import copy,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('v11',ROOT/'validate_operating_profile_v11.py');v11=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(v11)
PROFILE=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_2.json'
REQ={
'BEHAVIORAL_SYNCHRONY_NE_JOINT_COORDINATION':'SYNCHRONY_LAUNDERED_AS_COORDINATION',
'ONE_WAY_PREDICTION_NE_MUTUAL_COORDINATION':'ONE_WAY_LAUNDERED_AS_MUTUAL',
'SHARED_SCHEDULE_NE_RECIPROCAL_COORDINATION':'COMMON_SCHEDULE_LAUNDERED_AS_COORDINATION',
'TEMPORARY_REFUSAL_NE_COORDINATION_RELATION_DRIFT':'REFUSAL_LAUNDERED_AS_RELATION_DRIFT',
'COUNTERPARTY_CURRENT_NE_COORDINATION_RELATION_CURRENT':'BROAD_COUNTERPARTY_LAUNDERED_AS_RELATION_CURRENTNESS',
'COUNTERPARTY_EPOCH_AS_COORDINATION_PROXY_NE_SELECTIVE_INVALIDATION':'COARSE_PROXY_LAUNDERED_AS_SELECTIVE_CURRENTNESS',
'QUALIFICATION_TICKET_CURRENT_NE_COORDINATION_PREMISES_CURRENT':'TICKET_LAUNDERED_AS_CURRENT_PREMISES',
'JOINT_EFFECT_NE_MUTUAL_ACCEPTABILITY':'JOINT_EFFECT_LAUNDERED_AS_MUTUAL_ACCEPTABILITY',
'DESIGNER_SOCIAL_CUE_NE_COORDINATION_GROUNDING':'DESIGNER_CUE_LAUNDERED_AS_GROUNDING',
'PAIRWISE_COORDINATION_LANGUAGE_NE_GENERAL_JOINT_RELATION':'PAIRWISE_LANGUAGE_LAUNDERED_AS_GENERAL',
'SEMANTIC_COMMITMENT_LABEL_NE_OPERATIONAL_JOINT_RELATION':'SEMANTIC_LABEL_LAUNDERED_AS_OPERATIONAL_RELATION',
'coordination_relation_currentness_must_be_first_class_when_load_bearing':'RELATION_CURRENTNESS_DROPPED',
'coordination_contract_grants_operational_relation_authority_only':'COORDINATION_AUTHORITY_INFLATED',
'pending_candidates_recheck_coordination_epoch_after_external_qualification':'PENDING_RECHECK_DROPPED',
'relation_specific_drift_must_not_overinvalidate_unrelated_same_counterparty_capabilities':'SELECTIVE_INVALIDATION_DROPPED',
}
def validate(p):
    base=json.loads(v11.PROFILE.read_text());ok11,e11=v11.validate(base);e=list(e11)
    if not ok11 and not e:e.append('V11_ANCESTRY_INVALID')
    if p.get('inherits')!='microseed.maindev-operating-profile.v1.1':e.append('V12_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V12_CORE_METHOD_REPLACED')
    for k,err in REQ.items():
        if not p.get('refinements_from_ms1078_1102',{}).get(k):e.append(err)
    lang=p.get('language_policy',{})
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=1102:e.append('WRONG_RESEARCH_TERMINAL')
    if ci.get('ms1103_started') is not False:e.append('HARD_STOP_MS1103_VIOLATED')
    if not str(ci.get('selected_frontier','')).startswith('ATTN-MS1102-DISTRIBUTED-TEMPORAL-COMPETENCE'):e.append('WRONG_SELECTED_FRONTIER')
    for item in ('DISTRIBUTED_TEMPORAL_COMPETENCE_AND_JOINT_EPISODE_GROUNDING','GENERAL_MULTI_AGENT_PLANNING','SEMANTIC_COMMITMENT_INTENTION_PROMISE_ONTOLOGY'):
        if item not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED:'+item)
    for item in ('MS1088_V11_NO_FIRST_CLASS_RELATION_SPECIFIC_COORDINATION_CURRENTNESS','MS1089_V11_COORDINATION_DRIFT_FALSE_GREEN','MS1090_COUNTERPARTY_PROXY_OVERINVALIDATION'):
        if item not in ci.get('integration_debt_resolved',[]):e.append('RESOLVED_DEBT_NOT_RECORDED:'+item)
    return not e,e
def mutants(p):
    out=[]
    x=copy.deepcopy(p);x['core_shape_unchanged']=False;out.append(('replace_core_method',x))
    for k in REQ:
        x=copy.deepcopy(p);x['refinements_from_ms1078_1102'][k]=False;out.append(('drop_'+k.lower(),x))
    x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';out.append(('premature_language',x))
    x=copy.deepcopy(p);x['current_integration']['ms1103_started']=True;out.append(('quiet_next_pass',x))
    x=copy.deepcopy(p);x['inherits']='NONE';out.append(('drop_method_ancestry',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_open']=[];out.append(('erase_open_frontiers',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_resolved']=[];out.append(('erase_resolved_debt',x))
    x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1103;out.append(('lie_about_terminal',x))
    x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_SOCIAL_HELIX_ONLY';out.append(('replace_cross_family_frontier',x))
    return out
def main():
    p=json.loads(PROFILE.read_text());ok,errs=validate(p);rej=[];esc=[]
    for name,m in mutants(p):
        mok,merr=validate(m)
        if mok:esc.append(name)
        else:rej.append({'mutant':name,'errors':merr})
    out={'schema':'microseed.maindev-operating-profile-validation.v1.2','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(rej)+len(esc),'hostile_mutants_rejected':len(rej),'escaped':esc,'all_pass':ok and not esc}
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
