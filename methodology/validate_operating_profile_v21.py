from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
R=Path(__file__).parent
P=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_1.json'
PAR=R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_0.json'
BASE=json.loads(P.read_text())
REQ=list(BASE['refinements_from_ms1303_1327'])
TRUE_KEYS=['alternative_external_qualification_required','probe_pool_bound_supplied','probe_capability_currentness_required','frame_currentness_required','episode_currentness_required_when_bound','positive_disagreement_required','zero_disagreement_abstains','discriminator_unavailable_is_action_limited','repeat_count_supplied','minimum_agreement_supplied','minimum_margin_supplied','exact_outcome_equality_only','content_bound_plan_and_probe_evidence_required','evidence_replay_dedup_required','model_space_challenge_on_all_unpredicted_outcomes','restart_preserves_plan_and_witness_history']
FALSE_KEYS=['caller_current_access_is_authority','restart_restores_execution_access']
NONE_AUTH=['probe_selection_execution_authority','truth_authority','semantic_drift_cause_authority','model_switch_authority','qualification_authority','scheduling_authority']
NOT_INT=['effect_distance_metric','learned_noise_rate','intervention_synthesis','semantic_intervention_ontology','general_multi_step_active_learning','general_structural_non_identifiability_theorem','automatic_projection_switch','self_qualification']

def validate(p):
    e=[]
    if p.get('inherits')!='microseed.maindev-operating-profile.v2.0': e.append('ANCESTRY')
    if p.get('parent_profile_sha256')!=hashlib.sha256(PAR.read_bytes()).hexdigest(): e.append('PARENT_HASH')
    if p.get('core_shape_unchanged') is not True: e.append('CORE')
    for k in REQ:
        if p.get('refinements_from_ms1303_1327',{}).get(k) is not True:e.append('DROP:'+k)
    q=p.get('drift_intervention_policy',{}); ci=p.get('current_integration',{}); lang=p.get('language_policy',{})
    for k in TRUE_KEYS:
        if q.get(k) is not True:e.append('POLICY_TRUE:'+k)
    for k in FALSE_KEYS:
        if q.get(k) is not False:e.append('POLICY_FALSE:'+k)
    for k in NONE_AUTH:
        if q.get(k)!='NONE':e.append('AUTH:'+k)
    for k in NOT_INT:
        if q.get(k)!='NOT_INTEGRATED':e.append('PROMOTION:'+k)
    if q.get('probe_template_semantics')!='OPAQUE_SUPPLIED_ASSISTANCE_ANCESTRY':e.append('PROBE_SEMANTICS')
    if ci.get('research_terminal_ms')!=1327 or ci.get('integration_terminal_ms')!=1327:e.append('TERMINAL')
    if ci.get('ms1328_started') is not False:e.append('HARD_STOP')
    if ci.get('selected_frontier')!='ATTN-MS1327-QUALIFIED-COUNTERFACTUAL-REHEARSAL-AND-WHOLE-SYSTEM-CAPABILITY-CLOSURE__CROSS_FAMILY_PRELINGUAL_DELIBERATION':e.append('FRONTIER')
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE')
    # inherited v2.0 ceilings remain present
    dr=p.get('drift_recurrence_policy',{})
    for k in ('general_drift_cause_classifier','noise_process_identity','semantic_regime_identity','automatic_model_switcher','self_qualification','general_active_learning_planner'):
        if dr.get(k)!='NOT_INTEGRATED':e.append('INHERITED_PROMOTION:'+k)
    for k in ('truth_authority','drift_cause_authority','noise_semantics_authority','regime_identity_authority'):
        if dr.get(k)!='NONE':e.append('INHERITED_AUTH:'+k)
    return not e,e

def main():
    p=json.loads(P.read_text()); ok,errs=validate(p); muts=[]
    x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core',x))
    for k in REQ:
        x=copy.deepcopy(p);x['refinements_from_ms1303_1327'][k]=False;muts.append(('drop_'+k,x))
    for k in TRUE_KEYS:
        x=copy.deepcopy(p);x['drift_intervention_policy'][k]=False;muts.append(('break_'+k,x))
    for k in FALSE_KEYS:
        x=copy.deepcopy(p);x['drift_intervention_policy'][k]=True;muts.append(('flip_'+k,x))
    for k in NONE_AUTH:
        x=copy.deepcopy(p);x['drift_intervention_policy'][k]='MODEL_OUTPUT';muts.append(('grant_'+k,x))
    for k in NOT_INT:
        x=copy.deepcopy(p);x['drift_intervention_policy'][k]='INTEGRATED';muts.append(('promote_'+k,x))
    # repeat important authority mutants with distinct illegal values
    for k in NONE_AUTH:
        for val in ('INTERNAL','DERIVED_READ_ONLY','EXTERNAL_QUALIFIED'):
            x=copy.deepcopy(p);x['drift_intervention_policy'][k]=val;muts.append((f'grant_{k}_{val}',x))
    # inherited drift-recurrence ceilings
    for k in ('general_drift_cause_classifier','noise_process_identity','semantic_regime_identity','automatic_model_switcher','self_qualification','general_active_learning_planner'):
        x=copy.deepcopy(p);x['drift_recurrence_policy'][k]='INTEGRATED';muts.append(('break_inherited_'+k,x))
    for k in ('truth_authority','drift_cause_authority','noise_semantics_authority','regime_identity_authority'):
        x=copy.deepcopy(p);x['drift_recurrence_policy'][k]='MODEL_OUTPUT';muts.append(('break_inherited_auth_'+k,x))
    specs=[
      ('probe_semantics',('drift_intervention_policy','probe_template_semantics','SEMANTIC_INTERVENTION_ROLE')),
      ('language',('language_policy','cognitive_substrate','ACTIVE')),
      ('phase',('language_policy','active_phase','LINGUISTIC')),
      ('start_next',('current_integration','ms1328_started',True)),
      ('terminal_r',('current_integration','research_terminal_ms',1328)),
      ('terminal_i',('current_integration','integration_terminal_ms',1328)),
      ('frontier',('current_integration','selected_frontier','GENERAL_ACTIVE_LEARNING')),
    ]
    for n,(sec,key,val) in specs:
        x=copy.deepcopy(p);x[sec][key]=val;muts.append((n,x))
    x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_ancestry',x))
    x=copy.deepcopy(p);x['parent_profile_sha256']='0'*64;muts.append(('forge_parent_hash',x))
    rejected=[];escaped=[]
    for n,z in muts:
        mok,me=validate(z)
        if mok: escaped.append(n)
        else: rejected.append({'mutant':n,'errors':me})
    out={'schema':'microseed.maindev-operating-profile-validation.v2.1','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(muts),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
    (R/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V2_1_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0 if out['all_pass'] else 1
if __name__=='__main__': raise SystemExit(main())
