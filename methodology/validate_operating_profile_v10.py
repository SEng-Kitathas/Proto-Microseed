from __future__ import annotations
import copy,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('legacy_validate',ROOT/'validate_operating_profile.py')
legacy=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(legacy)
PROFILE=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V1_0.json'
REQ={
'STRUCTURAL_REWRITE_NE_DEVELOPMENTAL_TERMINATION':'STRUCTURAL_REWRITE_LAUNDERED_AS_IDENTITY_TERMINATION',
'ENDPOINT_EQUIVALENCE_NE_DEVELOPMENTAL_CONTINUITY':'ENDPOINT_EQUIVALENCE_LAUNDERED_AS_CONTINUITY',
'STABLE_ENTITY_TOKEN_NE_DEVELOPMENTAL_IDENTITY':'TOKEN_LAUNDERED_AS_IDENTITY',
'BOUNDED_DEVELOPMENTAL_LINEAGE_RELATION_NE_PERSISTENT_SELFHOOD':'LINEAGE_LAUNDERED_AS_SELFHOOD',
'COMMON_PARENT_CAN_HAVE_MULTIPLE_LAWFUL_DESCENDANT_CONTINUATIONS':'FORK_COLLAPSED_TO_SINGLE_ORIGINAL',
'SAME_BIOGRAPHY_GRAPH_STATE_NE_SAME_NUMERICAL_INDIVIDUAL':'GRAPH_EQUALITY_LAUNDERED_AS_NUMERICAL_IDENTITY',
'CONTENT_BOUND_BIOGRAPHY_NE_EXECUTION_UNIQUENESS':'CONTENT_HASH_LAUNDERED_AS_EXECUTION_UNIQUENESS',
'COPYABLE_INTERNAL_CONTINUATION_MARKER_NE_EXCLUSIVE_SUCCESSOR_AUTHORITY':'COPYABLE_MARKER_GRANTED_EXCLUSIVE_AUTHORITY',
'EXTERNAL_CANONICAL_CONTINUATION_AUTHORITY_MUST_REMAIN_EXPLICIT_ASSISTANCE':'EXTERNAL_IDENTITY_ASSISTANCE_HIDDEN',
'TOPOLOGY_PRESERVATION_NE_DEVELOPMENTAL_CONTINUITY_REQUIREMENT':'TOPOLOGY_EQUALITY_MADE_CONTINUITY_REQUIREMENT',
'DEVELOPMENTAL_CONTINUITY_NE_CAPABILITY_PRESERVATION':'COMPETENCE_PRESERVATION_CONFLATED_WITH_CONTINUITY',
'STATE_REVERSION_NE_HISTORY_REVERSION':'ROLLBACK_ERASED_HISTORY',
'BIOGRAPHY_INTEGRITY_FAILURE_FORCES_UNKNOWN':'INTEGRITY_FAILURE_ALLOWED_IDENTITY_GUESS',
'LEDGER_POSSESSION_NE_CAUSAL_EMBODIMENT_PROVENANCE':'COPIED_LEDGER_LAUNDERED_AS_EMBODIMENT_PROVENANCE',
'MULTI_ANCESTRY_DESCENDANCE_NE_UNIQUE_NUMERICAL_IDENTITY':'MERGE_LAUNDERED_AS_UNIQUE_IDENTITY',
'EXCLUSIVE_CONTINUATION_AUTHORITY_HAS_AVAILABILITY_COST':'EXCLUSIVE_AUTHORITY_ECONOMICS_HIDDEN',
'TERMINAL_STATE_EQUIVALENCE_NE_DEVELOPMENTAL_PATH_EQUIVALENCE':'TERMINAL_STATE_LAUNDERED_AS_PATH_EQUIVALENCE',
'FUTURE_DIVERGENCE_NE_RETROACTIVE_ORIGINAL_IDENTITY_AUTHORITY':'FUTURE_DIVERGENCE_RETROACTIVELY_INVENTED_ORIGINAL',
'exact_copy_ambiguity_must_be_explicit_in_entity_witness':'COPY_AMBIGUITY_DROPPED_FROM_ENTITY_CONTRACT',
'typed_continuity_witness_grants_lineage_authority_only':'CONTINUITY_WITNESS_GRANTED_SELFHOOD_AUTHORITY',
'internal_biography_cannot_self_grant_exclusive_successor_authority':'BIOGRAPHY_SELF_GRANTED_EXCLUSIVE_SUCCESSOR_AUTHORITY',
'branch_relative_agency_other_agent_frontier_selection_is_cross_family_evidence_driven':'OTHER_AGENT_FRONTIER_REPLACED_BY_LOCAL_IDENTITY_WATERFALL',
}

def legacy_ok():
    v02=json.loads(legacy.P02.read_text());v03=json.loads(legacy.P03.read_text());v04=json.loads(legacy.P04.read_text());v05=json.loads(legacy.P05.read_text());v06=json.loads(legacy.P06.read_text());v07=json.loads(legacy.P07.read_text());v08=json.loads(legacy.P08.read_text());v09=json.loads(legacy.PROFILE.read_text())
    return legacy.validate_v09(v02,v03,v04,v05,v06,v07,v08,v09)

def validate(p):
    ok09,e09=legacy_ok(); e=list(e09)
    if not ok09 and not e:e.append('V09_ANCESTRY_INVALID')
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.9':e.append('V10_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V10_CORE_METHOD_REPLACED')
    for k,err in REQ.items():
        if not p.get('refinements_from_ms1028_1052',{}).get(k):e.append(err)
    lang=p.get('language_policy',{})
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=1052:e.append('WRONG_RESEARCH_TERMINAL')
    if ci.get('ms1053_started') is not False:e.append('HARD_STOP_MS1053_VIOLATED')
    if ci.get('selected_frontier')!='ATTN-MS1052-BRANCH-RELATIVE-AGENCY-OTHER-AGENT-DISCRIMINATION__REACTIVATES_SOCIAL_OTHER_AGENT_AUDIT_AND_GRAND_P5':e.append('WRONG_SELECTED_FRONTIER')
    for item in ('PERSISTENT_NUMERICAL_SELFHOOD_NOT_QUALIFIED','UNASSISTED_EXCLUSIVE_CONTINUATION_AUTHORITY','GENERAL_BIOGRAPHY_MERGE_SEMANTICS','BRANCH_RELATIVE_AGENCY_OTHER_AGENT_DISCRIMINATION'):
        if item not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED:'+item)
    for item in ('MS1049_V09_SAME_BIOGRAPHY_STATE_STRING_LACKED_EXPLICIT_COPY_AMBIGUITY_CEILING','MS1051_V09_NO_TYPED_BRANCH_RELATIVE_CONTINUITY_WITNESS'):
        if item not in ci.get('integration_debt_resolved',[]):e.append('INTEGRATION_DEBT_DROPPED:'+item)
    return not e,e

def mutants(p):
    out=[]
    x=copy.deepcopy(p);x['core_shape_unchanged']=False;out.append(('replace_core_method',x))
    for k in REQ:
        x=copy.deepcopy(p);x['refinements_from_ms1028_1052'][k]=False;out.append(('drop_'+k.lower(),x))
    x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';out.append(('premature_language',x))
    x=copy.deepcopy(p);x['current_integration']['ms1053_started']=True;out.append(('quiet_next_pass',x))
    x=copy.deepcopy(p);x['inherits']='NONE';out.append(('drop_method_ancestry',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_open']=[];out.append(('erase_open_frontiers',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_resolved']=[];out.append(('erase_resolved_debt',x))
    x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1053;out.append(('lie_about_terminal',x))
    x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_IDENTITY_HELIX_ONLY';out.append(('replace_cross_family_frontier',x))
    return out

def main():
    p=json.loads(PROFILE.read_text());ok,errs=validate(p); rejected=[];escaped=[]
    for name,m in mutants(p):
        mok,merr=validate(m)
        if mok: escaped.append(name)
        else: rejected.append({'mutant':name,'errors':merr})
    out={'schema':'microseed.maindev-operating-profile-validation.v1.0','baseline_pass':ok,'baseline_errors':errs,'hostile_mutants':len(rejected)+len(escaped),'hostile_mutants_rejected':len(rejected),'escaped':escaped,'all_pass':ok and not escaped}
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
