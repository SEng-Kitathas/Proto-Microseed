from scratch.lang_recursive_composition_operand_owner_gap_audit import run_audit


def test_b2_composition_evidence_has_producer_but_no_recursive_operand_consumer():
    r=run_audit()
    assert r['status']=='STOP_RECURSIVE_COMPOSITION_OPERAND_OWNER_MISSING'
    assert r['production_b2_producers']==(
        'def derive_and_record_current_native_b2_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
    )
    assert r['production_b2_consumers']==()
    assert r['production_methods_mentioning_exact_b2_kind']==r['production_b2_producers']
    assert r['localized_missing_mechanism']=='CURRENT_COMPOSITION_AS_GROUNDED_OPERAND_CARRIER_AND_CURRENTNESS_OWNER'
    assert r['b2_systematicity']=='EARNED_BOUNDED'
    assert r['recursive_composition_as_operand']==r['arity_generalization']=='NOT_EARNED'
    assert r['new_planner_required']=='NO_EVIDENCE_FOR_NEW_PLANNER'
    assert r['semantic_authority']==r['grammar_authority']==r['truth_authority']==r['execution_authority']=='NONE'
