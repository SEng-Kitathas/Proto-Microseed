import inspect
import pytest

from microseed import EpistemicStatus,Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close

MIXED_SHAPES={
    (2,3):('R4','T9','R4','W3','K7'),
    (3,2):('R4','T9','W3','K7','W3'),
    (3,3):('R4','T9','W3','R4','W3','T9'),
    (2,4):('R4','T9','R4','W3','K7','T9'),
    (4,2):('R4','T9','W3','K7','W3','K7'),
    (3,4):('R4','T9','W3','R4','T9','W3','K7'),
    (4,3):('R4','T9','W3','K7','R4','K7','T9'),
    (4,4):('R4','T9','W3','K7','R4','T9','K7','W3'),
}


def _record(m,shape,base):
    seq=MIXED_SHAPES[shape]
    b=_boundary(m,seq,base)
    assert (b['split_index'],len(seq)-b['split_index'])==shape,b
    s=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
    assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
    p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
    return b,s,p


@pytest.mark.parametrize('shape',tuple(MIXED_SHAPES))
def test_new_production_owner_admits_every_mixed_bounded_shape_as_two_grouped_children_without_flattening(shape):
    td,m,world,seeded=_setup('SEGMENT-ARITY-PROD-'+str(shape))
    try:
        before=tuple(r['evidence_id'] for r in m.evidence.list())
        b,s,p=_record(m,shape,250000+100*shape[0]+shape[1])
        after=tuple(r['evidence_id'] for r in m.evidence.list())
        assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        assert p['child_leaf_arities']==shape
        assert p['child_arity']==2 and p['parent_child_count']==2 and p['composition_depth']==1
        assert tuple(c['source_side'] for c in p['children'])==('LEFT','RIGHT')
        assert tuple(c['leaf_arity'] for c in p['children'])==shape
        assert tuple(c['composition_content_digest_sha256'] for c in p['children'])==p['ordered_child_composition_content_digests']
        assert len(p['children'][0]['validated_components'])==shape[0]
        assert len(p['children'][1]['validated_components'])==shape[1]
        assert after[:len(before)]==before
        assert after[-3:]==(b['boundary_evidence_id'],s['segment_state_evidence_id'],p['composition_state_evidence_id'])
        row=m.evidence.get(p['composition_state_evidence_id']); assert row is not None
        payload=row['payload']
        assert payload['child_arity']==2 and tuple(payload['child_leaf_arities'])==shape
        assert payload['temporality']=='CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_SEGMENT_STATE'
        assert 'ordered_operational_referent_signatures' not in {
            'operator':payload['composition_operator'],
            'children':payload['ordered_child_composition_content_digests'],
            'depth':payload['composition_depth'],'arity':payload['child_arity'],
        }
        assert p['flattening_authority']==p['associativity_authority']=='NONE'
        assert p['historical_event_authority']==p['scheduler_authority']==p['effect_authority']=='NONE'
        assert p['caller_supplied_split']==p['caller_supplied_leaf_arity']==p['caller_supplied_grouping']=='NO'
        # Historical/B2 evidence kinds are not backfilled.
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind') in {
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE',
        }]
    finally:_close(m);td.cleanup()


def test_exact_2_plus_2_remains_owned_by_existing_b2_segment_consumer_not_new_bounded_owner():
    td,m,world,seeded=_setup('SEGMENT-ARITY-LEGACY-B2')
    try:
        b=_boundary(m,('R4','T9','R4','K7'),260000); assert b['split_index']==2,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        new=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert new['status']=='DEFER_UNKNOWN',new
        assert new['reason']=='CURRENT_UNCONSUMED_MIXED_BOUNDED_STRUCTURAL_SEGMENT_STATE_REQUIRED'
        assert new['skipped'][0]['reason']=='LEGACY_B2_COMPATIBLE_SEGMENT_STATE_OWNED_BY_EXISTING_B2_CONSUMER'
        old=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert old['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',old
        assert old['child_arity']==2
    finally:_close(m);td.cleanup()


def test_mixed_bounded_parent_is_idempotent_and_deterministic():
    td,m,world,seeded=_setup('SEGMENT-ARITY-IDEMP')
    try:
        b,s,p=_record(m,(3,4),261000)
        ids=tuple(r['evidence_id'] for r in m.evidence.list())
        again=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert again['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_ALREADY_PRESENT',again
        assert again['composition_state_evidence_id']==p['composition_state_evidence_id']
        assert again['composition_content_digest_sha256']==p['composition_content_digest_sha256']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids
    finally:_close(m);td.cleanup()


def test_copied_valid_mixed_bounded_parent_payload_under_new_id_is_refused():
    td,m,world,seeded=_setup('SEGMENT-ARITY-FORGE')
    try:
        _b,_s,p=_record(m,(2,4),262000)
        row=m.evidence.get(p['composition_state_evidence_id']); assert row is not None
        m.append_evidence('E-FORGED-SEGMENT-BOUNDED-PARENT',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_COPY')
        out=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='SEGMENT_BOUNDED_RECURSIVE_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT'
    finally:_close(m);td.cleanup()


def test_mixed_bounded_parent_stales_when_underlying_leaf_currentness_drifts():
    td,m,world,seeded=_setup('SEGMENT-ARITY-DRIFT')
    try:
        _b,_s,p=_record(m,(4,3),263000)
        m.change_capability_dependency('QA',reason='SEGMENT-ARITY-QA-DRIFT')
        out=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'},out
    finally:_close(m);td.cleanup()


def test_multiple_mixed_states_are_consumed_oldest_first_while_legacy_2_plus_2_is_skipped_not_stolen():
    td,m,world,seeded=_setup('SEGMENT-ARITY-MULTI')
    try:
        b0=_boundary(m,('R4','T9','R4','K7'),264000)
        b1=_boundary(m,MIXED_SHAPES[(2,3)],264100)
        b2=_boundary(m,MIXED_SHAPES[(4,2)],264200)
        s0=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        s1=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        s2=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s0['boundary_evidence_id']==b0['boundary_evidence_id']
        assert s1['boundary_evidence_id']==b1['boundary_evidence_id']
        assert s2['boundary_evidence_id']==b2['boundary_evidence_id']
        p1=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        p2=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        p3=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert p1['status']==p2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED'
        assert p1['segment_state_evidence_id']==s1['segment_state_evidence_id']
        assert p2['segment_state_evidence_id']==s2['segment_state_evidence_id']
        assert p3['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_ALREADY_PRESENT',p3
        old=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert old['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',old
        assert old['segment_state_evidence_id']==s0['segment_state_evidence_id']
    finally:_close(m);td.cleanup()


def test_mixed_bounded_parent_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-ARITY-BUDGET')
    try:
        b=_boundary(m,MIXED_SHAPES[(3,2)],265000)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        total=m.evidence.count(); assert total>0
        out=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='SEGMENT_BOUNDED_RECURSIVE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert out['total_records']==total and out['max_records']==total-1
    finally:_close(m);td.cleanup()


def test_new_mixed_bounded_surface_has_budget_only_and_no_caller_selector_or_scheduling_parameters():
    sig=inspect.signature(Microseed.derive_and_record_current_native_structural_segment_bounded_recursive_composition)
    assert tuple(sig.parameters)==('self','max_records')
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_bounded_recursive_composition).lower()
    assert 'oldest_current_unconsumed_mixed_bounded_structural_segment_state_by_evidence_append_order' in src
    for forbidden in ('segment_state_id:', 'split:', 'leaf_arity:', 'child_ids:', 'child_order:', 'grouping:', 'output_evidence_id:', 'execute_bounded_action(', 'scheduler(', 'planner('):
        assert forbidden not in str(sig).lower()
