import inspect

from microseed import Microseed
from scratch.lang_segment_depth_four_parent_prototype import derive_current_depth_four_segment_parent_prototype
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _mixed_parent
from tests.embodiment.test_lang_segment_depth_three_parent_production import _depth_three


def _depth_three_then_external(m,base=450000):
    p1,p2,d2,p3,d3=_depth_three(m,base)
    p4=_mixed_parent(m,(2,4),base+3000)[2]
    return p1,p2,d2,p3,d3,p4


def test_depth_four_prototype_preserves_depth_three_parent_and_external_depth_one():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-PROT')
    try:
        p1,p2,d2,p3,d3,p4=_depth_three_then_external(m)
        out=derive_current_depth_four_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_PROTOTYPE',out
        assert out['composition_depth']==4 and out['child_arity']==2 and out['max_input_parent_depth']==3
        assert sorted(out['ordered_child_composition_depths'])==[1,3]
        d3c=next(c for c in out['children'] if c['composition_depth']==3)
        d1c=next(c for c in out['children'] if c['composition_depth']==1)
        assert d3c['composition_content_digest_sha256']==d3['composition_content_digest_sha256']
        assert d1c['composition_content_digest_sha256']==p4['composition_content_digest_sha256']
        assert p4['composition_content_digest_sha256'] not in d3c['full_ancestry_content_digests']
        assert out['generic_recursive_closure_authority']==out['depth_five_authority']=='NONE'
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_depth_four_prototype_requires_external_parent_outside_full_depth_three_ancestry():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-ANCESTRY')
    try:
        _depth_three(m,454000)
        out=derive_current_depth_four_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_THREE_ANCESTRY_REQUIRED'
    finally:_close(m);td.cleanup()


def test_depth_four_prototype_evidence_order_is_owned_by_evidence():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-ORDER')
    try:
        # Two external parents before depth-three: depth-three consumes latest, leaving earlier one outside ancestry.
        from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent
        _b2_parent(m,458000);_mixed_parent(m,(3,4),459000)
        d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        early=_mixed_parent(m,(4,2),460000)[2]
        latest=_mixed_parent(m,(2,3),461000)[2]
        d3=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        out=derive_current_depth_four_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_PROTOTYPE',out
        assert out['ordered_child_composition_depths']==(1,3),out
        assert out['ordered_child_composition_content_digests'][0]==early['composition_content_digest_sha256']
        assert out['ordered_child_composition_content_digests'][1]==d3['composition_content_digest_sha256']
        assert latest['composition_content_digest_sha256'] in next(c for c in out['children'] if c['composition_depth']==3)['full_ancestry_content_digests']
    finally:_close(m);td.cleanup()


def test_depth_four_prototype_nested_currentness_drift_fails_closed():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-DRIFT')
    try:
        _depth_three_then_external(m,462000)
        m.change_capability_dependency('QA',reason='SEGMENT-DEPTH4-QA-DRIFT')
        out=derive_current_depth_four_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
    finally:_close(m);td.cleanup()


def test_depth_four_prototype_does_not_widen_depth_three_owner_or_claim_closure():
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_three_recursive_composition)
    accepted=src[src.index('accepted_depth_one={'):src.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE' not in accepted
    proto=inspect.getsource(derive_current_depth_four_segment_parent_prototype)
    assert 'generic_recursive_closure_authority' in proto and 'depth_five_authority' in proto
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE' not in proto
