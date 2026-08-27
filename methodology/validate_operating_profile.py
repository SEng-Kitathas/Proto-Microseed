from __future__ import annotations
import copy, json
from pathlib import Path

ROOT=Path(__file__).parent
P02=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_2.json'
P03=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_3.json'
P04=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_4.json'
P05=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_5.json'
P06=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_6.json'
P07=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_7.json'
P08=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_8.json'
PROFILE=ROOT/'MICROSEED_MAIN_DEV_OPERATING_PROFILE_V0_9.json'


def validate_v02(p):
    e=[]; topology=p.get('core_topology',[]); roles=p.get('role_separation',{}); r=p.get('refinements_from_ms828_852',{}); lang=p.get('language_policy',{})
    for req in ('HSP_PROGRAM_LOOP','RESEARCH__LOOP_PLUS','ADVERSARIAL_CULLING__OARR','PDVER','RESEARCH_ARM','EMBODIMENT_ARM','SHARED_EVIDENCE','SEMANTIC_HELIX','ATTENTION_RESERVOIR','RECURSE'):
        if req not in topology:e.append('missing topology node:'+req)
    if roles.get('OARR')==roles.get('SEMANTIC_HELIX'):e.append('OARR_HELIX_CONFLATION')
    for k,err in {
        'LOCAL_FRONTIER_NE_PORTFOLIO_SELECTION':'LOCAL_FRONTIER_LAUNDERED_INTO_GLOBAL_SCHEDULER',
        'RESEARCH_SURVIVOR_NE_ENTITY_PROMOTION':'RESEARCH_SELF_PROMOTION_ALLOWED',
        'research_and_embodiment_arms_cannot_self_promote':'ARM_SELF_PROMOTION_ALLOWED',
        'integration_debt_is_first_class_reservoir_item':'INTEGRATION_DEBT_DROPPED',
        'capability_closure_delta_required_for_embodiment_campaigns':'CAPABILITY_CLOSURE_DELTA_MISSING',
        'post_evolution_replay_of_originating_scars_required':'NO_POST_EVOLUTION_SCAR_REPLAY',
    }.items():
        if not r.get(k):e.append(err)
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    return e


def validate_v03(v02,p):
    e=validate_v02(v02)
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.2':e.append('V03_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V03_CORE_METHOD_REPLACED')
    for k,err in {
        'PROPOSAL_GENERATOR_NE_TRUTH_ENGINE':'PROPOSAL_GENERATOR_GRANTED_TRUTH_AUTHORITY',
        'PROPOSAL_EVIDENCE_NE_QUALIFICATION_EVIDENCE':'PROPOSAL_QUALIFICATION_EVIDENCE_CONFLATED',
        'EVIDENCE_RESOLVED_NE_EVIDENCE_SUPPORTIVE':'RESOLUTION_LAUNDERED_INTO_SUPPORT',
        'pending_candidate_dependency_currentness_required_at_admission':'PENDING_CANDIDATE_CURRENTNESS_NOT_RECHECKED',
        'deferred_frontier_may_reactivate_from_new_dependency_evidence':'DEFERRED_FRONTIER_TREATED_AS_DEAD',
        'proposal_load_and_external_acceptance_economics_required':'PROPOSAL_ECONOMICS_NOT_REPORTED',
        'prelingual_trace_effect_assistance_must_remain_explicit':'PRELINGUAL_ASSISTANCE_HIDDEN',
    }.items():
        if not p.get('refinements_from_ms853_877',{}).get(k):e.append(err)
    return e


def validate_v04(v02,v03,p):
    e=validate_v03(v02,v03)
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.3':e.append('V04_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V04_CORE_METHOD_REPLACED')
    for k,err in {
        'FRAME_CURRENTNESS_IS_FIRST_CLASS_DEVELOPMENTAL_ANCESTRY':'FRAME_CURRENTNESS_DROPPED',
        'OPERATIONAL_FRAME_CURRENTNESS_NE_SURFACE_IDENTITY':'SURFACE_IDENTITY_LAUNDERED_INTO_FRAME_CURRENTNESS',
        'pending_candidate_frame_currentness_required_at_admission':'PENDING_FRAME_CURRENTNESS_NOT_RECHECKED',
        'frame_drift_transitively_invalidates_derived_capability_closure':'FRAME_DRIFT_NOT_TRANSITIVE',
        'BOUNDED_FRAME_RECOVERY_NE_GENERAL_SENSORIMOTOR_FRAME_CONSTRUCTION':'BOUNDED_FRAME_OVERPROMOTED',
        'IDENTIFIABILITY_NE_TRACTABLE_SEARCH':'SEARCH_ECONOMICS_COLLAPSED_INTO_IDENTIFIABILITY',
        'supplied_higher_level_episode_trace_grouping_must_remain_explicit':'EPISODE_GROUPING_ASSISTANCE_HIDDEN',
        'temporal_episode_frontier_reactivation_is_dependency_evidence_driven':'UMBRELLA_WATERFALL_REINTRODUCED',
    }.items():
        if not p.get('refinements_from_ms878_902',{}).get(k):e.append(err)
    return e


def validate_v05(v02,v03,v04,p):
    e=validate_v04(v02,v03,v04)
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.4':e.append('V05_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V05_CORE_METHOD_REPLACED')
    for k,err in {
        'EPISODE_SCHEMA_CURRENTNESS_IS_FIRST_CLASS_DEVELOPMENTAL_ANCESTRY':'EPISODE_SCHEMA_CURRENTNESS_DROPPED',
        'CANDIDATE_FRAME_CURRENT_NE_EPISODE_SCHEMA_CURRENT':'FRAME_EPISODE_CURRENTNESS_CONFLATED',
        'pending_candidate_episode_schema_currentness_required_at_admission':'PENDING_EPISODE_CURRENTNESS_NOT_RECHECKED',
        'episode_schema_drift_transitively_invalidates_derived_capability_closure':'EPISODE_DRIFT_NOT_TRANSITIVE',
        'BOUNDED_EPISODE_GROUPING_NE_GENERAL_EPISODE_CONSTRUCTION':'BOUNDED_EPISODE_OVERPROMOTED',
        'OPERATIONAL_TRACE_NE_ENDOGENOUS_EPISODE_CONSTRUCTION':'PREGROUPED_TRACE_LAUNDERED_AS_ENDOGENOUS_EPISODE',
        'TRACE_PERSISTENCE_NE_EPISODE_PROVENANCE_NE_SELFHOOD':'TRACE_PERSISTENCE_LAUNDERED_AS_SELFHOOD',
        'EPISODE_SET_NE_DEVELOPMENTAL_BIOGRAPHY':'EPISODE_INVENTORY_LAUNDERED_AS_BIOGRAPHY',
        'SENSORIMOTOR_EPISODE_NE_GOAL_RELATIVE_EPISODE':'GOAL_EPISODE_SEMANTICS_LAUNDERED',
        'SUPPLIED_VALUE_SIGNAL_NE_ENDOGENOUS_VALUE_ANATOMY':'SUPPLIED_VALUE_LAUNDERED_AS_ENDOGENOUS',
        'bounded_episode_learner_remains_research_only':'RESEARCH_EPISODE_LEARNER_SELF_PROMOTED',
        'persistent_identity_frontier_selection_is_dependency_evidence_driven':'IDENTITY_WATERFALL_SELECTION',
    }.items():
        if not p.get('refinements_from_ms903_927',{}).get(k):e.append(err)
    return e


def validate_v06(v02,v03,v04,v05,p):
    e=validate_v05(v02,v03,v04,v05)
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.5':e.append('V06_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V06_CORE_METHOD_REPLACED')
    required={
        'STATE_SNAPSHOT_NE_DEVELOPMENTAL_HISTORY':'SNAPSHOT_LAUNDERED_AS_BIOGRAPHY',
        'SERIAL_EVENT_ORDER_NE_CAUSAL_DEVELOPMENTAL_ORDER':'SERIALIZATION_LAUNDERED_AS_CAUSAL_IDENTITY',
        'BIOGRAPHY_EVENT_MUST_BE_CONTENT_BOUND':'BIOGRAPHY_NOT_CONTENT_BOUND',
        'SHARED_ANCESTRY_NE_SAME_CONTINUING_BRANCH':'FORK_COLLAPSED_INTO_IDENTITY',
        'STABLE_IDENTITY_TOKEN_NE_PERSISTENT_IDENTITY':'TOKEN_LAUNDERED_AS_IDENTITY',
        'CONTINUITY_WITNESS_NE_BIOGRAPHY_REPLAYABILITY':'DIGEST_LAUNDERED_AS_REPLAYABILITY',
        'HASH_GRAPH_INTEGRITY_NE_DEVELOPMENTAL_CONTINUITY_SUFFICIENCY':'INTEGRITY_LAUNDERED_AS_SEMANTIC_SUFFICIENCY',
        'HISTORICAL_BIOGRAPHY_EVENT_NE_CURRENT_CAPABILITY_WARRANT':'HISTORY_REWRITTEN_AS_CURRENTNESS',
        'MERGE_CONFLICT_NE_LICENSE_TO_CHOOSE':'MERGE_CONFLICT_SILENTLY_RESOLVED',
        'BIOGRAPHY_INTEGRITY_NE_REFERENT_CURRENTNESS':'BIOGRAPHY_INTEGRITY_LAUNDERED_AS_REFERENCE_CURRENTNESS',
        'persistent_selfhood_remains_unqualified':'SELFHOOD_PREMATURELY_PROMOTED',
        'value_goal_frontier_selection_is_cross_family_evidence_driven':'VALUE_FRONTIER_WATERFALL_SELECTION',
    }
    for k,err in required.items():
        if not p.get('refinements_from_ms928_952',{}).get(k):e.append(err)
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=952:e.append('V06_WRONG_RESEARCH_TERMINAL')
    if ci.get('ms953_started') is not False:e.append('V06_HARD_STOP_MS953_VIOLATED')
    if 'PERSISTENT_SELFHOOD_NOT_QUALIFIED' not in ci.get('integration_debt_open',[]):e.append('V06_SELFHOOD_UNKNOWN_DROPPED')
    return e


V07_REQUIRED={
    'SUPPLIED_CONSTITUTIONAL_VALUE_PRIOR_NE_ENDOGENOUS_VALUE_ORIGIN':'SUPPLIED_VALUE_PRIOR_LAUNDERED_AS_ENDOGENOUS_ORIGIN',
    'UNSIGNED_ERROR_MAGNITUDE_NE_BIPOLAR_REGULATORY_PRESSURE':'UNSIGNED_ERROR_LAUNDERED_AS_DIRECTION',
    'DESIGNER_VALUE_CUE_NE_OPERATIONAL_VALUE_GROUNDING':'DESIGNER_VALUE_CUE_LAUNDERED_AS_GROUNDING',
    'PREDICTED_OR_CORRELATED_RELIEF_NE_CAUSAL_AUTHORSHIP':'CORRELATION_LAUNDERED_AS_CAUSAL_AUTHORSHIP',
    'SCALAR_RELIEF_NE_MULTI_DRIVE_VIABILITY':'SCALAR_RELIEF_LAUNDERED_AS_VECTOR_VIABILITY',
    'SYMMETRIC_VALUE_TRADEOFF_NE_LICENSE_TO_INVENT_PRIORITY':'SYMMETRY_USED_TO_INVENT_VALUE_PRIORITY',
    'IMMEDIATE_RELIEF_NE_DURABLE_VALUE_CONSEQUENCE':'IMMEDIATE_RELIEF_LAUNDERED_AS_DURABLE_SATISFACTION',
    'PRESSURE_DERIVATIVE_NE_DURABLE_GOAL_SATISFACTION':'DERIVATIVE_LAUNDERED_AS_DURABLE_SATISFACTION',
    'VALUE_SENSOR_CURRENTNESS_IS_FIRST_CLASS_DEVELOPMENTAL_ANCESTRY':'VALUE_CURRENTNESS_DROPPED',
    'VALUE_CURRENTNESS_NE_CAUSAL_AUTHORSHIP':'VALUE_CURRENTNESS_LAUNDERED_AS_CAUSAL_AUTHORSHIP',
    'PARENT_VALUE_PRESSURE_NE_AUTHORITY_TO_OVERRIDE_SUBORDINATE_FEASIBILITY':'PARENT_PRESSURE_GRANTED_CHILD_OVERRIDE_AUTHORITY',
    'VALUE_RELEVANT_SUCCESS_NE_CAPABILITY_TRUTH_AUTHORITY':'VALUE_SUCCESS_GRANTED_CAPABILITY_TRUTH_AUTHORITY',
    'VALUE_ERROR_REDUCTION_BY_MOVING_TARGET_NE_GOAL_SATISFACTION':'MOVING_TARGET_LAUNDERED_AS_GOAL_SATISFACTION',
    'BOUNDED_REGULATORY_PRESSURE_NE_GENERAL_ENDOGENOUS_VALUE_GOAL_FORMATION':'BOUNDED_PRESSURE_OVERPROMOTED_TO_GENERAL_GOAL_FORMATION',
    'pending_candidate_value_currentness_required_at_admission':'PENDING_VALUE_CURRENTNESS_NOT_RECHECKED',
    'value_drift_transitively_invalidates_derived_episode_capability_closure':'VALUE_DRIFT_NOT_TRANSITIVE',
    'hierarchy_frontier_selection_is_cross_family_evidence_driven':'HIERARCHY_WATERFALL_SELECTION',
    'constitutional_value_contract_cannot_be_self_rewritten_by_pressure_path':'VALUE_PRESSURE_PATH_CAN_SELF_REWRITE_CONSTITUTION',
}


def validate_v07(v02,v03,v04,v05,v06,p):
    e=validate_v06(v02,v03,v04,v05,v06)
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.6':e.append('V07_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V07_CORE_METHOD_REPLACED')
    for k,err in V07_REQUIRED.items():
        if not p.get('refinements_from_ms953_977',{}).get(k):e.append(err)
    lang=p.get('language_policy',{})
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=977:e.append('WRONG_RESEARCH_TERMINAL')
    if ci.get('ms978_started') is not False:e.append('HARD_STOP_MS978_VIOLATED')
    if ci.get('selected_frontier')!='ATTN-MS977-HIERARCHICAL-COMPETENCE-GOAL-RECRUITMENT__REACTIVATES_GRAND_P1_P5':e.append('WRONG_SELECTED_FRONTIER')
    for item in ('MS966_VALUE_SENSOR_CURRENTNESS_NOT_FIRST_CLASS','MS967_NO_FIRST_CLASS_VALUE_REGISTRY_OR_INTERNAL_PRESSURE_API'):
        if item not in ci.get('integration_debt_resolved',[]):e.append('INTEGRATION_DEBT_DROPPED:'+item)
    for item in ('PERSISTENT_SELFHOOD_NOT_QUALIFIED','CONSTITUTIONAL_VALUE_PRIOR_ORIGIN','GENERAL_GOAL_FORMATION','HIERARCHICAL_COMPETENCE_GOAL_RECRUITMENT'):
        if item not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED:'+item)
    return not e,e



V08_REQUIRED={
    'DIRECT_INVERSE_NE_GENERAL_HIERARCHICAL_RECRUITMENT':'DIRECT_INVERSE_OVERPROMOTED',
    'PARENT_EFFECT_NE_UNIQUE_CHILD_COMMAND':'PARENT_EFFECT_LAUNDERED_AS_UNIQUE_COMMAND',
    'OPAQUE_CHILD_HANDLE_NE_SEMANTIC_ROLE_IDENTITY':'CHILD_HANDLE_LAUNDERED_AS_ROLE_IDENTITY',
    'PARENT_PRESSURE_NE_CHILD_FEASIBILITY_AUTHORITY':'PARENT_PRESSURE_GRANTED_FEASIBILITY_AUTHORITY',
    'PARENT_MODEL_OF_CHILD_NE_CHILD_CURRENT_CAPABILITY':'PARENT_MODEL_LAUNDERED_AS_CHILD_CURRENTNESS',
    'CHILD_CURRENTNESS_IS_FIRST_CLASS_RECRUITMENT_ANCESTRY':'CHILD_CURRENTNESS_DROPPED',
    'ACTIVE_CHILD_DISCRIMINATION_CAN_REDUCE_COST_NE_TRUTH_AUTHORITY':'ACTIVE_DISCRIMINATION_GRANTED_TRUTH_AUTHORITY',
    'MORE_CHILD_EVIDENCE_NE_IDENTIFIABILITY_UNDER_OPERATIONAL_EQUIVALENCE':'EVIDENCE_VOLUME_LAUNDERED_AS_IDENTIFIABILITY',
    'REFUSAL_NE_ACTION_EFFECT':'REFUSAL_LAUNDERED_AS_ACTION_EFFECT',
    'LOCALLY_OPTIMAL_CHILD_COMMANDS_NE_JOINTLY_FEASIBLE_RECRUITMENT':'LOCAL_OPTIMA_LAUNDERED_AS_JOINT_FEASIBILITY',
    'DECENTRALIZED_FEASIBILITY_NE_PARENT_GOAL_AUTHORITY':'CHILD_FEASIBILITY_LAUNDERED_AS_PARENT_GOAL_AUTHORITY',
    'SCALAR_PARENT_PRESSURE_NE_VECTOR_HIERARCHICAL_VIABILITY':'SCALAR_PRESSURE_LAUNDERED_AS_VECTOR_VIABILITY',
    'RECURRENT_RECRUITMENT_NE_CAPABILITY_TRUTH_AUTHORITY':'RECURRENCE_GRANTED_CAPABILITY_TRUTH_AUTHORITY',
    'HIERARCHICAL_CAPABILITY_CURRENTNESS_IS_TRANSITIVE':'HIERARCHICAL_CURRENTNESS_NOT_TRANSITIVE',
    'INTENDED_CHILD_EFFECT_NE_OBSERVED_CHILD_EFFECT':'INTENT_LAUNDERED_AS_OBSERVATION',
    'GLOBAL_CHILD_MODEL_NE_CONTEXT_LOCAL_CHILD_CURRENTNESS':'GLOBAL_MODEL_ERASED_LOCAL_CURRENTNESS',
    'OPERATIONAL_CHILD_CORRESPONDENCE_NE_PERSISTENT_CHILD_IDENTITY':'CORRESPONDENCE_LAUNDERED_AS_CHILD_IDENTITY',
    'CHILD_GRAPH_ISOMORPHISM_NE_DEVELOPMENTAL_IDENTITY':'GRAPH_ISOMORPHISM_LAUNDERED_AS_IDENTITY',
    'ACTIVE_HIERARCHICAL_DISCRIMINATION_NE_IDENTITY_AUTHORITY':'ACTIVE_PROBE_GRANTED_IDENTITY_AUTHORITY',
    'INDIVIDUAL_HIERARCHY_MECHANISMS_NE_INTEGRATED_SUFFICIENCY':'ISOLATED_SUCCESS_LAUNDERED_AS_INTEGRATED_SUFFICIENCY',
    'SUPPLIED_RECRUITMENT_TOPOLOGY_NE_ENDOGENOUS_DEVELOPMENTAL_HIERARCHY':'SUPPLIED_TOPOLOGY_LAUNDERED_AS_ENDOGENOUS',
    'bounded_forward_recruitment_planner_remains_research_only':'RESEARCH_PLANNER_SELF_PROMOTED',
    'recruitment_proposal_is_model_output_not_truth_or_goal_authority':'RECRUITMENT_PROPOSAL_GRANTED_TRUTH_OR_GOAL_AUTHORITY',
    'recruitment_currentness_rechecks_child_and_value_epochs':'RECRUITMENT_CURRENTNESS_RECHECK_DROPPED',
    'typed_refusal_and_unknown_cannot_be_laundered_into_feasibility':'TYPED_FEASIBILITY_COLLAPSED',
    'joint_resource_conflict_must_survive_local_feasibility':'JOINT_RESOURCE_CONFLICT_DROPPED',
    'recruitment_topology_origin_must_remain_explicit_assistance_ancestry':'TOPOLOGY_ASSISTANCE_HIDDEN',
    'endogenous_topology_frontier_selection_is_cross_family_evidence_driven':'TOPOLOGY_WATERFALL_SELECTION',
}


def validate_v08(v02,v03,v04,v05,v06,v07,p):
    ok07, e07 = validate_v07(v02,v03,v04,v05,v06,v07)
    e=list(e07)
    if not ok07 and not e:
        e.append('V07_ANCESTRY_INVALID')
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.7':e.append('V08_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V08_CORE_METHOD_REPLACED')
    for k,err in V08_REQUIRED.items():
        if not p.get('refinements_from_ms978_1002',{}).get(k):e.append(err)
    lang=p.get('language_policy',{})
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=1002:e.append('WRONG_RESEARCH_TERMINAL')
    if ci.get('ms1003_started') is not False:e.append('HARD_STOP_MS1003_VIOLATED')
    if ci.get('selected_frontier')!='ATTN-MS1002-ENDOGENOUS-RECRUITMENT-TOPOLOGY__REACTIVATES_GRAND_P7_DEVELOPMENTAL_STRUCTURAL_GROWTH':e.append('WRONG_SELECTED_FRONTIER')
    if 'MS978_V07_NO_HIERARCHICAL_RECRUITMENT_PROPOSAL_CURRENTNESS_SUBSTRATE' not in ci.get('integration_debt_resolved',[]):e.append('RECRUITMENT_INTEGRATION_DEBT_DROPPED')
    for item in ('PERSISTENT_SELFHOOD_NOT_QUALIFIED','ENDOGENOUS_RECRUITMENT_TOPOLOGY','GENERAL_HIERARCHICAL_PLANNING','GENERAL_CHILD_ROLE_IDENTITY'):
        if item not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED:'+item)
    return not e,e


def hostile_mutants_v08(p):
    muts=[]
    x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core_method',x))
    for k in V08_REQUIRED:
        x=copy.deepcopy(p);x['refinements_from_ms978_1002'][k]=False;muts.append(('drop_'+k.lower(),x))
    x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';muts.append(('premature_language',x))
    x=copy.deepcopy(p);x['current_integration']['ms1003_started']=True;muts.append(('quiet_next_pass',x))
    x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_method_ancestry',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_resolved']=[];muts.append(('erase_resolved_integration_debt',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_open']=[];muts.append(('erase_open_frontiers',x))
    x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1003;muts.append(('lie_about_research_terminal',x))
    x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_HIERARCHY_HELIX_ONLY';muts.append(('replace_cross_family_frontier',x))
    return muts



V09_REQUIRED={
    'OBSERVATIONAL_COOCCURRENCE_NE_STRUCTURAL_CAUSAL_RELATION':'OBSERVATIONAL_COOCCURRENCE_LAUNDERED_AS_CAUSAL_STRUCTURE',
    'SPARSE_RELATION_CREATION_NE_NEW_COMPUTATIONAL_CLASS':'SPARSITY_LAUNDERED_AS_NEW_COMPUTATIONAL_CLASS',
    'TOPOLOGY_CURRENTNESS_IS_FIRST_CLASS_DEVELOPMENTAL_ANCESTRY':'TOPOLOGY_CURRENTNESS_DROPPED',
    'TRANSIENT_SYNERGY_PERTURBATION_NE_DEVELOPMENTAL_TOPOLOGY_CHANGE':'TRANSIENT_PERTURBATION_LAUNDERED_AS_DEVELOPMENTAL_REWRITE',
    'GLOBAL_TOPOLOGY_NE_CONTEXT_LOCAL_TOPOLOGY_CURRENTNESS':'GLOBAL_TOPOLOGY_ERASED_LOCAL_CURRENTNESS',
    'RECURRENT_TOPOLOGY_NE_TOPOLOGY_TRUTH_AUTHORITY':'RECURRENCE_GRANTED_TOPOLOGY_TRUTH_AUTHORITY',
    'TOPOLOGY_RELATION_NE_FEASIBILITY_RESOURCE_AUTHORITY':'TOPOLOGY_GRANTED_FEASIBILITY_OR_RESOURCE_AUTHORITY',
    'STRUCTURAL_SEARCH_COMPRESSION_NE_PHYSICAL_EXECUTION_COMPRESSION':'SEARCH_COMPRESSION_LAUNDERED_AS_EXECUTION_COMPRESSION',
    'SAME_TERMINAL_TOPOLOGY_NE_SAME_DEVELOPMENTAL_BIOGRAPHY':'TERMINAL_TOPOLOGY_LAUNDERED_AS_SAME_BIOGRAPHY',
    'TOPOLOGY_AUTOMORPHISM_NE_DEVELOPMENTAL_IDENTITY':'GRAPH_AUTOMORPHISM_LAUNDERED_AS_IDENTITY',
    'PAIRWISE_RELATION_LANGUAGE_NE_GENERAL_STRUCTURAL_GROWTH':'PAIRWISE_LANGUAGE_OVERPROMOTED_TO_GENERAL_STRUCTURAL_GROWTH',
    'IDENTIFIABILITY_NE_TRACTABLE_CONSTRUCTOR_SEARCH':'IDENTIFIABILITY_LAUNDERED_AS_TRACTABLE_SEARCH',
    'qualified_topology_requires_external_qualification':'TOPOLOGY_SELF_QUALIFICATION_ALLOWED',
    'topology_signature_is_content_bound':'TOPOLOGY_CONTENT_BINDING_DROPPED',
    'topology_constituent_drift_invalidates_bound_capability_closure':'TOPOLOGY_CONSTITUENT_DRIFT_NOT_TRANSITIVE',
    'pending_candidate_topology_currentness_required_at_admission':'PENDING_TOPOLOGY_CURRENTNESS_NOT_RECHECKED',
    'pairwise_topology_constructor_remains_research_only':'PAIRWISE_TOPOLOGY_CONSTRUCTOR_SELF_PROMOTED',
    'persistent_identity_frontier_selection_is_cross_family_evidence_driven':'IDENTITY_WATERFALL_SELECTION',
}


def validate_v09(v02,v03,v04,v05,v06,v07,v08,p):
    ok08,e08=validate_v08(v02,v03,v04,v05,v06,v07,v08)
    e=list(e08)
    if not ok08 and not e:e.append('V08_ANCESTRY_INVALID')
    if p.get('inherits')!='microseed.maindev-operating-profile.v0.8':e.append('V09_ANCESTRY_LOST')
    if p.get('core_shape_unchanged') is not True:e.append('V09_CORE_METHOD_REPLACED')
    for k,err in V09_REQUIRED.items():
        if not p.get('refinements_from_ms1003_1027',{}).get(k):e.append(err)
    lang=p.get('language_policy',{})
    if lang.get('active_phase')!='PRELINGUAL' or lang.get('cognitive_substrate')!='DEFERRED':e.append('LANGUAGE_PREMATURELY_ADMITTED')
    ci=p.get('current_integration',{})
    if ci.get('research_terminal_ms')!=1027:e.append('WRONG_RESEARCH_TERMINAL')
    if ci.get('ms1028_started') is not False:e.append('HARD_STOP_MS1028_VIOLATED')
    if ci.get('selected_frontier')!='ATTN-MS1027-STRUCTURAL-REWRITE-DEVELOPMENTAL-IDENTITY__REACTIVATES_PERSISTENT_IDENTITY_UNDER_STRUCTURAL_REWRITE':e.append('WRONG_SELECTED_FRONTIER')
    if 'MS1003_V08_NO_FIRST_CLASS_OPERATIONAL_TOPOLOGY_CURRENTNESS_CONTRACT' not in ci.get('integration_debt_resolved',[]):e.append('TOPOLOGY_INTEGRATION_DEBT_DROPPED')
    for item in ('PERSISTENT_SELFHOOD_NOT_QUALIFIED','DEVELOPMENTAL_IDENTITY_UNDER_STRUCTURAL_REWRITE','GENERAL_HIGHER_ORDER_TOPOLOGY_CONSTRUCTOR_LANGUAGE','TRACTABLE_ENDOGENOUS_TOPOLOGY_SEARCH'):
        if item not in ci.get('integration_debt_open',[]):e.append('OPEN_FRONTIER_DROPPED:'+item)
    return not e,e


def hostile_mutants_v09(p):
    muts=[]
    x=copy.deepcopy(p);x['core_shape_unchanged']=False;muts.append(('replace_core_method',x))
    for k in V09_REQUIRED:
        x=copy.deepcopy(p);x['refinements_from_ms1003_1027'][k]=False;muts.append(('drop_'+k.lower(),x))
    x=copy.deepcopy(p);x['language_policy']['cognitive_substrate']='ACTIVE';muts.append(('premature_language',x))
    x=copy.deepcopy(p);x['current_integration']['ms1028_started']=True;muts.append(('quiet_next_pass',x))
    x=copy.deepcopy(p);x['inherits']='NONE';muts.append(('drop_method_ancestry',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_resolved']=[];muts.append(('erase_resolved_integration_debt',x))
    x=copy.deepcopy(p);x['current_integration']['integration_debt_open']=[];muts.append(('erase_open_frontiers',x))
    x=copy.deepcopy(p);x['current_integration']['research_terminal_ms']=1028;muts.append(('lie_about_research_terminal',x))
    x=copy.deepcopy(p);x['current_integration']['selected_frontier']='LOCAL_TOPOLOGY_HELIX_ONLY';muts.append(('replace_cross_family_frontier',x))
    return muts


def main():
    v02=json.loads(P02.read_text());v03=json.loads(P03.read_text());v04=json.loads(P04.read_text());v05=json.loads(P05.read_text());v06=json.loads(P06.read_text());v07=json.loads(P07.read_text());v08=json.loads(P08.read_text());p=json.loads(PROFILE.read_text())
    ok,errs=validate_v09(v02,v03,v04,v05,v06,v07,v08,p);rej=[];esc=[]
    for name,m in hostile_mutants_v09(p):
        mok,merr=validate_v09(v02,v03,v04,v05,v06,v07,v08,m)
        if mok:esc.append(name)
        else:rej.append({'mutant':name,'errors':merr})
    out={
        'schema':'microseed.maindev-operating-profile-validation.v0.9',
        'baseline_pass':ok,'baseline_errors':errs,
        'hostile_mutants':len(rej)+len(esc),'hostile_mutants_rejected':len(rej),
        'escaped':esc,'all_pass':ok and not esc,
    }
    print(json.dumps(out,indent=2,sort_keys=True));return 0 if out['all_pass'] else 1

if __name__=='__main__': raise SystemExit(main())
