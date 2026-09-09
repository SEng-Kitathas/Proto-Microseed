import inspect

from microseed import Microseed
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_close


def _run_parent(*,tokens=('R4','T9','W3','K7'),sensor_transform=None,base=157000):
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-INVAR',tokens=tokens,sensor_transform=sensor_transform)
    try:
        _boundary(m,(tokens[0],tokens[1],tokens[0],tokens[3]),base)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        return p['composition_content_digest_sha256'],p['ordered_child_composition_content_digests']
    finally:_close(m);td.cleanup()


def test_segment_recursive_parent_is_invariant_to_surface_token_permutation_and_sensor_transform():
    a=_run_parent(base=157000)
    b=_run_parent(tokens=('K7','R4','T9','W3'),base=158000)
    p=_run_parent(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=159000)
    inv=_run_parent(sensor_transform=lambda row:tuple(-x for x in row),base=160000)
    assert a==b==p==inv


def test_segment_recursive_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-BUDGET')
    try:
        _boundary(m,('R4','T9','R4','K7'),161000)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        total=m.evidence.count();assert total>0
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='SEGMENT_RECURSIVE_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert out['total_records']==total and out['max_records']==total-1
    finally:_close(m);td.cleanup()


def test_segment_state_creation_does_not_automatically_schedule_or_create_recursive_parent():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-NOAUTO')
    try:
        _boundary(m,('R4','T9','R4','K7'),162000)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE']
        segment_src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_state).lower()
        assert 'derive_and_record_current_native_structural_segment_b2_recursive_composition' not in segment_src
        assert 'owned_native_structural_segment_b2_recursive_composition_state' not in segment_src
    finally:_close(m);td.cleanup()


def test_identical_segment_side_content_cannot_fake_two_independent_recursive_operands_in_production():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-IDENTICAL')
    try:
        _boundary(m,('R4','T9','R4','T9'),163000)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert s['left_composition_content_digest_sha256']==s['right_composition_content_digest_sha256']
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED',out
        assert out['skipped'][0]['reason']=='TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED'
    finally:_close(m);td.cleanup()


def test_unsupported_mixed_arity_state_is_not_consumed_and_does_not_override_oldest_compatible_selection():
    td,m,world,seeded=_setup('SEGMENT-RECURSIVE-COMPAT-SELECTION')
    try:
        bm=_boundary(m,('R4','T9','R4','W3','K7'),164000);assert bm['split_index']==2,bm
        bc=_boundary(m,('R4','T9','R4','K7'),164100);assert bc['split_index']==2,bc
        sm=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        sc=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert sm['boundary_evidence_id']==bm['boundary_evidence_id'] and sm['right_content']['arity']==3
        assert sc['boundary_evidence_id']==bc['boundary_evidence_id'] and sc['right_content']['arity']==2
        out=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['segment_state_evidence_id']==sc['segment_state_evidence_id']
        assert out['skipped'][0]['segment_state_evidence_id']==sm['segment_state_evidence_id']
        assert out['skipped'][0]['reason']=='SEGMENT_STATE_SIDE_NOT_B2_COMPATIBLE_FOR_RECURSIVE_REUSE'
        # The mixed state remains unconsumed, making the bounded compatibility ceiling visible.
        again=m.derive_and_record_current_native_structural_segment_b2_recursive_composition(max_records=65536)
        assert again['status']=='DEFER_UNKNOWN',again
        assert again['reason']=='CURRENT_UNCONSUMED_B2_COMPATIBLE_STRUCTURAL_SEGMENT_STATE_REQUIRED'
        assert again['skipped'][0]['segment_state_evidence_id']==sm['segment_state_evidence_id']
    finally:_close(m);td.cleanup()
