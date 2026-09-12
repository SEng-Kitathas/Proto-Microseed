import inspect
from microseed import Microseed
from scratch.lang_segment_depth_five_parent_prototype import derive_current_depth_five_segment_parent_prototype
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent
from tests.embodiment.test_lang_segment_depth_four_parent_production import _depth_four


def _depth_four_then_external(m,base=520000):
    p1,p2,d2,p3,d3,p4,d4=_depth_four(m,base)
    p5=_mixed_parent(m,(3,2),base+4000)[2]
    return p1,p2,d2,p3,d3,p4,d4,p5


def test_depth_five_prototype_preserves_depth_four_parent_and_external_depth_one():
    td,m,world,seeded=_setup('SEGMENT-DEPTH5-PROT')
    try:
        *xs,d4,p5=_depth_four_then_external(m)
        out=derive_current_depth_five_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_PROTOTYPE',out
        assert out['composition_depth']==5 and out['max_input_parent_depth']==4 and sorted(out['ordered_child_composition_depths'])==[1,4]
        d4c=next(c for c in out['children'] if c['composition_depth']==4);d1c=next(c for c in out['children'] if c['composition_depth']==1)
        assert d4c['composition_content_digest_sha256']==d4['composition_content_digest_sha256']
        assert d1c['composition_content_digest_sha256']==p5['composition_content_digest_sha256']
        assert p5['composition_content_digest_sha256'] not in d4c['full_ancestry_content_digests']
        assert out['generic_recursive_closure_authority']==out['depth_six_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_depth_five_prototype_requires_external_parent_outside_full_depth_four_ancestry():
    td,m,world,seeded=_setup('SEGMENT-DEPTH5-ANCESTRY')
    try:
        _depth_four(m,525000)
        out=derive_current_depth_five_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_FOUR_ANCESTRY_REQUIRED',out
    finally:_close(m);td.cleanup()


def test_depth_five_prototype_evidence_order_is_owned():
    td,m,world,seeded=_setup('SEGMENT-DEPTH5-ORDER')
    try:
        _b2_parent(m,530000);_mixed_parent(m,(3,4),531000);m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        _mixed_parent(m,(4,2),532000);m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        early=_mixed_parent(m,(2,3),533000)[2];latest=_mixed_parent(m,(3,2),534000)[2]
        d4=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        out=derive_current_depth_five_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_PROTOTYPE',out
        assert out['ordered_child_composition_depths']==(1,4),out
        assert out['ordered_child_composition_content_digests'][0]==early['composition_content_digest_sha256']
        assert out['ordered_child_composition_content_digests'][1]==d4['composition_content_digest_sha256']
        assert latest['composition_content_digest_sha256'] in next(c for c in out['children'] if c['composition_depth']==4)['full_ancestry_content_digests']
    finally:_close(m);td.cleanup()


def test_depth_five_prototype_nested_currentness_drift_fails_closed():
    td,m,world,seeded=_setup('SEGMENT-DEPTH5-DRIFT')
    try:
        _depth_four_then_external(m,535000);m.change_capability_dependency('QA',reason='SEGMENT-DEPTH5-QA-DRIFT')
        out=derive_current_depth_five_segment_parent_prototype(m,max_records=65536);assert out['status']=='DEFER_UNKNOWN',out
    finally:_close(m);td.cleanup()


def test_depth_five_prototype_does_not_widen_depth_four_owner_or_claim_closure():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_four_recursive_composition)
    accepted=src[src.index('accepted_depth_one={'):src.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE' not in accepted
    proto=inspect.getsource(derive_current_depth_five_segment_parent_prototype)
    assert 'generic_recursive_closure_authority' in proto and 'depth_six_authority' in proto
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_RECURSIVE_COMPOSITION_STATE' not in proto
