from scratch.lang_active_acquisition_owner_composition_audit import run_campaign


def test_active_acquisition_localizes_missing_binding_between_existing_selection_and_association_evidence_owners():
    r=run_campaign()
    assert r['status']=='STOP_ACTIVE_ACQUISITION_OWNER_BINDING_MISSING'
    assert r['existing_selection_owner']=='CURRENT_UNIQUE_OWNED_REFERENT_EPISTEMIC_OPPORTUNITY'
    assert r['existing_selected_probe_action_id']=='P2'
    assert r['caller_selected_binding_or_deficit']=='NO'
    assert r['action_generated_grounded_evidence_kind']=='OWNED_AFFORDANCE_EFFECT_PROFILE_WITNESS'
    assert r['c08i_pair_harvest_from_action_generated_grounded_evidence']=='NO'
    assert r['pair_witness_delta']==0
    assert r['association_to_opportunity_coupled_methods']==[]
    assert r['localized_missing_mechanism']=='NATIVE_ASSOCIATION_PRESSURE_TO_CURRENT_GROUNDED_ACQUISITION_OPPORTUNITY_BINDING'
    assert r['new_planner_required']=='NO_EVIDENCE_FOR_NEW_PLANNER'
    assert r['information_value_effect_authority_conflated']=='NO'
    assert r['effect_authority']==r['execution_authority']=='NONE'
