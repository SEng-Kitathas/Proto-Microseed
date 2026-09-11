import inspect
from microseed import Microseed


def test_depth_four_owner_is_closed_and_does_not_widen_depth_three_owner():
    d3=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_three_recursive_composition)
    accepted=d3[d3.index('accepted_depth_one={'):d3.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE' not in accepted
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE' not in accepted
    d4=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_four_recursive_composition)
    accepted4=d4[d4.index('accepted_depth_one={'):d4.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE' not in accepted4
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE' not in accepted4
    assert 'generic_recursive_closure_authority":"NONE"' in d4
    assert 'depth_five_authority":"NONE"' in d4


def test_depth_four_validator_requires_exact_mixed_depth_children_full_ancestry_and_order():
    src=inspect.getsource(Microseed._validate_current_native_structural_segment_depth_four_recursive_composition_state)
    for token in ('sorted(child_depths)!=[1,3]','DEPTH_FOUR_CHILD_ORDER_NOT_EVIDENCE_OWNED','DEPTH_FOUR_EXTERNAL_DEPTH_ONE_PARENT_MUST_BE_OUTSIDE_FULL_DEPTH_THREE_ANCESTRY','full_ancestry_content_digests'):
        assert token in src
    for token in ('semantic_composition_authority','grammar_authority','effect_authority','execution_authority','scheduler_authority'):
        assert token in src
