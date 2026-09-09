from scratch.lang_segment_state_b2_recursive_parent_prototype import derive_current_segment_state_b2_recursive_parent_prototypes
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_obs,_close


def _historical_recursive_parent_digest():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-HISTORICAL-CONTROL')
    try:
        _obs(m,('R4','T9'),142000,'SEGMENT-OPERAND-HISTORICAL-LEFT')
        left=m.derive_and_record_current_native_b2_ordered_composition(max_records=65536)
        assert left['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',left
        _obs(m,('R4','K7'),142100,'SEGMENT-OPERAND-HISTORICAL-RIGHT')
        right=m.derive_and_record_current_native_b2_ordered_composition(max_records=65536)
        assert right['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',right
        parent=m.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=65536)
        assert parent['status']=='CURRENT_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_RECORDED',parent
        return parent['composition_content_digest_sha256'],tuple(parent['ordered_child_composition_content_digests'])
    finally:_close(m);td.cleanup()


def test_b2_compatible_segment_state_reuses_exact_recursive_content_identity_without_historical_b2_rows():
    historical_parent_digest,historical_children=_historical_recursive_parent_digest()
    td,m,world,seeded=_setup('SEGMENT-OPERAND-PARENT-PROTOTYPE')
    try:
        _boundary(m,('R4','T9','R4','K7'),143000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        before=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        out=derive_current_segment_state_b2_recursive_parent_prototypes(m,max_records=65536)
        after=tuple((r['evidence_id'],r['sha256']) for r in m.evidence.list())
        assert out['status']=='CURRENT_SEGMENT_STATE_B2_RECURSIVE_PARENT_PROTOTYPES_DERIVED',out
        assert out['parent_count']==1
        parent=out['parents'][0]
        assert parent['composition_content_digest_sha256']==historical_parent_digest
        assert parent['ordered_child_composition_content_digests']==historical_children
        assert parent['segment_state_evidence_ref']==[state['segment_state_evidence_id'],state['segment_state_evidence_sha256']]
        assert tuple(c['side'] for c in parent['children'])==('LEFT','RIGHT')
        assert tuple(c['arity'] for c in parent['children'])==(2,2)
        assert before==after
        forbidden={
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
        }
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind') in forbidden]
        assert parent['historical_event_authority']==parent['flattening_authority']==parent['associativity_authority']=='NONE'
        assert out['caller_supplied_segment_state_id']==out['caller_supplied_child_ids']==out['caller_supplied_child_order']==out['caller_supplied_grouping']=='NO'
    finally:_close(m);td.cleanup()


def test_mixed_2_plus_3_segment_state_does_not_silently_generalize_recursive_child_arity():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-MIXED-ARITY')
    try:
        b=_boundary(m,('R4','T9','R4','W3','K7'),144000)
        assert b['split_index']==2,b
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        assert state['left_content']['arity']==2 and state['right_content']['arity']==3
        out=derive_current_segment_state_b2_recursive_parent_prototypes(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED',out
        assert out['skipped'][0]['child_arities']==(2,3)
        assert out['skipped'][0]['reason']=='MIXED_OR_NON_B2_SEGMENT_CHILD_ARITY_NOT_EARNED'
    finally:_close(m);td.cleanup()


def test_segment_parent_prototype_preserves_left_right_order_and_refuses_identical_child_content():
    td,m,world,seeded=_setup('SEGMENT-OPERAND-IDENTICAL-CHILD')
    try:
        # A,B | A,B gives two individually admissible B2 sides but identical grouped child content.
        _boundary(m,('R4','T9','R4','T9'),145000)
        state=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert state['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',state
        assert state['left_composition_content_digest_sha256']==state['right_composition_content_digest_sha256']
        out=derive_current_segment_state_b2_recursive_parent_prototypes(m,max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED',out
    finally:_close(m);td.cleanup()
