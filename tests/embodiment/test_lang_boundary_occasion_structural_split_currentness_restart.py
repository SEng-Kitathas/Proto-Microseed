from pathlib import Path
from tempfile import TemporaryDirectory

from microseed import Microseed
from scratch.lang_arity_four_grounded_referents_fixture import (
    OpaqueFourLocusWorld,attach_four_runtime_surface,fresh_four_owned_profiles,
    seed_four_current_native_referent_associations,_close,
)
from scratch.lang_c08e_native_token_relation_binding import observe_opaque_token
from scratch.lang_boundary_occasion_unique_structural_split_prototype import derive_unique_structural_split_candidate


def _obs(m,tokens,phase,base):
    rows=[]
    for i,t in enumerate(tokens):
        r=observe_opaque_token(m,t,base+i,phase=phase)
        assert r['status']=='OPAQUE_TOKEN_OBSERVED_NATIVE_EVIDENCE',r
        rows.append(r)
    return rows


def test_unique_structural_split_disappears_when_any_leaf_profile_becomes_stale():
    td=TemporaryDirectory(prefix='boundary-split-currentness-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-SPLIT-CUR')
        seeded=seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        _obs(m,('R4','T9','R4','K7'),'BOUNDARY-SPLIT-CUR',51000)
        before=derive_unique_structural_split_candidate(m)
        assert before['status']=='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE',before
        assert before['candidate']['split_index']==2
        m.change_capability_dependency('QA',reason='BOUNDARY-SPLIT-QA-DRIFT')
        stale=derive_unique_structural_split_candidate(m)
        assert stale['status']=='DEFER_UNKNOWN' and stale['reason']=='CURRENT_NATIVE_REFERENT_PROFILE_REQUIRED',stale
    finally:_close(m);td.cleanup()


def test_restart_requires_fresh_token_window_and_live_association_revalidation_before_same_split_reappears():
    td=TemporaryDirectory(prefix='boundary-split-restart-');root=Path(td.name);world=OpaqueFourLocusWorld();tokens=('R4','T9','W3','K7')
    m1=Microseed(root)
    try:
        attach_four_runtime_surface(m1,world,'BOUNDARY-SPLIT-R1')
        seeded=seed_four_current_native_referent_associations(m1,world,tokens=tokens);records=seeded['records']
        _obs(m1,('R4','T9','R4','K7'),'BOUNDARY-SPLIT-R1',52000)
        first=derive_unique_structural_split_candidate(m1)
        assert first['status']=='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE',first
        first_sigs=first['referent_signatures'];first_split=first['candidate']['split_index']
    finally:_close(m1)
    m2=Microseed(root)
    try:
        nofresh=derive_unique_structural_split_candidate(m2)
        assert nofresh['status']=='DEFER_UNKNOWN' and nofresh['reason']=='BOUNDED_OPERAND_WINDOW_BELOW_MINIMUM',nofresh
        attach_four_runtime_surface(m2,world,'BOUNDARY-SPLIT-R2')
        profiles=fresh_four_owned_profiles(m2,world,tag='BOUNDARY-SPLIT-R2-FRESH',serial_base=53000)
        for token,key in zip(tokens,('QA','QB','QC','QD')):
            cur=m2.assess_opaque_evidence_association_currentness(records[token],witness_evidence_id=str(profiles[key]['evidence_id']))
            assert cur['status']=='CURRENTNESS_CONFIRMED',cur
        _obs(m2,('R4','T9','R4','K7'),'BOUNDARY-SPLIT-R2',54000)
        second=derive_unique_structural_split_candidate(m2)
        assert second['status']=='CURRENT_UNIQUE_STRUCTURAL_BOUNDARY_OCCASION_CANDIDATE',second
        assert second['candidate']['split_index']==first_split==2
        assert second['referent_signatures']==first_sigs
    finally:_close(m2);td.cleanup()


def test_replayed_token_evidence_store_event_blocks_split_inference():
    td=TemporaryDirectory(prefix='boundary-split-replay-');root=Path(td.name);world=OpaqueFourLocusWorld();m=Microseed(root)
    try:
        attach_four_runtime_surface(m,world,'BOUNDARY-SPLIT-REPLAY')
        seed_four_current_native_referent_associations(m,world,tokens=('R4','T9','W3','K7'))
        rows=_obs(m,('R4','T9','R4','K7'),'BOUNDARY-SPLIT-REPLAY',55000)
        eid=rows[1]['evidence_id']
        ev=[e for e in m.store.events() if e.get('kind')=='EVIDENCE' and (e.get('payload') or {}).get('evidence_id')==eid][-1]
        m.store.append('EVIDENCE',dict(ev['payload']))
        out=derive_unique_structural_split_candidate(m)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='OPERAND_WINDOW_EVIDENCE_EVENT_REPLAY_DETECTED',out
    finally:_close(m);td.cleanup()
