from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import EpistemicStatus,Microseed
from scratch.lang_arity_four_grounded_referents_fixture import OpaqueFourLocusWorld,attach_four_runtime_surface,seed_four_current_native_referent_associations,_close
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token


def _obs(m,token,idx,phase='PROD-OCCASION-HOSTILE'):
    r=observe_opaque_token(m,token,idx,phase=phase);assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
    return r


def _fixture():
    td=TemporaryDirectory(prefix='prod-boundary-occasion-hostile-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    attach_four_runtime_surface(m,world,'PROD-OCCASION-HOSTILE')
    seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
    return td,m,world


def test_repeated_invocation_after_each_prefix_records_nothing_until_unique_conflict_and_matches_end_only_witness():
    td,m,world=_fixture()
    try:
        seq=('R4','T9','R4','K7');early=[]
        for i,t in enumerate(seq):
            _obs(m,t,75000+i)
            out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
            if i<3:
                assert out['status'] in {'DEFER_UNKNOWN','NO_CURRENT_STRUCTURAL_BOUNDARY_OCCASION'},out
                early.append((out['status'],out.get('reason')))
            else:
                assert out['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',out
                greedy=out
        assert all((row.get('payload') or {}).get('kind')!='OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS' for row in m.evidence.list()[:-1])
    finally:_close(m);td.cleanup()

    td2,m2,world2=_fixture()
    try:
        for i,t in enumerate(seq):_obs(m2,t,76000+i)
        end=m2.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert end['status']=='CURRENT_NATIVE_STRUCTURAL_BOUNDARY_WITNESS_RECORDED',end
        assert end['boundary_content_digest_sha256']==greedy['boundary_content_digest_sha256']
        assert end['split_index']==greedy['split_index']==2
        assert end['ordered_operational_referent_signatures']==greedy['ordered_operational_referent_signatures']
    finally:_close(m2);td2.cleanup()


def test_forged_current_boot_boundary_witness_is_refused_before_new_inference():
    td,m,world=_fixture()
    try:
        m.append_evidence('E-FORGED-PROD-BOUNDARY',{
            'kind':'OWNED_NATIVE_STRUCTURAL_COMPOSITION_WINDOW_BOUNDARY_WITNESS',
            'runtime_boot_seq':m._current_runtime_boot_seq(),
            'operator_owner':'MICROSEED_NATIVE_STRUCTURAL_BOUNDARY_OCCASION',
            'boundary_basis':'EXACT_ONE_TWO_WINDOW_SPLIT_RESTORES_EARNED_DISTINCT_OPERAND_ADMISSIBILITY',
            'boundary_temporality':'RETROSPECTIVE_RECOGNITION_AFTER_EXTENSION_CONFLICT',
            'retroactive_composition_rewrite_authority':'NONE','effect_authority':'NONE','execution_authority':'NONE','semantic_grouping_authority':'NONE',
            'components':[],'split_index':2,'boundary_content_digest_sha256':'0'*64,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE-FORGERY')
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN',out
        assert out['reason'] in {'STRUCTURAL_BOUNDARY_WITNESS_EVIDENCE_ID_NOT_DERIVED_FROM_CONTENT','STRUCTURAL_BOUNDARY_UNIQUE_SPLIT_NO_LONGER_HOLDS','STRUCTURAL_BOUNDARY_CONTENT_DIGEST_MISMATCH'}
    finally:_close(m);td.cleanup()


def test_replayed_token_evidence_event_blocks_production_structural_boundary_inference():
    td,m,world=_fixture()
    try:
        rows=[]
        for i,t in enumerate(('R4','T9','R4','K7')):rows.append(_obs(m,t,77000+i))
        eid=rows[1]['evidence_id'];ev=[e for e in m.store.events() if e.get('kind')=='EVIDENCE' and (e.get('payload') or {}).get('evidence_id')==eid][-1]
        m.store.append('EVIDENCE',dict(ev['payload']))
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='OPERAND_WINDOW_EVIDENCE_EVENT_REPLAY_DETECTED',out
    finally:_close(m);td.cleanup()


def test_evidence_and_event_budgets_fail_closed_before_partial_structural_inference():
    td,m,world=_fixture()
    try:
        for i,t in enumerate(('R4','T9','R4','K7')):_obs(m,t,78000+i)
        total=m.evidence.count();out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=total-1,max_events=65536)
        assert out['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED' and out['reason']=='STRUCTURAL_BOUNDARY_EVIDENCE_HISTORY_EXCEEDS_SCAN_BUDGET',out
        boot=m._current_runtime_boot_seq();current=[e for e in m.store.events() if int(e.get('seq',-1))>boot]
        out2=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=len(current)-1)
        assert out2['status']=='SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED' and out2['reason']=='OPERAND_WINDOW_EVENT_HISTORY_EXCEEDS_SCAN_BUDGET',out2
    finally:_close(m);td.cleanup()


def test_nine_token_window_is_visible_and_refused_not_cropped_into_a_structural_split():
    td,m,world=_fixture()
    try:
        seq=('R4','T9','W3','K7','R4','T9','W3','K7','R4')
        for i,t in enumerate(seq):_obs(m,t,79000+i)
        out=m.derive_and_record_current_native_structural_boundary_occasion(max_records=65536,max_events=65536)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='BOUNDED_OPERAND_WINDOW_EXCEEDS_MAXIMUM',out
        assert out['derived_arity']==9
        assert out['bounded_max_structural_window']==8
    finally:_close(m);td.cleanup()
