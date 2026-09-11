import copy
from microseed import EpistemicStatus
from microseed.development.action_closure import result_digest
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent
from tests.embodiment.test_lang_segment_depth_three_parent_production import _depth_three


def _depth_four(m,base=470000):
    p1,p2,d2,p3,d3=_depth_three(m,base)
    p4=_mixed_parent(m,(2,4),base+3000)[2]
    d4=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
    return p1,p2,d2,p3,d3,p4,d4


def test_production_depth_four_preserves_whole_depth_three_plus_external_depth_one():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-PROD')
    try:
        p1,p2,d2,p3,d3,p4,out=_depth_four(m)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['composition_depth']==4 and out['child_arity']==2 and out['max_input_parent_depth']==3
        assert sorted(out['ordered_child_composition_depths'])==[1,3]
        d3c=next(c for c in out['children'] if c['composition_depth']==3);d1c=next(c for c in out['children'] if c['composition_depth']==1)
        assert d3c['composition_content_digest_sha256']==d3['composition_content_digest_sha256']
        assert d1c['composition_content_digest_sha256']==p4['composition_content_digest_sha256']
        row=m.evidence.get(out['composition_state_evidence_id']);pc3=next(c for c in row['payload']['children'] if c['composition_depth']==3)
        assert p4['composition_content_digest_sha256'] not in pc3['full_ancestry_content_digests']
        assert row['payload']['generic_recursive_closure_authority']==row['payload']['depth_five_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_production_depth_four_full_ancestry_exclusion_requires_new_external_parent():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-ANCESTRY')
    try:
        _depth_three(m,474000)
        got=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        assert got['status']=='DEFER_UNKNOWN' and got['reason']=='DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_THREE_ANCESTRY_REQUIRED',got
    finally:_close(m);td.cleanup()


def test_production_depth_four_evidence_order_can_be_depth_one_then_depth_three():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-ORDER')
    try:
        _b2_parent(m,478000);_mixed_parent(m,(3,4),479000)
        m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        early=_mixed_parent(m,(4,2),480000)[2]
        latest=_mixed_parent(m,(2,3),481000)[2]
        d3=m.derive_and_record_current_native_structural_segment_depth_three_recursive_composition(max_records=65536)
        out=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FOUR_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['ordered_child_composition_depths']==(1,3)
        assert out['ordered_child_composition_content_digests'][0]==early['composition_content_digest_sha256']
        assert out['ordered_child_composition_content_digests'][1]==d3['composition_content_digest_sha256']
        assert latest['composition_content_digest_sha256'] in next(c for c in out['children'] if c['composition_depth']==3)['full_ancestry_content_digests']
    finally:_close(m);td.cleanup()


def test_production_depth_four_is_idempotent_and_never_uses_own_output_as_child():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-IDEMP')
    try:
        *_x,out=_depth_four(m,482000);ids=tuple(r['evidence_id'] for r in m.evidence.list())
        again=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        assert again['composition_state_record_status']=='SEGMENT_DEPTH_FOUR_STATE_ALREADY_PRESENT'
        assert again['composition_state_evidence_id']==out['composition_state_evidence_id']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids
        assert 4 not in again['ordered_child_composition_depths']
    finally:_close(m);td.cleanup()


def test_copied_valid_depth_four_payload_under_new_id_is_refused():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-COPY')
    try:
        *_x,out=_depth_four(m,486000);row=m.evidence.get(out['composition_state_evidence_id']);payload=copy.deepcopy(row['payload'])
        m.append_evidence('E-DEPTH4-COPIED-INVALID-ID',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='TEST-COPY')
        got=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        assert got['status']=='DEFER_UNKNOWN' and got['reason']=='SEGMENT_DEPTH_FOUR_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',got
    finally:_close(m);td.cleanup()


def test_depth_four_nested_currentness_drift_invalidates_reuse():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-DRIFT')
    try:
        _depth_four(m,490000);m.change_capability_dependency('QA',reason='SEGMENT-DEPTH4-QA-DRIFT')
        got=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=65536)
        assert got['status']=='DEFER_UNKNOWN',got
    finally:_close(m);td.cleanup()


def test_depth_four_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-BUDGET')
    try:
        _depth_four(m,494000);got=m.derive_and_record_current_native_structural_segment_depth_four_recursive_composition(max_records=1)
        assert got['status']=='DEFER_UNKNOWN' and got['reason']=='SEGMENT_DEPTH_FOUR_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET',got
    finally:_close(m);td.cleanup()


def test_depth_four_nested_identity_differs_from_flattened_depth_one_descendants():
    td,m,world,seeded=_setup('SEGMENT-DEPTH4-IDENTITY')
    try:
        p1,p2,d2,p3,d3,p4,out=_depth_four(m,498000)
        flat=result_digest({'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE','ordered_child_composition_content_digests':[p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'],p3['composition_content_digest_sha256'],p4['composition_content_digest_sha256']],'composition_depth':1,'child_arity':4,'identity_scope':'FLATTENED'})
        assert out['composition_content_digest_sha256']!=flat
    finally:_close(m);td.cleanup()
