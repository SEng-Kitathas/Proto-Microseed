import copy
from microseed import EpistemicStatus
from microseed.development.action_closure import result_digest
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent
from tests.embodiment.test_lang_segment_depth_four_parent_production import _depth_four

def _depth_five(m,base=550000):
    p1,p2,d2,p3,d3,p4,d4=_depth_four(m,base);p5=_mixed_parent(m,(3,2),base+4000)[2];d5=m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=65536);return p1,p2,d2,p3,d3,p4,d4,p5,d5

def test_production_depth_five_preserves_whole_depth_four_plus_external_depth_one():
    td,m,w,s=_setup('D5-PROD')
    try:
        *xs,d4,p5,o=_depth_five(m);assert o['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_FIVE_RECURSIVE_COMPOSITION_STATE_RECORDED',o;assert sorted(o['ordered_child_composition_depths'])==[1,4];d4c=next(c for c in o['children'] if c['composition_depth']==4);assert d4c['composition_content_digest_sha256']==d4['composition_content_digest_sha256'];row=m.evidence.get(o['composition_state_evidence_id']);pc=next(c for c in row['payload']['children'] if c['composition_depth']==4);assert p5['composition_content_digest_sha256'] not in pc['full_ancestry_content_digests'];assert row['payload']['generic_recursive_closure_authority']==row['payload']['depth_six_authority']=='NONE'
    finally:_close(m);td.cleanup()

def test_production_depth_five_requires_external_outside_full_ancestry():
    td,m,w,s=_setup('D5-ANCESTRY')
    try:_depth_four(m,555000);g=m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=65536);assert g['status']=='DEFER_UNKNOWN' and g['reason']=='DISTINCT_EXTERNAL_CURRENT_DEPTH_ONE_PARENT_OUTSIDE_FULL_DEPTH_FOUR_ANCESTRY_REQUIRED',g
    finally:_close(m);td.cleanup()

def test_production_depth_five_idempotent_no_self_feed():
    td,m,w,s=_setup('D5-IDEMP')
    try:*x,o=_depth_five(m,560000);ids=tuple(r['evidence_id'] for r in m.evidence.list());a=m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=65536);assert a['composition_state_record_status']=='SEGMENT_DEPTH_FIVE_STATE_ALREADY_PRESENT';assert tuple(r['evidence_id'] for r in m.evidence.list())==ids;assert 5 not in a['ordered_child_composition_depths']
    finally:_close(m);td.cleanup()

def test_copied_depth_five_payload_under_new_id_refused():
    td,m,w,s=_setup('D5-COPY')
    try:*x,o=_depth_five(m,565000);row=m.evidence.get(o['composition_state_evidence_id']);m.append_evidence('E-D5-COPY',copy.deepcopy(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='TEST');g=m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=65536);assert g['status']=='DEFER_UNKNOWN' and g['reason']=='SEGMENT_DEPTH_FIVE_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',g
    finally:_close(m);td.cleanup()

def test_depth_five_currentness_drift_fails_closed():
    td,m,w,s=_setup('D5-DRIFT')
    try:_depth_five(m,570000);m.change_capability_dependency('QA',reason='D5-QA-DRIFT');assert m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=65536)['status']=='DEFER_UNKNOWN'
    finally:_close(m);td.cleanup()

def test_depth_five_budget_exhaustion_not_saturation():
    td,m,w,s=_setup('D5-BUDGET')
    try:_depth_five(m,575000);g=m.derive_and_record_current_native_structural_segment_depth_five_recursive_composition(max_records=1);assert g['status']=='DEFER_UNKNOWN' and g['reason']=='SEGMENT_DEPTH_FIVE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
    finally:_close(m);td.cleanup()

def test_depth_five_identity_differs_from_flattened_descendants():
    td,m,w,s=_setup('D5-ID')
    try:p1,p2,d2,p3,d3,p4,d4,p5,o=_depth_five(m,580000);flat=result_digest({'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE','ordered_child_composition_content_digests':[p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'],p3['composition_content_digest_sha256'],p4['composition_content_digest_sha256'],p5['composition_content_digest_sha256']],'composition_depth':1,'child_arity':5,'identity_scope':'FLATTENED'});assert o['composition_content_digest_sha256']!=flat
    finally:_close(m);td.cleanup()
