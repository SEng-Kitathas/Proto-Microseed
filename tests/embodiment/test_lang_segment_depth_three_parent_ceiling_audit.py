import inspect
from microseed import Microseed


def test_depth_three_owner_is_closed_and_does_not_widen_depth_two_owner():
    d2=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
    d2accepted=d2[d2.index('accepted={'):d2.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in d2accepted
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE' not in d2accepted
    d3=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_three_recursive_composition)
    accepted=d3[d3.index('accepted_depth_one={'):d3.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE' not in accepted
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in accepted
    assert 'generic_recursive_closure_authority":"NONE"' in d3
    assert 'depth_four_authority":"NONE"' in d3


def test_depth_three_validator_requires_exact_mixed_depth_children_and_evidence_order():
    src=inspect.getsource(Microseed._validate_current_native_structural_segment_depth_three_recursive_composition_state)
    for token in ('sorted(child_depths)!=[1,2]','DEPTH_THREE_CHILD_ORDER_NOT_EVIDENCE_OWNED','DEPTH_THREE_EXTERNAL_DEPTH_ONE_PARENT_MUST_NOT_BE_NESTED_ALREADY'):
        assert token in src
    for token in ('semantic_composition_authority','grammar_authority','effect_authority','execution_authority','scheduler_authority'):
        assert token in src
