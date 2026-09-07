from scratch.lang_systematic_recombination_owner_gap_audit import run_audit


def test_c08g_rule_exists_only_in_research_helper_not_microseed_owner():
    r=run_audit()
    assert r['status']=='STOP_SYSTEMATIC_RECOMBINATION_OWNER_MISSING'
    assert r['c08g_order_sensitive'] is True
    assert r['production_owned_composition_methods']==[]
    assert r['localized_missing_mechanism']=='MICROSEED_OWNED_BOUNDED_ORDERED_COMPOSITION_OPERATOR'
    assert r['new_planner_required']=='NO'
    assert r['grammar_authority']==r['semantic_authority']==r['truth_authority']==r['execution_authority']=='NONE'
