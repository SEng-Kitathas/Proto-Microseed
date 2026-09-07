from scratch.lang_recursive_composition_operand_owner_gap_audit import run_audit


def test_b2_composition_evidence_has_producer_but_no_recursive_operand_consumer():
    r=run_audit()
    assert r['status']=='CURRENT_RECURSIVE_COMPOSITION_OPERAND_OWNER_PRESENT'
    assert r['production_b2_producers']==(
        'def derive_and_record_current_native_b2_ordered_composition(self, *, max_records: int = 4096) -> dict[str, Any]:',
    )
    assert r['production_b2_consumers']==('def derive_and_record_current_native_recursive_b2_ordered_composition(',)
    assert set(r['production_methods_mentioning_exact_b2_kind'])==set(r['production_b2_producers']+r['production_b2_consumers'])
    assert r['historically_localized_missing_mechanism']=='CURRENT_COMPOSITION_AS_GROUNDED_OPERAND_CARRIER_AND_CURRENTNESS_OWNER'
    assert r['bridge_now_embodied']=='YES_FIXED_DEPTH_ONE_ONLY'
    assert r['b2_systematicity']=='EARNED_BOUNDED'
    assert r['recursive_composition_as_operand']=='EARNED_BOUNDED_DEPTH_ONE'
    assert r['arity_generalization']=='NOT_EARNED'
    assert r['new_planner_required']=='NO_EVIDENCE_FOR_NEW_PLANNER'
    assert r['semantic_authority']==r['grammar_authority']==r['truth_authority']==r['execution_authority']=='NONE'
