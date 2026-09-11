import inspect

from microseed import Microseed
from scratch.lang_segment_depth_three_parent_prototype import derive_current_depth_three_segment_parent_prototype
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent


def _depth_two_then_external(m,base=410000):
    p1=_b2_parent(m,base)[2]
    p2=_mixed_parent(m,(3,4),base+1000)[2]
    d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
    assert d2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',d2
    p3=_mixed_parent(m,(4,2),base+2000)[2]
    return p1,p2,d2,p3


def test_depth_three_prototype_requires_depth_two_plus_external_depth_one_and_preserves_nesting():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-PROT')
    try:
        p1,p2,d2,p3=_depth_two_then_external(m)
        out=derive_current_depth_three_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_PROTOTYPE',out
        assert out['composition_depth']==3 and out['child_arity']==2 and out['max_input_parent_depth']==2
        assert sorted(out['ordered_child_composition_depths'])==[1,2]
        d2_child=next(c for c in out['children'] if c['composition_depth']==2)
        d1_child=next(c for c in out['children'] if c['composition_depth']==1)
        assert d2_child['composition_content_digest_sha256']==d2['composition_content_digest_sha256']
        assert tuple(d2_child['nested_child_content_digests'])==d2['ordered_child_composition_content_digests']
        assert d1_child['composition_content_digest_sha256']==p3['composition_content_digest_sha256']
        assert p3['composition_content_digest_sha256'] not in d2['ordered_child_composition_content_digests']
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
        assert out['generic_recursive_closure_authority']==out['depth_four_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_depth_three_prototype_defers_without_external_parent_instead_of_reusing_nested_child():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-NO-EXTERNAL')
    try:
        _b2_parent(m,412000);_mixed_parent(m,(3,4),413000)
        d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert d2['status'].startswith('CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO')
        out=derive_current_depth_three_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_REQUIRED',out
    finally:_close(m);td.cleanup()


def test_depth_three_prototype_child_order_is_evidence_owned_not_caller_supplied():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-ORDER')
    try:
        early=_b2_parent(m,414000)[2]
        p2=_mixed_parent(m,(3,4),415000)[2]
        p3=_mixed_parent(m,(4,2),416000)[2]
        d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        # depth-two uses p2+p3, leaving early as the external parent before the depth-two state in evidence order.
        out=derive_current_depth_three_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_PROTOTYPE',out
        assert out['ordered_child_composition_depths']==(1,2),out
        assert out['ordered_child_composition_content_digests'][0]==early['composition_content_digest_sha256']
        assert out['ordered_child_composition_content_digests'][1]==d2['composition_content_digest_sha256']
        assert out['caller_supplied_parent_order']=='NO' and out['caller_supplied_grouping']=='NO'
    finally:_close(m);td.cleanup()


def test_depth_three_prototype_nested_currentness_drift_fails_closed():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-DRIFT')
    try:
        _depth_two_then_external(m,417000)
        m.change_capability_dependency('QA',reason='SEGMENT-DEPTH3-QA-DRIFT')
        out=derive_current_depth_three_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
    finally:_close(m);td.cleanup()


def test_depth_three_prototype_does_not_widen_depth_two_owner_or_claim_recursive_closure():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
    accepted=src[src.index('accepted={'):src.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in accepted
    proto=inspect.getsource(derive_current_depth_three_segment_parent_prototype)
    assert 'generic_recursive_closure_authority' in proto and 'depth_four_authority' in proto
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE' not in proto
