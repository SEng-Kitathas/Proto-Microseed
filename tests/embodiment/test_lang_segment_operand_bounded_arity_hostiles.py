from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed import EpistemicStatus,Microseed
from microseed.development.action_closure import result_digest
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_boundary,_obs,_close
from tests.embodiment.test_lang_segment_operand_bounded_arity_production import MIXED_SHAPES
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,seed_four_current_native_referent_associations


def _run_invariant(tokens=('R4','T9','W3','K7'),sensor_transform=None,base=270000):
    td,m,world,seeded=_setup('SEGMENT-ARITY-INVAR',tokens=tokens,sensor_transform=sensor_transform)
    try:
        seq=(tokens[0],tokens[1],tokens[2],tokens[0],tokens[1],tokens[2],tokens[3])
        b=_boundary(m,seq,base); assert (b['split_index'],len(seq)-b['split_index'])==(3,4),b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        return p['composition_content_digest_sha256'],p['ordered_child_composition_content_digests'],p['child_leaf_arities']
    finally:_close(m);td.cleanup()


def test_mixed_bounded_parent_is_invariant_to_surface_token_permutation_and_sensor_transform():
    a=_run_invariant(base=270000)
    b=_run_invariant(tokens=('K7','R4','T9','W3'),base=271000)
    p=_run_invariant(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=272000)
    inv=_run_invariant(sensor_transform=lambda row:tuple(-x for x in row),base=273000)
    assert a==b==p==inv


def test_identical_four_plus_four_child_content_is_refused_in_production():
    td,m,world,seeded=_setup('SEGMENT-ARITY-IDENTICAL')
    try:
        seq=('R4','T9','W3','K7','R4','T9','W3','K7')
        b=_boundary(m,seq,274000); assert b['split_index']==4,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert s['left_composition_content_digest_sha256']==s['right_composition_content_digest_sha256']
        out=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='CURRENT_UNCONSUMED_MIXED_BOUNDED_STRUCTURAL_SEGMENT_STATE_REQUIRED'
        assert out['skipped'][0]['reason']=='TWO_DISTINCT_SEGMENT_SIDE_CHILD_CONTENTS_REQUIRED'
        assert out['skipped'][0]['child_leaf_arities']==(4,4)
    finally:_close(m);td.cleanup()


def test_tampered_matching_id_parent_with_false_leaf_arities_is_rejected_by_rederivation():
    td,m,world,seeded=_setup('SEGMENT-ARITY-TAMPER')
    try:
        b=_boundary(m,MIXED_SHAPES[(2,3)],275000); assert b['split_index']==2,b
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        p=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p
        row=m.evidence.get(p['composition_state_evidence_id']); assert row is not None
        payload=dict(row['payload']); payload['child_leaf_arities']=[4,4]
        forged_id='E-NATIVE-STRUCTURAL-SEGMENT-BOUNDED-RECURSIVE-'+result_digest(payload)[:24]
        assert forged_id!=p['composition_state_evidence_id']
        m.append_evidence(forged_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_CONTENT_TAMPER')
        out=m.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason']=='SEGMENT_BOUNDED_RECURSIVE_STATE_CONTENT_OR_CHILD_MISMATCH'
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_current_segment_state_but_rederives_same_mixed_parent_content():
    td=TemporaryDirectory(prefix='segment-arity-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'SEGMENT-ARITY-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens); records=seeded['records']
        _obs(m1,MIXED_SHAPES[(3,4)],276000,'SEGMENT-ARITY-R1')
        b1=m1.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536); assert b1['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b1
        s1=m1.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s1
        p1=m1.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p1
        digest=p1['composition_content_digest_sha256']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='CURRENT_UNCONSUMED_MIXED_BOUNDED_STRUCTURAL_SEGMENT_STATE_REQUIRED',old
        attach_four_runtime_surface(m2,world,'SEGMENT-ARITY-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='SEGMENT-ARITY-R2-FRESH',serial_base=277000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id'])); assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,MIXED_SHAPES[(3,4)],278000,'SEGMENT-ARITY-R2')
        b2=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536); assert b2['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b2
        s2=m2.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s2
        p2=m2.derive_and_record_current_native_structural_segment_bounded_recursive_composition(max_records=65536); assert p2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE_RECORDED',p2
        assert p2['composition_content_digest_sha256']==digest
        assert p2['composition_state_evidence_id']!=p1['composition_state_evidence_id']
        assert p2['child_leaf_arities']==(3,4)
    finally:_close(m2);td.cleanup()


def test_segment_state_creation_does_not_auto_invoke_mixed_bounded_parent_consumer():
    td,m,world,seeded=_setup('SEGMENT-ARITY-NOAUTO')
    try:
        b=_boundary(m,MIXED_SHAPES[(4,3)],279000)
        s=m.derive_and_record_current_native_structural_segment_state(max_records=65536); assert s['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE']
        src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_state)
        assert 'derive_and_record_current_native_structural_segment_bounded_recursive_composition' not in src
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE' not in src
    finally:_close(m);td.cleanup()
