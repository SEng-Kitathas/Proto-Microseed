import inspect

from microseed import Microseed
from scratch.lang_segment_parent_operand_prototype import (
    derive_current_depth_one_segment_parent_child_carriers,
    derive_current_depth_two_segment_parent_prototype,
)
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close
from tests.embodiment.test_lang_segment_operand_bounded_arity_production import MIXED_SHAPES


def _b2_parent(m,base,seq=('R4','T9','R4','K7')):
    b=_boundary(m,seq,base); assert b['split_index']==2,b
    s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
    p=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',p
    return b,s,p


def _mixed_parent(m,shape,base):
    seq=MIXED_SHAPES[shape]
    b=_boundary(m,seq,base); assert (b['split_index'],len(seq)-b['split_index'])==shape,b
    s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
    p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
    return b,s,p


def test_p01_owner_gap_is_closed_only_by_explicit_depth_two_owner_without_widening_prior_owners():
    new_src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
    validator_src=inspect.getsource(Microseed._validate_current_native_structural_segment_depth_two_recursive_composition_state)
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' in new_src
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' in validator_src
    accepted_block=new_src[new_src.index('accepted={'):new_src.index('for pos,row')]
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE' in accepted_block
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE' in accepted_block
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in accepted_block
    for prior in (
        Microseed.derive_and_record_current_native_recursive_b2_ordered_composition,
        Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition,
        Microseed.derive_and_record_current_native_structural_segment_bounded_recursive_composition,
    ):
        prior_src=inspect.getsource(prior)
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in prior_src
        assert 'derive_and_record_current_native_structural_segment_depth_two_recursive_composition' not in prior_src
    td,m,world,seeded=_setup('SEGMENT-PARENT-P01-TRANSITION')
    try:
        _b2_parent(m,300000)
        _mixed_parent(m,(3,4),301000)
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        historical=m.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=65536)
        assert historical['status']=='DEFER_UNKNOWN',historical
        assert historical['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED'
        assert historical['current_distinct_child_count']==0
        assert out['generic_recursive_closure_authority']==out['depth_three_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_b2_then_mixed_parents_form_read_only_exact_depth_two_nested_content():
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROTOTYPE-B2-MIXED')
    try:
        _b1,_s1,p1=_b2_parent(m,302000)
        _b2,_s2,p2=_mixed_parent(m,(3,4),303000)
        before=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        out=derive_current_depth_two_segment_parent_prototype(m,max_records=65536)
        after=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        assert out['status']=='CURRENT_DEPTH_TWO_SEGMENT_PARENT_PROTOTYPE_DERIVED',out
        assert out['composition_depth']==2 and out['child_arity']==2
        assert out['ordered_child_composition_content_digests']==(p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'])
        assert tuple(c['source_parent_kind'] for c in out['children'])==(
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE',
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE')
        assert tuple(c['composition_depth'] for c in out['children'])==(1,1)
        assert tuple(len(c['nested_children']) for c in out['children'])==(2,2)
        assert before==after
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
        assert out['generic_recursive_closure_authority']==out['depth_three_authority']=='NONE'
    finally:_close(m);td.cleanup()


def _ordered_parent_digest(order):
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROTOTYPE-ORDER-'+order)
    try:
        if order=='B2_MIXED':
            _b2_parent(m,304000); _mixed_parent(m,(2,4),305000)
        else:
            _mixed_parent(m,(2,4),304000); _b2_parent(m,305000)
        out=derive_current_depth_two_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_DEPTH_TWO_SEGMENT_PARENT_PROTOTYPE_DERIVED',out
        return out['composition_content_digest_sha256'],out['ordered_child_composition_content_digests'],tuple(c['source_parent_kind'] for c in out['children'])
    finally:_close(m);td.cleanup()


def test_depth_two_parent_order_is_evidence_owned_and_noncommutative():
    a=_ordered_parent_digest('B2_MIXED'); b=_ordered_parent_digest('MIXED_B2')
    assert a[1]==tuple(reversed(b[1]))
    assert a[2]==tuple(reversed(b[2]))
    assert a[0]!=b[0]


def test_two_distinct_mixed_parents_form_two_nested_depth_one_children():
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROTOTYPE-MIXED-MIXED')
    try:
        _mixed_parent(m,(2,3),306000)
        _mixed_parent(m,(4,2),307000)
        out=derive_current_depth_two_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='CURRENT_DEPTH_TWO_SEGMENT_PARENT_PROTOTYPE_DERIVED',out
        assert out['composition_depth']==2 and out['child_arity']==2
        assert tuple(c['source_parent_kind'] for c in out['children'])==(
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE',
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE')
        assert tuple(c['composition_depth'] for c in out['children'])==(1,1)
        assert all(len(c['nested_child_content_digests'])==2 for c in out['children'])
    finally:_close(m);td.cleanup()


def test_duplicate_depth_one_parent_content_does_not_manufacture_two_deeper_operands():
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROTOTYPE-DUP')
    try:
        _b2_parent(m,308000)
        _b2_parent(m,309000)
        carriers=derive_current_depth_one_segment_parent_child_carriers(m,max_records=65536)
        assert carriers['status']=='CURRENT_DEPTH_ONE_SEGMENT_PARENT_CHILD_CARRIERS_DERIVED',carriers
        assert carriers['carrier_count']==2
        assert carriers['carriers'][0]['composition_content_digest_sha256']==carriers['carriers'][1]['composition_content_digest_sha256']
        out=derive_current_depth_two_segment_parent_prototype(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='TWO_DISTINCT_CURRENT_DEPTH_ONE_SEGMENT_PARENT_CONTENTS_REQUIRED'
        assert out['current_distinct_parent_count']==1
    finally:_close(m);td.cleanup()
