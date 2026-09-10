from pathlib import Path
from tempfile import TemporaryDirectory
import inspect

from microseed import EpistemicStatus,Microseed
from microseed.development.action_closure import result_digest
from tests.embodiment.test_lang_boundary_consumption_production import _setup,_obs,_close
from tests.embodiment.test_lang_segment_parent_operand_prototype import _b2_parent,_mixed_parent
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,seed_four_current_native_referent_associations
from tests.embodiment.test_lang_segment_operand_bounded_arity_production import MIXED_SHAPES


def _depth_two(m,base=320000):
    _b1,_s1,p1=_b2_parent(m,base)
    _b2,_s2,p2=_mixed_parent(m,(3,4),base+1000)
    out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
    return p1,p2,out


def test_production_depth_two_parent_preserves_each_depth_one_parent_as_one_nested_child():
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROD')
    try:
        before=tuple(r['evidence_id'] for r in m.evidence.list())
        p1,p2,out=_depth_two(m)
        after=tuple(r['evidence_id'] for r in m.evidence.list())
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['composition_depth']==2 and out['child_arity']==2 and out['input_parent_depth']==1
        assert out['ordered_child_composition_content_digests']==(p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'])
        assert tuple(c['source_parent_kind'] for c in out['children'])==(
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE',
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE')
        assert tuple(c['composition_depth'] for c in out['children'])==(1,1)
        assert all(len(c['nested_children'])==2 for c in out['children'])
        assert after[:len(before)]==before and after[-1]==out['composition_state_evidence_id']
        row=m.evidence.get(out['composition_state_evidence_id']); assert row is not None
        payload=row['payload']
        assert len(payload['ordered_child_composition_content_digests'])==2
        assert all(len(c['nested_child_content_digests'])==2 for c in payload['children'])
        assert payload['composition_depth']==2 and payload['child_arity']==2
        assert payload['flattening_authority']==payload['associativity_authority']=='NONE'
        assert payload['generic_recursive_closure_authority']==payload['depth_three_authority']=='NONE'
        assert payload['historical_event_authority']==payload['scheduler_authority']==payload['effect_authority']=='NONE'
    finally:_close(m);td.cleanup()


def _ordered_depth_two(order):
    td,m,world,seeded=_setup('SEGMENT-PARENT-PROD-ORDER-'+order)
    try:
        if order=='B2_MIXED':
            p1=_b2_parent(m,322000)[2]; p2=_mixed_parent(m,(2,4),323000)[2]
        else:
            p1=_mixed_parent(m,(2,4),322000)[2]; p2=_b2_parent(m,323000)[2]
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        return out['composition_content_digest_sha256'],out['ordered_child_composition_content_digests'],(p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'])
    finally:_close(m);td.cleanup()


def test_depth_two_order_is_evidence_owned_and_noncommutative():
    a=_ordered_depth_two('B2_MIXED'); b=_ordered_depth_two('MIXED_B2')
    assert a[1]==a[2] and b[1]==b[2]
    assert a[1]==tuple(reversed(b[1]))
    assert a[0]!=b[0]


def test_latest_two_distinct_depth_one_parents_are_selected_not_oldest_pair():
    td,m,world,seeded=_setup('SEGMENT-PARENT-LATEST')
    try:
        p0=_b2_parent(m,324000)[2]
        p1=_mixed_parent(m,(2,3),325000)[2]
        p2=_mixed_parent(m,(4,2),326000)[2]
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert out['ordered_child_composition_content_digests']==(p1['composition_content_digest_sha256'],p2['composition_content_digest_sha256'])
        assert p0['composition_content_digest_sha256'] not in out['ordered_child_composition_content_digests']
        assert out['selection_basis']=='LATEST_TWO_DISTINCT_CURRENT_DEPTH_ONE_RETROSPECTIVE_SEGMENT_PARENT_CONTENTS_IN_EVIDENCE_ORDER'
    finally:_close(m);td.cleanup()


def test_depth_two_recording_is_idempotent_and_deterministic():
    td,m,world,seeded=_setup('SEGMENT-PARENT-IDEMP')
    try:
        _p1,_p2,out=_depth_two(m,327000)
        ids=tuple(r['evidence_id'] for r in m.evidence.list())
        again=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert again['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',again
        assert again['composition_state_record_status']=='SEGMENT_DEPTH_TWO_STATE_ALREADY_PRESENT'
        assert again['composition_state_evidence_id']==out['composition_state_evidence_id']
        assert again['composition_content_digest_sha256']==out['composition_content_digest_sha256']
        assert tuple(r['evidence_id'] for r in m.evidence.list())==ids
    finally:_close(m);td.cleanup()


def test_copied_valid_depth_two_payload_under_new_id_is_refused():
    td,m,world,seeded=_setup('SEGMENT-PARENT-FORGE')
    try:
        _p1,_p2,out=_depth_two(m,329000)
        row=m.evidence.get(out['composition_state_evidence_id']); assert row is not None
        m.append_evidence('E-FORGED-DEPTH-TWO-PARENT',dict(row['payload']),EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE_COPY')
        again=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert again['status']=='DEFER_UNKNOWN',again
        assert again['reason']=='SEGMENT_DEPTH_TWO_STATE_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT'
    finally:_close(m);td.cleanup()


def test_nested_currentness_drift_invalidates_depth_two_parent_reuse():
    td,m,world,seeded=_setup('SEGMENT-PARENT-DRIFT')
    try:
        _depth_two(m,331000)
        m.change_capability_dependency('QA',reason='SEGMENT-PARENT-QA-DRIFT')
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_PROFILE_NOT_CURRENT_EXACT_SOURCE','STRUCTURAL_BOUNDARY_ASSOCIATION_NOT_CURRENT'},out
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_depth_one_parents_but_rederives_same_depth_two_content():
    td=TemporaryDirectory(prefix='segment-parent-restart-'); root=Path(td.name); world=OpaqueFourLocusWorld(); tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'SEGMENT-PARENT-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens); records=seeded['records']
        _b2_parent(m1,333000); _mixed_parent(m1,(3,4),334000)
        p1=m1.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536); assert p1['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',p1
        digest=p1['composition_content_digest_sha256']; eid=p1['composition_state_evidence_id']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        old=m2.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert old['status']=='DEFER_UNKNOWN' and old['reason']=='TWO_DISTINCT_CURRENT_DEPTH_ONE_SEGMENT_PARENT_CONTENTS_REQUIRED',old
        attach_four_runtime_surface(m2,world,'SEGMENT-PARENT-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='SEGMENT-PARENT-R2-FRESH',serial_base=335000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id'])); assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _b2_parent(m2,336000); _mixed_parent(m2,(3,4),337000)
        p2=m2.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536); assert p2['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',p2
        assert p2['composition_content_digest_sha256']==digest
        assert p2['composition_state_evidence_id']!=eid
    finally:_close(m2);td.cleanup()


def test_depth_two_output_is_not_an_eligible_input_to_its_own_owner():
    td,m,world,seeded=_setup('SEGMENT-PARENT-NO-CLOSURE')
    try:
        _depth_two(m,338000)
        _mixed_parent(m,(4,3),340000)
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=65536)
        assert out['status']=='CURRENT_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE_RECORDED',out
        assert all(c['source_parent_kind'] in {
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_B2_RECURSIVE_COMPOSITION_STATE',
            'OWNED_NATIVE_STRUCTURAL_SEGMENT_BOUNDED_RECURSIVE_COMPOSITION_STATE'} for c in out['children'])
        assert all(c['composition_depth']==1 for c in out['children'])
        src=inspect.getsource(Microseed.derive_and_record_current_native_structural_segment_depth_two_recursive_composition)
        accepted_block=src[src.index('accepted={'):src.index('for pos,row')]
        assert 'OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE' not in accepted_block
        assert out['generic_recursive_closure_authority']==out['depth_three_authority']=='NONE'
    finally:_close(m);td.cleanup()


def test_depth_two_budget_exhaustion_is_not_false_saturation():
    td,m,world,seeded=_setup('SEGMENT-PARENT-BUDGET')
    try:
        _b2_parent(m,341000); _mixed_parent(m,(2,3),342000)
        total=m.evidence.count(); assert total>0
        out=m.derive_and_record_current_native_structural_segment_depth_two_recursive_composition(max_records=total-1)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED',out
        assert out['reason']=='SEGMENT_DEPTH_TWO_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET'
        assert out['total_records']==total and out['max_records']==total-1
    finally:_close(m);td.cleanup()


def test_depth_one_parent_creation_does_not_auto_schedule_depth_two_consumer():
    td,m,world,seeded=_setup('SEGMENT-PARENT-NOAUTO')
    try:
        _b2_parent(m,343000); _mixed_parent(m,(2,4),344000)
        assert not [r for r in m.evidence.list() if (r.get('payload') or {}).get('kind')=='OWNED_NATIVE_STRUCTURAL_SEGMENT_DEPTH_TWO_RECURSIVE_COMPOSITION_STATE']
        for method in (Microseed.derive_and_record_current_native_structural_segment_b2_recursive_composition,Microseed.derive_and_record_current_native_structural_segment_bounded_recursive_composition):
            src=inspect.getsource(method)
            assert 'derive_and_record_current_native_structural_segment_depth_two_recursive_composition' not in src
    finally:_close(m);td.cleanup()


def test_nested_identity_differs_from_flattened_and_alternate_regrouping_identities():
    td,m,world,seeded=_setup('SEGMENT-PARENT-GROUPING')
    try:
        _p1,_p2,out=_depth_two(m,345000)
        row=m.evidence.get(out['composition_state_evidence_id']); assert row is not None
        children=row['payload']['children']; grand=[d for c in children for d in c['nested_child_content_digests']]
        assert len(grand)==4
        flattened=result_digest({
            'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE',
            'ordered_child_composition_content_digests':grand,
            'composition_depth':2,'child_arity':4,
            'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY'})
        def d1(pair):
            return result_digest({'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE','ordered_child_composition_content_digests':list(pair),'composition_depth':1,'child_arity':2,'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY'})
        alt_children=(d1((grand[0],grand[2])),d1((grand[1],grand[3])))
        alternate=result_digest({'operator':'RECURSIVE_ORDERED_EVIDENCE_TUPLE','ordered_child_composition_content_digests':list(alt_children),'composition_depth':2,'child_arity':2,'identity_scope':'EXACT_GROUPED_OPERATIONAL_COMPOSITION_ONLY'})
        assert out['composition_content_digest_sha256']!=flattened
        assert out['composition_content_digest_sha256']!=alternate
        assert row['payload']['flattening_authority']==row['payload']['associativity_authority']=='NONE'
    finally:_close(m);td.cleanup()
