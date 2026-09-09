from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed import EpistemicStatus,Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_obs,_close
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,seed_four_current_native_referent_associations


def _historical_parent_control():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-HISTORICAL-CONTROL')
    try:
        _obs(m,('R4','T9'),146000,'SEGMENT-RECURSIVE-HIST-LEFT')
        left=m.derive_and_record_current_native_b2_ordered_composition(max_records=65536)
        _obs(m,('R4','K7'),146100,'SEGMENT-RECURSIVE-HIST-RIGHT')
        right=m.derive_and_record_current_native_b2_ordered_composition(max_records=65536)
        parent=m.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=65536)
        assert left['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',left
        assert right['status']=='CURRENT_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',right
        assert parent['status']=='CURRENT_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_RECORDED',parent
        return parent['composition_content_digest_sha256'],tuple(parent['ordered_child_composition_content_digests'])
    finally:_close(m);td.cleanup()


def _segment_parent(m,seq=('R4','T9','R4','K7'),base=147000):
    boundary=_boundary(m,seq,base)
    segment=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
    assert segment['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',segment
    parent=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
    return boundary,segment,parent


def test_production_segment_state_sides_become_grouped_recursive_operands_with_exact_existing_parent_content_identity():
    historical_digest,historical_children=_historical_parent_control()
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-PROD')
    try:
        before=tuple(r['evidence_id'] for r in m.evidence.list())
        boundary,segment,parent=_segment_parent(m)
        after=tuple(r['evidence_id'] for r in m.evidence.list())
        assert parent['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',parent
        assert parent['composition_content_digest_sha256']==historical_digest
        assert parent['ordered_child_composition_content_digests']==historical_children
        assert parent['segment_state_evidence_id']==segment['segment_state_evidence_id']
        assert parent['boundary_evidence_id']==boundary['boundary_evidence_id']
        assert tuple(c['source_side'] for c in parent['children'])==('LEFT','RIGHT')
        assert tuple(len(c['validated_components']) for c in parent['children'])==(2,2)
        assert after[:len(before)]==before
        assert after[-1]==parent['composition_state_evidence_id']
        assert parent['historical_event_authority']==parent['ledger_rewrite_authority']=='NONE'
        assert parent['flattening_authority']==parent['associativity_authority']=='NONE'
        assert parent['semantic_composition_authority']==parent['grammar_authority']=='NONE'
        assert parent['effect_authority']==parent['execution_authority']==parent['scheduler_authority']=='NONE'
        assert parent['caller_supplied_segment_state_id']==parent['caller_supplied_child_ids']==parent['caller_supplied_child_order']==parent['caller_supplied_grouping']==parent['caller_supplied_output_evidence_id']=='NO'
        historical_kinds={
            'OWNED_NATIVE_B2_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE',
            'OWNED_NATIVE_RECURSIVE_B2_ORDERED_COMPOSITION_EVIDENCE',
        }
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind') in historical_kinds]
    finally:_close(m);td.cleanup()


def test_production_segment_recursive_reuse_is_idempotent_and_deterministic():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-IDEMP')
    try:
        _b,_s,parent=_segment_parent(m,base=148000)
        ids=tuple(r['evidence_id'] for r in m.evidence.list())
        again=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert again['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_ALREADY_PRESENT',again
        assert again['composition_state_evidence_id']==parent['composition_state_evidence_id']
        assert again['composition_content_digest_sha256']==parent['composition_content_digest_sha256']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids
    finally:_close(m);td.cleanup()


def test_copied_valid_segment_recursive_payload_under_new_id_is_refused():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-FORGE')
    try:
        _b,_s,parent=_segment_parent(m,base=149000)
        row=m.evidence.get(parent['composition_state_evidence_id']);assert row is not None
        m.append_evidence('E-FORGED-SEGMENT-RECURSIVE-COPY',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_COPY')
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='SEGMENT_RECURSIVE_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',out
    finally:_close(m);td.cleanup()


def test_segment_recursive_operand_reuse_stales_when_underlying_leaf_currentness_drifts():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-DRIFT')
    try:
        _b,_s,parent=_segment_parent(m,base=150000)
        m.change_capability_dependency('QA',reason='SEGMENT-RECURSIVE-QA-DRIFT')
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'},out
    finally:_close(m);td.cleanup()


def test_mixed_2_plus_3_segment_state_remains_unearned_for_recursive_reuse():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-MIXED')
    try:
        b=_boundary(m,('R4','T9','R4','W3','K7'),151000);assert b['split_index']==2,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED',out
        assert out['skipped'][0]['reason']=='SEGMENT_STATE_SIDE_NOT_B2_COMPATIBLE_FOR_RECURSIVE_REUSE'
        assert out['skipped'][0]['side']=='RIGHT' and out['skipped'][0]['side_arity']==3
    finally:_close(m);td.cleanup()


def test_multiple_compatible_segment_states_are_consumed_oldest_first_by_evidence_chronology():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-MULTI')
    try:
        b1=_boundary(m,('R4','T9','R4','K7'),152000)
        b2=_boundary(m,('T9','W3','T9','R4'),152100)
        s1=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        s2=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s1['boundary_evidence_id']==b1['boundary_evidence_id'] and s2['boundary_evidence_id']==b2['boundary_evidence_id']
        p1=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        p2=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        p3=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert p1['status']==p2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED'
        assert p1['segment_state_evidence_id']==s1['segment_state_evidence_id']
        assert p2['segment_state_evidence_id']==s2['segment_state_evidence_id']
        assert p1['selection_basis']==p2['selection_basis']=='OLDEST_CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_BY_EVIDENCE_APPEND_ORDER'
        assert p3['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_ALREADY_PRESENT',p3
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_current_segment_state_but_rederives_same_parent_content_after_fresh_reacquisition():
    td=TemporaryDirectory(prefix='segment-recursive-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'SEGMENT-RECURSIVE-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),153000,'SEGMENT-RECURSIVE-R1')
        b1=m1.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b1['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b1
        s1=m1.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s1
        p1=m1.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536);assert p1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',p1
        digest=p1['composition_content_digest_sha256']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED',old
        attach_four_runtime_surface(m2,world,'SEGMENT-RECURSIVE-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='SEGMENT-RECURSIVE-R2-FRESH',serial_base=154000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']));assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),155000,'SEGMENT-RECURSIVE-R2')
        b2=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b2['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b2
        s2=m2.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s2
        p2=m2.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536);assert p2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',p2
        assert p2['composition_content_digest_sha256']==digest
        assert p2['composition_state_evidence_id']!=p1['composition_state_evidence_id']
    finally:_close(m2);td.cleanup()


def test_old_recursive_b2_owner_remains_historical_b2_only_and_does_not_consume_segment_state_or_new_parent_state():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-OWNER-SEPARATION')
    try:
        _b,_s,parent=_segment_parent(m,base=156000)
        old=m.derive_and_record_current_native_recursive_b2_ordered_composition(max_records=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='TWO_DISTINCT_CURRENT_B2_COMPOSITION_CHILDREN_REQUIRED',old
        src=inspect.getsource(Microseed.derive_and_record_current_native_recursive_b2_ordered_composition)
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE' not in src
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE' not in src
    finally:_close(m);td.cleanup()


def test_new_segment_recursive_surface_has_budget_only_and_no_caller_grouping_or_selector_parameters():
    sig=inspect.signature(Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition)
    assert tuple(sig.parameters)==('self','max_records')
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition).lower()
    assert 'oldest_current_unconsumed_b2_compatible_structural_segment_state_by_evidence_append_order' in src
    for forbidden in ('segment_state_id:', 'child_ids:', 'child_order:', 'grouping:', 'output_evidence_id:', 'execute_bounded_action(', 'scheduler', 'planner'):
        assert forbidden not in str(sig).lower()
