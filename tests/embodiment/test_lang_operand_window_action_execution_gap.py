from scratch.lang_operand_window_action_execution_gap import run_gap

def test_historical_action_execution_boundary_gap_is_now_embodied_but_negative_commit_remains_recovery_anchor():
    r=run_gap()
    assert r['status']=='CURRENT_ACTION_EXECUTION_BOUNDARY_OWNER_PRESENT'
    assert r['historical_negative_commit']=='eca0d36b64bbf07683d927b572e723007dfdbed7'
    assert r['action_outcome_recorded']=='NO'
    assert r['historical_evidence_only_derived_arity']==4
    assert r['current_generalized_derived_arity']==r['expected_post_execution_window_arity']==2
    assert r['localized_missing_mechanism']=='CROSS_PLANE_TOKEN_EVIDENCE_TO_DURABLE_ACTION_EXECUTION_WINDOW_OWNER'
    assert r['caller_supplied_boundary_marker']=='NO'
    assert r['execution_authority_gain_from_boundary_use']==r['semantic_grouping_authority']=='NONE'
