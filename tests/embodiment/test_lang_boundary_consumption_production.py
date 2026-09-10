from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed import Authority,EpistemicStatus,Microseed,Observation
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _setup(tag='PROD-BOUNDARY-CONSUME',tokens=('R4','T9','W3','K7'),sensor_transform=None,root=None):
    td=None
    if root is None:
        td=TemporaryDirectory(prefix='prod-boundary-consume-');root=Path(td.name)
    world=OpaqueFourLocusWorld()
    if sensor_transform is not None:world.sensor_transform=sensor_transform
    m=Microseed(root);attach_four_runtime_surface(m,world,tag)
    seeded=seed_four_current_native_referent_associations(m,world,tokens=tokens)
    return td,m,world,seeded

def _obs(m,seq,base,phase='PROD-BOUNDARY-CONSUME'):
    for i,t in enumerate(seq):
        r=observe_opaque_token(m,t,base+i,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r

def _boundary(m,seq,base):
    reset=m.observe_opaque_control_state(
        Observation(f'CAP-STRUCTURAL-WINDOW-{base}','EXTERNAL','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-STRUCTURAL-WINDOW-{base}',
    )
    assert reset['status']=='CURRENT_OPAQUE_CONTROL_STATE',reset
    _obs(m,seq,base)
    out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
    assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
    return out

def _direct_digest(seq,base):
    td,m,world,seeded=_setup('PROD-BOUNDARY-CONSUME-DIRECT')
    try:
        _obs(m,seq,base,'PROD-BOUNDARY-CONSUME-DIRECT')
        out=m.derive_and_record_current_native_bounded_ordered_composition(max_records=65536,max_events=65536)
        assert out['status']=='CURRENT_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_RECORDED',out
        return out['composition_content_digest_sha256'],out['ordered_operational_referent_signatures']
    finally:_close(m);td.cleanup()


def test_production_segment_state_consumes_boundary_append_only_and_reuses_exact_bounded_composition_identity():
    left_digest,left_sigs=_direct_digest(('R4','T9'),111000)
    right_digest,right_sigs=_direct_digest(('R4','K7'),112000)
    td,m,world,seeded=_setup()
    try:
        b=_boundary(m,('R4','T9','R4','K7'),113000)
        ids_before=tuple(r['evidence_id'] for r in m.evidence.list())
        ordinary_before=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        out=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        ids_after=tuple(r['evidence_id'] for r in m.evidence.list())
        ordinary_after=[r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_BOUNDED_ORDERED_OPERATIONAL_REFERENCE_COMPOSITION_EVIDENCE']
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',out
        assert ids_after[:-1]==ids_before and ids_after[-1]==out['segment_state_evidence_id']
        assert len(ordinary_after)==len(ordinary_before)==0
        assert out['boundary_evidence_id']==b['boundary_evidence_id']
        assert out['left_composition_content_digest_sha256']==left_digest
        assert out['right_composition_content_digest_sha256']==right_digest
        assert tuple(out['left_content']['ordered_operational_referent_signatures'])==left_sigs
        assert tuple(out['right_content']['ordered_operational_referent_signatures'])==right_sigs
        assert out['ledger_rewrite_authority']==out['historical_event_authority']==out['effect_authority']==out['execution_authority']==out['semantic_grouping_authority']=='NONE'
        again=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert again['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_ALREADY_PRESENT',again
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids_after
    finally:_close(m);td.cleanup()


def test_production_delayed_two_boundary_consumption_is_oldest_first_and_invocation_order_independent_of_content():
    td,m,world,seeded=_setup('PROD-BOUNDARY-CONSUME-QUEUE')
    try:
        a=_boundary(m,('R4','T9','R4','K7'),114000)
        b=_boundary(m,('T9','W3','T9','R4'),114100)
        first=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        second=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        third=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert first['status']==second['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED'
        assert first['boundary_evidence_id']==a['boundary_evidence_id']
        assert second['boundary_evidence_id']==b['boundary_evidence_id']
        assert first['selection_basis']==second['selection_basis']=='OLDEST_CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_BY_EVIDENCE_APPEND_ORDER'
        assert third['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_ALREADY_PRESENT'
        assert third['boundary_evidence_id']==b['boundary_evidence_id']
    finally:_close(m);td.cleanup()


def test_production_forged_segment_state_payload_under_arbitrary_id_is_refused():
    td,m,world,seeded=_setup('PROD-BOUNDARY-CONSUME-FORGE')
    try:
        b=_boundary(m,('R4','T9','R4','K7'),115000)
        valid=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert valid['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',valid
        row=m.evidence.get(valid['segment_state_evidence_id']);assert row is not None
        payload=dict(row['payload'])
        m.append_evidence('E-FORGED-COPIED-SEGMENT-STATE',payload,EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-FORGERY')
        out=m.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='SEGMENT_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT',out
    finally:_close(m);td.cleanup()


def test_production_state_currentness_tracks_boundary_leaf_support_and_restart():
    td=TemporaryDirectory(prefix='prod-boundary-consume-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'PROD-CONSUME-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),116000,'PROD-CONSUME-R1')
        b1=m1.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b1['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b1
        s1=m1.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s1
        digest=s1['segment_state_content_digest_sha256']
        m1.change_capability_dependency('QA',reason='PROD-CONSUME-QA-DRIFT')
        stale=m1.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert stale['status']=='DEFER_UNKNOWN' and stale['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'},stale
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_structural_segment_state(max_records=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='CURRENT_UNCONSUMED_STRUCTURAL_BOUNDARY_WITNESS_REQUIRED',old
        attach_four_runtime_surface(m2,world,'PROD-CONSUME-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='PROD-CONSUME-R2-FRESH',serial_base=117000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']));assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),118000,'PROD-CONSUME-R2')
        b2=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536);assert b2['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',b2
        s2=m2.derive_and_record_current_native_structural_segment_state(max_records=65536);assert s2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',s2
        assert s2['segment_state_content_digest_sha256']==digest
        assert s2['segment_state_evidence_id']!=s1['segment_state_evidence_id']
    finally:_close(m2);td.cleanup()


def test_production_segment_state_representation_invariant():
    def run(tokens=('R4','T9','W3','K7'),sensor_transform=None,base=119000):
        td,m,world,seeded=_setup('PROD-CONSUME-INVAR',tokens=tokens,sensor_transform=sensor_transform)
        try:
            seq=(tokens[0],tokens[1],tokens[0],tokens[3]);_boundary(m,seq,base)
            out=m.derive_and_record_current_native_structural_segment_state(max_records=65536);assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_STATE_RECORDED',out
            return out['segment_state_content_digest_sha256'],out['left_content'],out['right_content']
        finally:_close(m);td.cleanup()
    a=run(base=119000)
    b=run(tokens=('K7','R4','T9','W3'),base=120000)
    p=run(sensor_transform=lambda row:(row[6],row[7],row[0],row[1],row[2],row[3],row[4],row[5]),base=121000)
    inv=run(sensor_transform=lambda row:tuple(-x for x in row),base=122000)
    assert a==b==p==inv


def test_production_consumer_surface_has_budget_only_no_grouping_or_boundary_selector_parameters():
    sig=inspect.signature(Microseed.derive_and_record_current_native_structural_segment_state)
    assert tuple(sig.parameters)==('self','max_records')
    src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_state).lower()
    assert 'oldest_current_unconsumed_structural_boundary_by_evidence_append_order' in src
    for forbidden in ('boundary_id:', 'split_index:', 'grouping:', 'segment_operands:', 'output_evidence_id:', 'execute_bounded_action(', 'nominate_bounded_action_intent(', 'scheduler', 'planner'):
        assert forbidden not in str(sig).lower()
