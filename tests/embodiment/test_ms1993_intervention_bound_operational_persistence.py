from scratch.ms1993_intervention_bound_operational_persistence import run_ms1993


def test_ms1993_intervention_trace_supports_operational_persistence_without_identity_promotion():
    result=run_ms1993()
    assert result['status']=='BOUNDARY_CONFIRMED'
    assert result['new_core_mechanism_required']=='NO'
    assert result['persistent']['trace_retained'] is True
    assert result['persistent']['evaluator_persistence'] is True
    assert result['unmarked_replacement']['trace_retained'] is False
    assert result['unmarked_replacement']['evaluator_persistence'] is False
    assert result['perfect_copy_replacement']['trace_retained'] is True
    assert result['perfect_copy_replacement']['evaluator_persistence'] is False
    assert result['persistent']['target_signature']==result['unmarked_replacement']['target_signature']==result['perfect_copy_replacement']['target_signature']
    assert result['persistent']['target_group']==result['unmarked_replacement']['target_group']==result['perfect_copy_replacement']['target_group']==[0,1]
    assert result['operational_persistence_authority']=='TRACE_RELATIVE_ONLY'
    assert result['numerical_identity_authority']=='NONE'
    assert result['semantic_reference_authority']=='NONE'
    assert result['language_authority']=='NONE'
    assert result['remaining_boundary']=='PERFECT_COPY_WITH_RETAINED_TRACE_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE'
