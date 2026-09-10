from microseed import EpistemicStatus
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent


def _run_invariant(tokens=('R4','T9','W3','K7'),sensor_transform=None,base=350000):
    td,m,world,seeded=_setup('SEGMENT-PARENT-INVAR',tokens=tokens,sensor_transform=sensor_transform)
    try:
        b2_seq=(tokens[0],tokens[1],tokens[0],tokens[3])
        mixed_seq=(tokens[0],tokens[1],tokens[2],tokens[0],tokens[1],tokens[2],tokens[3])
        _b2_parent(m,base,b2_seq)
        # local mixed parent helper uses fixed token fixture, so build the equivalent parent directly.
        from tests.embodiment.test_lang_boundary_consumption_production import _boundary
        b=_boundary(m,mixed_seq,base+1000); assert (b['split_index'],len(mixed_seq)-b['split_index'])==(3,4),b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536); assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        return out['composition_content_digest_sha256'],out['ordered_child_composition_content_digests']
    finally:_close(m);td.cleanup()


def test_depth_two_nested_parent_identity_is_invariant_to_token_permutation_and_sensor_transform():
    a=_run_invariant(base=350000)
    b=_run_invariant(tokens=('K7','R4','T9','W3'),base=352000)
    p=_run_invariant(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=354000)
    inv=_run_invariant(sensor_transform=lambda row:tuple(-x for x in row),base=356000)
    assert a==b==p==inv


def test_copied_valid_depth_one_parent_payload_under_new_id_cannot_become_depth_two_child():
    td,m,world,seeded=_setup('SEGMENT-PARENT-CHILD-FORGE')
    try:
        _b2_parent(m,358000)
        _b,_s,p=_mixed_parent(m,(3,4),359000)
        row=m.evidence.get(p['composition_state_evidence_id']); assert row is not None
        m.append_evidence('E-FORGED-DEPTH-ONE-PARENT',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_DEPTH_ONE_COPY')
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='SEGMENT_BOUNDED_RECURSIVE_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT'
    finally:_close(m);td.cleanup()
