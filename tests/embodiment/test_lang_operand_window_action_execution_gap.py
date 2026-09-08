from scratch.lang_operand_window_action_execution_gap import run_gap

def test_bare_owned_action_execution_is_invisible_to_current_evidence_only_operand_window():
    r=run_gap()
    assert r['status']=='STOP_EVIDENCE_ONLY_WINDOW_MISSES_OWNED_ACTION_EXECUTION_BOUNDARY'
    assert r['action_outcome_recorded']=='NO'
    assert r['current_generalized_derived_arity']==4
    assert r['expected_post_execution_window_arity_if_execution_is_boundary']==2
    assert r['localized_missing_mechanism']=='CROSS_PLANE_TOKEN_EVIDENCE_TO_DURABLE_ACTION_EXECUTION_WINDOW_OWNER'
    assert r['caller_supplied_boundary_marker']=='NO'
    assert r['execution_authority_gain_from_boundary_use']==r['semantic_grouping_authority']=='NONE'
