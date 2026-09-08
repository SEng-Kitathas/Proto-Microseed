import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def _fixture(tokens=('R4','T9','W3','K7'),sensor_transform=None):
    td=TemporaryDirectory(prefix='prod-boundary-occasion-');root=Path(td.name);world=OpaqueFourLocusWorld()
    if sensor_transform is not None:world.sensor_transform=sensor_transform
    m=Microseed(root);attach_four_runtime_surface(m,world,'PROD-BOUNDARY-OCCASION')
    seeded=seed_four_current_native_referent_associations(m,world,tokens=tokens)
    return td,m,world,seeded


def test_production_unique_extension_conflict_records_retrospective_structural_boundary_witness_only():
    td,m,world,seeded=_fixture()
    try:
        _obs(m,('R4','T9','R4','K7'),'PROD-OCCASION',63000);before=m.evidence.count()
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
        assert out['split_index']==2
        assert out['selection_authority']=='CONTENT_UNIQUENESS_ONLY'
        assert out['caller_supplied_split']==out['caller_supplied_grouping']==out['caller_supplied_output_evidence_id']=='NO'
        assert out['retroactive_composition_rewrite_authority']==out['effect_authority']==out['execution_authority']==out['semantic_grouping_authority']=='NONE'
        assert m.evidence.count()==before+1
        row=m.evidence.get(out['boundary_evidence_id']);assert row is not None
        assert row['payload']['operator_owner']=='MICROSEED_NATIVE_STRUCTURAL_BOUNDARY_OCCASION'
        assert row['payload']['boundary_temporality']=='RETROSPECTIVE_RECOGNITION_AFTER_EXTENSION_CONFLICT'
        # Witness is a boundary fact, not permission to materialize retroactive compositions.
        comp=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert comp['status']=='DEFER_UNKNOWN' and comp['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM' and comp['derived_arity']==0,comp
        again=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert again['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_ALREADY_PRESENT',again
        assert again['boundary_content_digest_sha256']==out['boundary_content_digest_sha256']
        assert m.evidence.count()==before+1
    finally:_close(m);td.cleanup()


def test_production_fully_valid_ambiguous_and_zero_split_cases_write_nothing():
    cases=[
        (('R4','T9','W3','K7'),'NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION','FULL_CURRENT_WINDOW_STRUCTURALLY_ADMISSIBLE',64000),
        (('R4','T9','W3','R4','K7'),'AMBIGUOUS_CURRENT_STRUCTURAL_BOUNDARY_OCCASION','MULTIPLE_TWO_WINDOW_SPLITS_SATISFY_EARNED_SEGMENT_ADMISSIBILITY',65000),
        (('R4','R4','T9','K7'),'NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION','NO_TWO_WINDOW_SPLIT_SATISFIES_EARNED_SEGMENT_ADMISSIBILITY',66000),
    ]
    for seq,status,reason,base in cases:
        td,m,world,seeded=_fixture()
        try:
            _obs(m,seq,'PROD-OCCASION-CONTROL',base);before=m.evidence.count()
            out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
            assert out['status']==status and out['reason']==reason,out
            assert m.evidence.count()==before
        finally:_close(m);td.cleanup()


def test_production_boundary_witness_loses_currentness_after_leaf_drift():
    td,m,world,seeded=_fixture()
    try:
        _obs(m,('R4','T9','R4','K7'),'PROD-OCCASION-STALE',67000)
        first=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert first['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',first
        m.change_capability_dependency('QA',reason='PROD-OCCASION-QA-DRIFT')
        stale=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert stale['status']=='DEFER_UNKNOWN',stale
        assert stale['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'}
    finally:_close(m);td.cleanup()


def test_production_restart_requires_fresh_conflict_and_revalidation_then_rederives_same_content():
    td=TemporaryDirectory(prefix='prod-boundary-occasion-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'PROD-OCCASION-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),'PROD-OCCASION-R1',68000)
        first=m1.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert first['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',first
        digest=first['boundary_content_digest_sha256']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM',old
        attach_four_runtime_surface(m2,world,'PROD-OCCASION-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='PROD-OCCASION-R2-FRESH',serial_base=69000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
            assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),'PROD-OCCASION-R2',70000)
        second=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert second['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',second
        assert second['boundary_content_digest_sha256']==digest
        assert second['boundary_evidence_id']!=first['boundary_evidence_id']
    finally:_close(m2);td.cleanup()


def test_production_structural_boundary_is_representation_invariant():
    def run(tokens=('R4','T9','W3','K7'),sensor_transform=None,base=71000):
        td,m,world,seeded=_fixture(tokens=tokens,sensor_transform=sensor_transform)
        try:
            seq=(tokens[0],tokens[1],tokens[0],tokens[3])
            _obs(m,seq,'PROD-OCCASION-INVAR',base)
            out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
            assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
            return out['boundary_content_digest_sha256'],out['split_index'],out['ordered_operational_referent_signatures']
        finally:_close(m);td.cleanup()
    a=run(base=71000)
    b=run(tokens=('K7','R4','T9','W3'),base=72000)
    p=run(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=73000)
    inv=run(sensor_transform=lambda row:tuple(-x for x in row),base=74000)
    assert a==b==p==inv


def test_production_method_exposes_budgets_only_not_grouping_controls():
    sig=inspect.signature(Microseed.derive_and_record_current_native_structural_boundary_occasion)
    assert tuple(sig.parameters)==('self','max_records','max_events')
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_boundary_occasion)
    assert 'min_segment=2; max_segment=4; max_window=8' in src
    for forbidden in ('split_index:', 'grouping:', 'token_operands:', 'output_evidence_id:', 'min_segment:', 'max_segment:', 'max_window:'):
        assert forbidden not in str(sig)
