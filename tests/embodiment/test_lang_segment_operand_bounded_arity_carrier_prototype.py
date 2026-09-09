import pytest

from scratch.lang_segment_operand_bounded_arity_carrier_prototype import (
    derive_current_bounded_structural_segment_child_carriers,
    derive_current_bounded_structural_segment_recursive_parent_prototypes,
)
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_direct_digest,_close

SHAPES={
    (2,2):('R4','T9','R4','K7'),
    (2,3):('R4','T9','R4','W3','K7'),
    (3,2):('R4','T9','W3','K7','W3'),
    (3,3):('R4','T9','W3','R4','W3','T9'),
    (2,4):('R4','T9','R4','W3','K7','T9'),
    (4,2):('R4','T9','W3','K7','W3','K7'),
    (3,4):('R4','T9','W3','R4','T9','W3','K7'),
    (4,3):('R4','T9','W3','K7','R4','K7','T9'),
    (4,4):('R4','T9','W3','K7','R4','T9','K7','W3'),
}

@pytest.mark.parametrize('shape',tuple(SHAPES))
def test_every_bounded_segment_shape_derives_split_endogenously_and_side_content_matches_existing_direct_bounded_law(shape):
    seq=SHAPES[shape]; split=shape[0]
    left_direct,left_sigs=_direct_digest(seq[:split],220000+10*split+len(seq))
    right_direct,right_sigs=_direct_digest(seq[split:],221000+10*split+len(seq))
    td,m,world,seeded=_setup('SEGMENT-ARITY-CARRIER-'+str(shape))
    try:
        b=_boundary(m,seq,222000+100*split+len(seq))
        assert (b['split_index'],len(seq)-b['split_index'])==shape,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        before=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        out=derive_current_bounded_structural_segment_child_carriers(m,max_records=65536)
        after=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        assert out['status']=='CURRENT_BOUNDED_STRUCTURAL_SEGMENT_CHILD_CARRIERS_DERIVED',out
        assert out['carrier_count']==2
        left,right=out['carriers']
        assert (left['source_side'],right['source_side'])==('LEFT','RIGHT')
        assert (left['leaf_arity'],right['leaf_arity'])==shape
        assert left['composition_content_digest_sha256']==left_direct
        assert right['composition_content_digest_sha256']==right_direct
        assert tuple(left['ordered_operational_referent_signatures'])==left_sigs
        assert tuple(right['ordered_operational_referent_signatures'])==right_sigs
        assert len(left['validated_components'])==shape[0] and len(right['validated_components'])==shape[1]
        assert before==after
        assert out['parent_child_count']==2 and out['recursive_depth_limit']==1
        assert out['flattening_authority']==out['associativity_authority']=='NONE'
        assert out['historical_event_authority']==out['scheduler_authority']==out['effect_authority']=='NONE'
        assert out['caller_supplied_split']==out['caller_supplied_leaf_arity']==out['caller_supplied_grouping']=='NO'
    finally:_close(m);td.cleanup()

@pytest.mark.parametrize('shape',tuple(x for x in SHAPES if x!=(2,2)))
def test_every_mixed_shape_forms_exact_two_child_depth_one_parent_without_flattening(shape):
    seq=SHAPES[shape]
    td,m,world,seeded=_setup('SEGMENT-ARITY-PARENT-'+str(shape))
    try:
        b=_boundary(m,seq,230000+100*shape[0]+shape[1]); assert (b['split_index'],len(seq)-b['split_index'])==shape,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        before=tuple(r['evidence_id'] for r in m.evidence.list())
        out=derive_current_bounded_structural_segment_recursive_parent_prototypes(m,max_records=65536)
        assert out['status']=='CURRENT_BOUNDED_STRUCTURAL_SEGMENT_RECURSIVE_PARENT_PROTOTYPES_DERIVED',out
        assert out['parent_count']==1
        p=out['parents'][0]
        assert p['child_leaf_arities']==shape
        assert p['child_arity']==2 and p['composition_depth']==1
        assert tuple(c['source_side'] for c in p['children'])==('LEFT','RIGHT')
        assert tuple(c['leaf_arity'] for c in p['children'])==shape
        assert p['composition_content']=={
            'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'ordered_child_composition_content_digests':list(p['ordered_child_composition_content_digests']),
            'composition_depth':1,'child_arity':2,
            'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY',
        }
        assert 'ordered_operational_referent_signatures' not in p['composition_content']
        assert p['flattening_authority']==p['associativity_authority']==p['historical_event_authority']=='NONE'
        assert tuple(r['evidence_id'] for r in m.evidence.list())==before
    finally:_close(m);td.cleanup()


def test_identical_four_plus_four_child_content_does_not_manufacture_two_recursive_operands():
    td,m,world,seeded=_setup('SEGMENT-ARITY-IDENTICAL-4-4')
    try:
        seq=('R4','T9','W3','K7','R4','T9','W3','K7')
        b=_boundary(m,seq,240000); assert b['split_index']==4,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert s['left_composition_content_digest_sha256']==s['right_composition_content_digest_sha256']
        out=derive_current_bounded_structural_segment_recursive_parent_prototypes(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_DISTINCT_BOUNDED_SEGMENT_CHILD_PAIR_REQUIRED'
        assert out['skipped'][0]['reason']=='TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED'
        assert out['skipped'][0]['child_leaf_arities']==(4,4)
    finally:_close(m);td.cleanup()
