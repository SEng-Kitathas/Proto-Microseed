import inspect

from microseed import Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close


def test_current_campaign_earns_mixed_bounded_leaf_arity_but_parent_remains_exact_two_grouped_children_depth_one():
    td,m,world,seeded=_setup('SEGMENT-ARITY-CEILING-MIXED')
    try:
        seq=('R4','T9','W3','R4','T9','W3','K7')  # derived 3+4
        b=_boundary(m,seq,281000); assert (b['split_index'],len(seq)-b['split_index'])==(3,4),b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        assert p['child_leaf_arities']==(3,4)
        assert p['bounded_min_leaf_arity']==2 and p['bounded_max_leaf_arity']==4
        assert p['parent_child_count']==2 and p['child_arity']==2 and p['recursive_depth_limit']==1
        assert tuple(c['source_side'] for c in p['children'])==('LEFT','RIGHT')
        assert tuple(c['leaf_arity'] for c in p['children'])==(3,4)
        assert p['flattening_authority']==p['associativity_authority']=='NONE'
        assert p['historical_event_authority']==p['scheduler_authority']==p['effect_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_exact_2_plus_2_remains_sealed_b2_owner_while_new_owner_is_mixed_only():
    td,m,world,seeded=_setup('SEGMENT-ARITY-CEILING-2-2')
    try:
        b=_boundary(m,('R4','T9','R4','K7'),282000); assert b['split_index']==2,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        mixed=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert mixed['status']=='DEFER_UNKNOWN',mixed
        assert mixed['reason']=='CURRENT_UNCONSUMED_MIXED_BOUNDED_STRUCTURAL_SEGMENT_STATE_REQUIRED'
        assert mixed['skipped'][0]['reason']=='LEGACY_B2_COMPATIBLE_SEGMENT_STATE_OWNED_BY_EXISTING_B2_CONSUMER'
        b2=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert b2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',b2
    finally:_close(m);td.cleanup()


def test_current_campaign_does_not_earn_unbounded_leaf_arity_flattening_associativity_or_historical_event_status():
    helper=inspect.getsource(Microseed._native_structural_segment_bounded_child_carriers)
    consumer=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_bounded_recursive_composition)
    validator=inspect.getsource(Microseed._validate_current_native_structural_segment_bounded_recursive_composition_state)
    assert '2<=leaf_arity<=4' in helper
    assert '"composition_depth":1,"child_arity":2' in consumer
    assert '"bounded_min_leaf_arity":2,"bounded_max_leaf_arity":4' in consumer
    assert '"flattening_authority":"NONE"' in consumer
    assert '"associativity_authority":"NONE"' in consumer
    assert '"historical_event_authority":"NONE"' in consumer
    assert '"scheduler_authority":"NONE"' in consumer
    assert '"effect_authority":"NONE"' in consumer
    assert '"semantic_composition_authority":"NONE"' in consumer
    assert 'SEGMENT_BOUNDED_RECURSIVE_STATE_AUTHORITY_OVERCLAIM' in validator
    historical=inspect.getsource(Microseed.derive_and_record_current_native_recursive_b2_ordered_composition)
    assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE' not in historical


def test_new_parent_content_is_nested_child_identity_only_not_flattened_leaf_referent_list():
    td,m,world,seeded=_setup('SEGMENT-ARITY-CEILING-NESTED')
    try:
        seq=('R4','T9','R4','W3','K7','T9')  # derived 2+4
        b=_boundary(m,seq,283000); assert (b['split_index'],len(seq)-b['split_index'])==(2,4),b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        row=m.evidence.get(p['composition_state_evidence_id']); assert row is not None
        payload=row['payload']
        assert payload['composition_operator']=='RECURSIVE_ORDERED_EVIDENCE_TUPLE'
        assert payload['child_arity']==2 and tuple(payload['child_leaf_arities'])==(2,4)
        assert len(payload['ordered_child_composition_content_digests'])==2
        assert 'ordered_operational_referent_signatures' not in {
            'operator':payload['composition_operator'],
            'children':payload['ordered_child_composition_content_digests'],
            'depth':payload['composition_depth'],
            'child_arity':payload['child_arity'],
        }
        assert sum(len(c['validated_components']) for c in payload['children'])==6
        assert payload['flattening_authority']==payload['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()
