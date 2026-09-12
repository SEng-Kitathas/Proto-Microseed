from pathlib import Path
import tempfile
from microseed import Veya,EpistemicStatus
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_counterpart_name_preference_prototype import derive_counterpart_name_preference,resolve_current_counterpart_name_preference,SOURCE,KIND

def _close(ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()

def _record(ms,text,*,eid,epoch=1,session='S1',turn='T1',counterpart='A'):
    ep=record_conversational_episode(ms,session_id=session,counterpart_id=counterpart,counterpart_epoch=epoch,turn_id=turn,utterance=text,evidence_id=eid)
    assert ep['status']=='OWNED_CONVERSATIONAL_EPISODE_RECORDED_RESEARCH_ONLY',ep
    pref=derive_counterpart_name_preference(ms,episode_evidence_id=eid)
    return ep,pref

def test_rahl_preference_persists_across_restart_without_identity_truth():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-restart-') as td:
        path=Path(td);a=Veya(path)
        ep,p=_record(a,'Hello Veya, you can call me Rahl',eid='E-INTRO')
        assert p['status']=='OWNED_COUNTERPART_CALL_NAME_PREFERENCE_RECORDED_RESEARCH_ONLY'
        assert p['preferred_call_name']=='Rahl'
        assert p['human_identity_truth_authority']=='NONE'
        _close(a)
        b=Veya(path);out=resolve_current_counterpart_name_preference(b,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='CURRENT_COUNTERPART_CALL_NAME_PREFERENCE_RESEARCH_ONLY'
        assert out['preferred_call_name']=='Rahl'
        assert out['human_identity_truth_authority']==out['legal_name_authority']=='NONE'
        _close(b)

def test_later_explicit_preference_replaces_for_current_recall_without_erasing_history():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-replace-') as td:
        ms=Veya(Path(td));_,p1=_record(ms,'you can call me Rahl',eid='E1',turn='T1');_,p2=_record(ms,'call me Rowan',eid='E2',session='S2',turn='T2')
        out=resolve_current_counterpart_name_preference(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['preferred_call_name']=='Rowan'
        assert ms.evidence.get(p1['evidence_id']) is not None and ms.evidence.get(p2['evidence_id']) is not None
        _close(ms)

def test_wrong_counterpart_and_epoch_do_not_reuse_preference():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-current-') as td:
        ms=Veya(Path(td));_record(ms,'you can call me Rahl',eid='E1')
        wrong=resolve_current_counterpart_name_preference(ms,counterpart_id='B',counterpart_epoch=1)
        stale=resolve_current_counterpart_name_preference(ms,counterpart_id='A',counterpart_epoch=2)
        assert wrong['status']=='DEFER_UNKNOWN'
        assert stale['status']=='STALE_COUNTERPART_CALL_NAME_PREFERENCE_RESEARCH_ONLY'
        _close(ms)

def test_ambiguous_or_nonpreference_utterance_cannot_create_binding():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-ambig-') as td:
        ms=Veya(Path(td))
        ep=record_conversational_episode(ms,session_id='S',counterpart_id='A',counterpart_epoch=1,turn_id='T',utterance='Rahl is a name I heard, maybe call me something else',evidence_id='E1')
        out=derive_counterpart_name_preference(ms,episode_evidence_id='E1')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='EXPLICIT_UNAMBIGUOUS_CALL_NAME_PREFERENCE_REQUIRED'
        _close(ms)

def test_generic_or_forged_evidence_cannot_be_preference_source():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-forge-') as td:
        ms=Veya(Path(td));ms.append_evidence('E-G',{'utterance':'you can call me Rahl'},EpistemicStatus.PRESSURE_SUPPORTED,source='OTHER')
        out=derive_counterpart_name_preference(ms,episode_evidence_id='E-G')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='OWNED_CONVERSATIONAL_EPISODE_REQUIRED'
        _close(ms)

def test_preference_record_with_missing_exact_source_fails_closed():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-source-') as td:
        ms=Veya(Path(td));payload={'kind':KIND,'counterpart_id':'A','counterpart_epoch':1,'preferred_call_name':'Rahl','source_episode_evidence_id':'MISSING','source_episode_evidence_sha256':'0'*64,'source_session_id':'S','source_turn_id':'T','preference_semantics':'CURRENT_SELF_DECLARED_CONVERSATIONAL_CALL_NAME_PREFERENCE_ONLY','human_identity_truth_authority':'NONE','legal_name_authority':'NONE','counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY','social_relationship_authority':'NONE','authority_gain':'NONE'}
        ms.append_evidence('E-P',payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE)
        out=resolve_current_counterpart_name_preference(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='EXACT_SOURCE_CONVERSATIONAL_EPISODE_REQUIRED'
        _close(ms)

def test_no_auto_name_binding_from_unrecorded_chamber_style_text():
    with tempfile.TemporaryDirectory(prefix='veya-name-pref-noauto-') as td:
        ms=Veya(Path(td));(Path(td)/'transcript.txt').write_text('you can call me Rahl',encoding='utf-8')
        out=resolve_current_counterpart_name_preference(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN'
        _close(ms)
