from scratch.lang_arity_generalization_caller_selection_gap import run_audit


def test_same_three_current_grounded_leaves_have_no_organism_owned_arity_choice():
    r=run_audit()
    assert r['status']=='STOP_ARITY_CURRENTLY_CALLER_SELECTED_BY_METHOD'
    assert r['b2_result_arity']==2 and r['b3_result_arity']==3
    assert r['caller_method_choice_changes_arity']=='YES'
    assert r['organism_owned_arity_carrier']=='ABSENT'
    assert r['localized_missing_mechanism']=='ORGANISM_OWNED_BOUNDED_OPERAND_WINDOW_OR_ARITY_CARRIER'
    assert r['generic_nary']=='NOT_EARNED'
    assert r['semantic_authority']==r['execution_authority']=='NONE'
