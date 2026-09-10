from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import EpistemicStatus,Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_boundary_occasion_unique_structural_split_prototype import record_unique_structural_boundary_witness_prototype


def _obs(m,tokens,phase,base):
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r


def test_unique_structural_conflict_records_exact_durable_boundary_witness_but_does_not_retroactively_compose():
    td=TemporaryDirectory(prefix='boundary-witness-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-WITNESS')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _obs(m,('R4','T9','R4','K7'),'BOUNDARY-WITNESS',56000)
        before=m.evidence.count()
        out=record_unique_structural_boundary_witness_prototype(m)
        assert out['status']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
        assert out['record_status']=='BOUNDARY_WITNESS_RECORDED'
        assert out['split_index']==2
        assert out['caller_supplied_split']==out['caller_supplied_output_evidence_id']=='NO'
        assert out['retroactive_composition_rewrite_authority']==out['effect_authority']==out['execution_authority']==out['semantic_grouping_authority']=='NONE'
        assert m.evidence.count()==before+1
        row=m.evidence.get(out['boundary_evidence_id']);assert row is not None
        payload=row['payload']
        assert payload['kind']=='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS'
        assert payload['boundary_content_digest_sha256']==out['boundary_content_digest_sha256']
        assert payload['boundary_temporality']=='RETROSPECTIVE_RECOGNITION_AFTER_EXTENSION_CONFLICT'
        assert len(payload['components'])==4
        assert payload['left_last_token_store_seq']<payload['right_first_token_store_seq']
        # Boundary witness evidence is grouping-neutral. The conflicted source window stays visible;
        # the witness does not authorize a retroactive direct composition or erase chronology.
        composition=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert composition['status']=='DEFER_UNKNOWN' and composition['reason']=='ALL_BOUNDED_REFERENT_OPERANDS_MUST_BE_DISTINCT',composition
        assert composition['derived_arity']==4
        again=record_unique_structural_boundary_witness_prototype(m)
        assert again['status']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_ALREADY_PRESENT',again
        assert again['boundary_content_digest_sha256']==out['boundary_content_digest_sha256']
        assert m.evidence.count()==before+1
    finally:_close(m);td.cleanup()


def test_fully_valid_or_ambiguous_windows_do_not_record_boundary_witness():
    for seq,status,base in [
        (('R4','T9','W3','K7'),'NO_STRUCTURAL_BOUNDARY_OCCASION_REQUIRED',57000),
        (('R4','T9','W3','R4','K7'),'AMBIGUOUS_STRUCTURAL_BOUNDARY_OCCASION',58000),
    ]:
        td=TemporaryDirectory(prefix='boundary-witness-control-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
        try:
            attach_four_runtime_surface(m,world,'BOUNDARY-WITNESS-CONTROL')
            seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
            _obs(m,seq,'BOUNDARY-WITNESS-CONTROL',base);before=m.evidence.count()
            out=record_unique_structural_boundary_witness_prototype(m)
            assert out['status']==status,out
            assert m.evidence.count()==before
        finally:_close(m);td.cleanup()


def test_forged_current_boot_structural_boundary_witness_is_refused():
    td=TemporaryDirectory(prefix='boundary-witness-forged-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-WITNESS-FORGED')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        m.append_evidence('E-FORGED-STRUCTURAL-BOUNDARY',{
            'kind':'OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS',
            'runtime_boot_seq':m._current_runtime_boot_seq(),'components':[],'split_index':2,
            'boundary_content_digest_sha256':'0'*64,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-FORGERY')
        out=record_unique_structural_boundary_witness_prototype(m)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_UNIQUE_SPLIT_NO_LONGER_HOLDS','STRUCTURAL_BOUNDARY_CONTENT_DIGEST_MISMATCH'}
    finally:_close(m);td.cleanup()


def test_persisted_witness_loses_current_status_after_leaf_capability_drift():
    td=TemporaryDirectory(prefix='boundary-witness-stale-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-WITNESS-STALE')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _obs(m,('R4','T9','R4','K7'),'BOUNDARY-WITNESS-STALE',59000)
        first=record_unique_structural_boundary_witness_prototype(m)
        assert first['status']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',first
        m.change_capability_dependency('QA',reason='BOUNDARY-WITNESS-QA-DRIFT')
        stale=record_unique_structural_boundary_witness_prototype(m)
        assert stale['status']=='DEFER_UNKNOWN',stale
        assert stale['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'}
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_window_and_revalidation_then_rederives_same_structural_content():
    td=TemporaryDirectory(prefix='boundary-witness-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'BOUNDARY-WITNESS-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),'BOUNDARY-WITNESS-R1',60000)
        first=record_unique_structural_boundary_witness_prototype(m1)
        assert first['status']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',first
        digest=first['boundary_content_digest_sha256']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=record_unique_structural_boundary_witness_prototype(m2)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM',old
        attach_four_runtime_surface(m2,world,'BOUNDARY-WITNESS-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='BOUNDARY-WITNESS-R2-FRESH',serial_base=61000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
            assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),'BOUNDARY-WITNESS-R2',62000)
        second=record_unique_structural_boundary_witness_prototype(m2)
        assert second['status']=='CURRENT_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',second
        assert second['boundary_content_digest_sha256']==digest
        assert second['boundary_evidence_id']!=first['boundary_evidence_id']
    finally:_close(m2);td.cleanup()
