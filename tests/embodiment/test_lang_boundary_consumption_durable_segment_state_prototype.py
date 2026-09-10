from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Authority,EpistemicStatus,Microseed,Observation
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_boundary_consumption_durable_segment_state_prototype import record_oldest_unconsumed_structural_segment_state_prototype


def _setup(tag='BOUNDARY-CONSUME-DURABLE',tokens=('R4','T9','W3','K7'),sensor_transform=None,root=None):
    td=None
    if root is None:
        td=TemporaryDirectory(prefix='boundary-consume-durable-');root=Path(td.name)
    world=OpaqueFourLocusWorld()
    if sensor_transform is not None:world.sensor_transform=sensor_transform
    m=Microseed(root);attach_four_runtime_surface(m,world,tag)
    seeded=seed_four_current_native_referent_associations(m,world,tokens=tokens)
    return td,m,world,seeded

def _obs(m,seq,base,phase='BOUNDARY-CONSUME-DURABLE'):
    for i,t in enumerate(seq):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _boundary(m,seq,base):
    reset=m.observe_opaque_control_state(
        Observation(f'CAP-DURABLE-WINDOW-{base}','EXTERNAL','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-DURABLE-WINDOW-{base}',
    )
    assert reset['status']=='CURRENT_OPAQUE_CONTROL_STATE',reset
    _obs(m,seq,base)
    out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
    assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
    return out


def test_durable_segment_state_is_appended_after_boundary_without_historical_ledger_rewrite_or_ordinary_composition_rows():
    td,m,world,seeded=_setup()
    try:
        b=_boundary(m,('R4','T9','R4','K7'),100000)
        ids_before=tuple(r['evidence_id'] for r in m.evidence.list())
        ordinary_before=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        out=record_oldest_unconsumed_structural_segment_state_prototype(m)
        ids_after=tuple(r['evidence_id'] for r in m.evidence.list())
        ordinary_after=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        assert out['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED',out
        assert ids_after[:-1]==ids_before and ids_after[-1]==out['segment_state_evidence_id']
        assert len(ordinary_after)==len(ordinary_before)==0
        assert out['boundary_evidence_id']==b['boundary_evidence_id']
        assert out['ledger_rewrite_authority']==out['historical_event_authority']==out['effect_authority']==out['execution_authority']==out['semantic_grouping_authority']=='NONE'
        again=record_oldest_unconsumed_structural_segment_state_prototype(m)
        assert again['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_ALREADY_PRESENT',again
        assert again['segment_state_content_digest_sha256']==out['segment_state_content_digest_sha256']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids_after
    finally:_close(m);td.cleanup()


def test_delayed_invocation_consumes_multiple_boundaries_oldest_first_by_persisted_chronology():
    td,m,world,seeded=_setup('BOUNDARY-CONSUME-QUEUE')
    try:
        a=_boundary(m,('R4','T9','R4','K7'),101000)
        b=_boundary(m,('T9','W3','T9','R4'),101100)
        first=record_oldest_unconsumed_structural_segment_state_prototype(m)
        second=record_oldest_unconsumed_structural_segment_state_prototype(m)
        third=record_oldest_unconsumed_structural_segment_state_prototype(m)
        assert first['status']==second['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED'
        assert first['boundary_evidence_id']==a['boundary_evidence_id']
        assert second['boundary_evidence_id']==b['boundary_evidence_id']
        assert first['selection_basis']==second['selection_basis']=='OLDEST_CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_BY_EVIDENCE_APPEND_ORDER'
        assert third['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_ALREADY_PRESENT'
        assert third['boundary_evidence_id']==b['boundary_evidence_id']
    finally:_close(m);td.cleanup()


def test_forged_current_segment_state_blocks_consumption_instead_of_suppressing_or_redirecting_boundary():
    td,m,world,seeded=_setup('BOUNDARY-CONSUME-FORGE')
    try:
        b=_boundary(m,('R4','T9','R4','K7'),102000)
        m.append_evidence('E-FORGED-SEGMENT-STATE',{
            'kind':'OWNED_NATIVE_STRUCTURAL_SEGMENT_COMPOSITION_STATE','runtime_boot_seq':m._current_runtime_boot_seq(),
            'operator_owner':'MICROSEED_NATIVE_STRUCTURAL_BOUNDARY_CONSUMPTION','temporality':'CURRENT_RETROSPECTIVE_DERIVATION_APPENDED_AFTER_BOUNDARY',
            'boundary_evidence_ref':[b['boundary_evidence_id'],b['boundary_evidence_sha256']],
            'left_content':{},'right_content':{},'segment_state_content':{},'segment_state_content_digest_sha256':'0'*64,
            'ledger_rewrite_authority':'NONE','historical_event_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE',
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-FORGERY')
        out=record_oldest_unconsumed_structural_segment_state_prototype(m)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'SEGMENT_STATE_COMPOSITION_CONTENT_MISMATCH','SEGMENT_STATE_CONTENT_DIGEST_MISMATCH'}
    finally:_close(m);td.cleanup()


def test_persisted_segment_state_loses_current_status_when_boundary_leaf_support_drifts():
    td,m,world,seeded=_setup('BOUNDARY-CONSUME-STALE')
    try:
        _boundary(m,('R4','T9','R4','K7'),103000)
        first=record_oldest_unconsumed_structural_segment_state_prototype(m)
        assert first['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED',first
        m.change_capability_dependency('QA',reason='BOUNDARY-CONSUME-QA-DRIFT')
        stale=record_oldest_unconsumed_structural_segment_state_prototype(m)
        assert stale['status']=='DEFER_UNKNOWN',stale
        assert stale['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'}
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_boundary_and_revalidation_then_rederives_same_segment_state_content():
    td=TemporaryDirectory(prefix='boundary-consume-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'BOUNDARY-CONSUME-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),104000,'BOUNDARY-CONSUME-R1')
        b1=m1.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b1['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b1
        s1=record_oldest_unconsumed_structural_segment_state_prototype(m1);assert s1['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED',s1
        digest=s1['segment_state_content_digest_sha256']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=record_oldest_unconsumed_structural_segment_state_prototype(m2)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_WITNESS_REQUIRED',old
        attach_four_runtime_surface(m2,world,'BOUNDARY-CONSUME-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='BOUNDARY-CONSUME-R2-FRESH',serial_base=105000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']));assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),106000,'BOUNDARY-CONSUME-R2')
        b2=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b2['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b2
        s2=record_oldest_unconsumed_structural_segment_state_prototype(m2);assert s2['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED',s2
        assert s2['segment_state_content_digest_sha256']==digest
        assert s2['segment_state_evidence_id']!=s1['segment_state_evidence_id']
    finally:_close(m2);td.cleanup()


def test_segment_state_content_is_representation_invariant():
    def run(tokens=('R4','T9','W3','K7'),sensor_transform=None,base=107000):
        td,m,world,seeded=_setup('BOUNDARY-CONSUME-INVAR',tokens=tokens,sensor_transform=sensor_transform)
        try:
            seq=(tokens[0],tokens[1],tokens[0],tokens[3]);_boundary(m,seq,base)
            out=record_oldest_unconsumed_structural_segment_state_prototype(m);assert out['status']=='CURRENT_STRUCTURAL_SEGMENT_STATE_RECORDED',out
            return out['segment_state_content_digest_sha256'],out['left_content'],out['right_content']
        finally:_close(m);td.cleanup()
    a=run(base=107000)
    b=run(tokens=('K7','R4','T9','W3'),base=108000)
    p=run(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=109000)
    inv=run(sensor_transform=lambda row:tuple(-x for x in row),base=110000)
    assert a==b==p==inv
