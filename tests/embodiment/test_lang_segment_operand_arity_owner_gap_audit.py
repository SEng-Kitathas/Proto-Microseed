import inspect

from microseed import Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close


def test_current_owner_gap_is_internal_child_arity_hardcode_not_missing_bounded_content_or_parent_law():
    bounded=inspect.getsource(Microseed.derive_and_record_current_native_bounded_ordered_composition)
    segment_content=inspect.getsource(Microseed._native_structural_segment_state_content_from_boundary)
    child=inspect.getsource(Microseed._native_structural_segment_b2_child_carriers)
    parent=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition)
    assert 'min_arity=2; max_arity=4' in bounded
    assert '"arity":split' in segment_content and '"arity":len(sigs)-split' in segment_content
    assert 'int(content.get("arity",-1))!=2' in child
    assert '"composition_depth":1,"child_arity":2' in parent
    assert 'ordered_child_composition_content_digests' in parent
    # Parent child_arity is grouped child count, not each child's leaf arity.
    assert 'ordered_operational_referent_signatures' not in parent[parent.index('content={'):parent.index('parent_digest=')]


def test_current_production_b2_only_consumer_refuses_known_lawful_2_plus_3_segment_state():
    td,m,world,seeded=_setup('SEGMENT-ARITY-P01-GAP')
    try:
        b=_boundary(m,('R4','T9','R4','W3','K7'),210000)
        assert b['split_index']==2,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert s['left_content']['arity']==2 and s['right_content']['arity']==3
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED',out
        assert out['skipped'][0]['reason']=='SEGMENT_STATE_SIDE_NOT_B2_COMPATIBLE_FOR_RECURSIVE_REUSE'
        assert out['skipped'][0]['side']=='RIGHT' and out['skipped'][0]['side_arity']==3
    finally:_close(m);td.cleanup()
