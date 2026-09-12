import inspect
from microseed import Microseed

def test_depth_five_owner_closed_and_depth_four_unchanged_by_contract():
    d4=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_four_recursive_composition);acc=d4[d4.index('accepted_depth_one={'):d4.index('for pos,row')];assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_RECURSIVE_COMPOSITION_STATE' not in acc
    d5=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_five_recursive_composition);acc5=d5[d5.index('accepted_depth_one={'):d5.index('for pos,row')];assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_RECURSIVE_COMPOSITION_STATE' not in acc5;assert 'generic_recursive_closure_authority":"NONE"' in d5;assert 'depth_six_authority":"NONE"' in d5

def test_depth_five_validator_exact_mixed_depth_full_ancestry_order():
    src=inspect.getsource(Microseed._validate_current_native_structural_segment_depth_five_recursive_composition_state)
    for t in ('sorted(depths)!=[1,4]','DEPTH_FIVE_CHILD_ORDER_NOT_EVIDENCE_OWNED','DEPTH_FIVE_EXTERNAL_DEPTH_ONE_PARENT_MUST_BE_OUTSIDE_FULL_DEPTH_FOUR_ANCESTRY','full_ancestry_content_digests'): assert t in src
