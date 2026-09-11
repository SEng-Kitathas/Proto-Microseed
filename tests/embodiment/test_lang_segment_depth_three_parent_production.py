import copy

from microseed import EpistemicStatus
from microseed.development.action_closure import result_digest
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent


def _depth_three(m,base=420000):
    p1=_b2_parent(m,base)[2]
    p2=_mixed_parent(m,(3,4),base+1000)[2]
    d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
    assert d2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',d2
    p3=_mixed_parent(m,(4,2),base+2000)[2]
    d3=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
    return p1,p2,d2,p3,d3


def test_production_depth_three_preserves_whole_depth_two_plus_external_depth_one():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-PROD')
    try:
        p1,p2,d2,p3,out=_depth_three(m)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['composition_depth']==3 and out['child_arity']==2 and out['max_input_parent_depth']==2
        assert sorted(out['ordered_child_composition_depths'])==[1,2]
        d2_child=next(c for c in out['children'] if c['composition_depth']==2)
        d1_child=next(c for c in out['children'] if c['composition_depth']==1)
        assert d2_child['composition_content_digest_sha256']==d2['composition_content_digest_sha256']
        assert d1_child['composition_content_digest_sha256']==p3['composition_content_digest_sha256']
        row=m.evidence.get(out['composition_state_evidence_id']); payload=row['payload']
        pc2=next(c for c in payload['children'] if c['composition_depth']==2)
        assert tuple(pc2['nested_child_content_digests'])==d2['ordered_child_composition_content_digests']
        assert payload['generic_recursive_closure_authority']==payload['depth_four_authority']=='NONE'
        assert payload['flattening_authority']==payload['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_production_depth_three_evidence_order_can_be_depth_one_then_depth_two():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-ORDER')
    try:
        early=_b2_parent(m,423000)[2]
        _mixed_parent(m,(3,4),424000)
        _mixed_parent(m,(4,2),425000)
        d2=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        out=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_THREE_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['ordered_child_composition_depths']==(1,2)
        assert out['ordered_child_composition_content_digests'][0]==early['composition_content_digest_sha256']
        assert out['ordered_child_composition_content_digests'][1]==d2['composition_content_digest_sha256']
    finally:_close(m);td.cleanup()


def test_production_depth_three_is_idempotent_and_never_uses_own_output_as_child():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-IDEMP')
    try:
        *_x,out=_depth_three(m,426000)
        ids=tuple(r['evidence_id'] for r in m.evidence.list())
        again=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        assert again['composition_state_record_status']=='SEGMENT_DEPTH_THREE_STATE_ALREADY_PRESENT'
        assert again['composition_state_evidence_id']==out['composition_state_evidence_id']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids
        assert 3 not in again['ordered_child_composition_depths']
    finally:_close(m);td.cleanup()


def test_copied_valid_depth_three_payload_under_new_id_is_refused():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-COPY')
    try:
        *_x,out=_depth_three(m,429000)
        row=m.evidence.get(out['composition_state_evidence_id']); payload=copy.deepcopy(row['payload'])
        m.append_evidence('E-DEPTH3-COPIED-INVALID-ID',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='TEST-COPY')
        got=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        assert got['status']=='DEFER_UNKNOWN' and got['reason']=='SEGMENT_DEPTH_THREE_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',got
    finally:_close(m);td.cleanup()


def test_depth_three_nested_currentness_drift_invalidates_reuse():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-DRIFT')
    try:
        _depth_three(m,432000)
        m.change_capability_dependency('QA',reason='SEGMENT-DEPTH3-QA-DRIFT')
        got=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        assert got['status']=='DEFER_UNKNOWN',got
    finally:_close(m);td.cleanup()


def test_depth_three_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-BUDGET')
    try:
        _depth_three(m,435000)
        got=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=1)
        assert got['status']=='DEFER_UNKNOWN' and got['reason']=='SEGMENT_DEPTH_THREE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET',got
    finally:_close(m);td.cleanup()


def test_depth_three_nested_identity_differs_from_flattened_descendants():
    td,m,world,seeded=_setup('SEGMENT-DEPTH3-IDENTITY')
    try:
        p1,p2,d2,p3,out=_depth_three(m,438000)
        flattened=result_digest({'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE','ordered_child_composition_content_digests':[p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'],p3['composition_content_digest_sha256']],'composition_depth':1,'child_arity':3,'identity_scope':'FLATTENED'})
        assert out['composition_content_digest_sha256']!=flattened
    finally:_close(m);td.cleanup()
