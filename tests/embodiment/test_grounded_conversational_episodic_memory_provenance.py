from pathlib import Path
import tempfile

from microseed import Veya,EpistemicStatus
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode,recall_recent_conversational_episode,KIND,SOURCE


def _close(ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()


def test_episode_persists_across_runtime_restart_and_recalls_only_as_historical_utterance():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-restart-') as td:
        path=Path(td);a=Veya(path)
        rec=record_conversational_episode(a,session_id='SESSION-1',counterpart_id='COUNTERPART-A',counterpart_epoch=3,turn_id='T1',utterance='My favorite shape is a spiral.')
        assert rec['status']=='OWNED_CONVERSATIONAL_EPISODE_RECORDED_RESEARCH_ONLY',rec
        _close(a)
        b=Veya(path)
        out=recall_recent_conversational_episode(b,counterpart_id='COUNTERPART-A',counterpart_epoch=3,current_session_id='SESSION-2')
        assert out['status']=='CURRENT_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY',out
        assert out['source_session_id']=='SESSION-1' and out['current_session_id']=='SESSION-2'
        assert out['recalled_utterance']=='My favorite shape is a spiral.'
        assert out['memory_semantics']=='HISTORICAL_UTTERANCE_RECALL_ONLY'
        assert out['truth_authority']==out['semantic_truth_inference']==out['selfhood_authority']=='NONE'
        _close(b)


def test_wrong_counterpart_does_not_recall_episode():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-wrong-') as td:
        ms=Veya(Path(td));record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='hello')
        out=recall_recent_conversational_episode(ms,counterpart_id='B',counterpart_epoch=1,current_session_id='S2')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='NO_CURRENT_MATCHING_CONVERSATIONAL_EPISODE'
        _close(ms)


def test_counterpart_epoch_change_stales_memory_without_erasing_history():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-stale-') as td:
        ms=Veya(Path(td));rec=record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='hello')
        out=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=2,current_session_id='S2')
        assert out['status']=='STALE_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY' and out['reason']=='COUNTERPART_EPOCH_MISMATCH'
        assert ms.evidence.get(rec['evidence_id']) is not None
        _close(ms)


def test_same_session_recall_is_blocked_by_default_but_explicitly_available():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-session-') as td:
        ms=Veya(Path(td));record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='hello')
        blocked=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='S1')
        allowed=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='S1',allow_same_session=True)
        assert blocked['status']=='DEFER_UNKNOWN' and allowed['status']=='CURRENT_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY'
        _close(ms)


def test_corrupt_owned_episode_fails_closed_instead_of_recalling_plausible_text():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-corrupt-') as td:
        ms=Veya(Path(td));payload={'kind':KIND,'session_id':'S1','counterpart_id':'A','counterpart_epoch':1,'turn_id':'T1','utterance':'hello','utterance_sha256':'0'*64,'episode_identity_sha256':'0'*64,'memory_semantics':'OBSERVED_HISTORICAL_UTTERANCE_EVENT_ONLY','truth_authority':'NONE','counterpart_identity_authority':'OPAQUE_EXPERIMENTAL_ID_ONLY','selfhood_authority':'NONE','semantic_commitment_authority':'NONE'}
        ms.append_evidence('E-CORRUPT-CONV',payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE)
        out=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='S2')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='CONVERSATIONAL_EPISODE_UTTERANCE_HASH_MISMATCH'
        _close(ms)


def test_unowned_or_generic_evidence_does_not_become_conversational_memory():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-unowned-') as td:
        ms=Veya(Path(td));ms.append_evidence('E-GENERIC',{'counterpart_id':'A','utterance':'hello'},EpistemicStatus.PRESSURE_SUPPORTED,source='OTHER')
        out=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='S2')
        assert out['status']=='DEFER_UNKNOWN'
        _close(ms)


def test_external_echo_transcript_file_is_not_auto_ingested():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-no-auto-') as td:
        path=Path(td);ms=Veya(path)
        (path/'echo_transcript.json').write_text('{"counterpart_id":"A","utterance":"remember me"}',encoding='utf-8')
        out=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='S2')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='NO_CURRENT_MATCHING_CONVERSATIONAL_EPISODE'
        _close(ms)


def test_bounded_recent_retrieval_does_not_claim_general_memory_search():
    with tempfile.TemporaryDirectory(prefix='veya-conv-mem-bound-') as td:
        ms=Veya(Path(td))
        for i in range(70): record_conversational_episode(ms,session_id=f'S{i}',counterpart_id='A',counterpart_epoch=1,turn_id=f'T{i}',utterance=f'u{i}')
        out=recall_recent_conversational_episode(ms,counterpart_id='A',counterpart_epoch=1,current_session_id='NEW',limit=64)
        assert out['status']=='CURRENT_CONVERSATIONAL_EPISODIC_MEMORY_RESEARCH_ONLY'
        assert out['recalled_utterance']=='u69' and out['retrieval_scope']=='BOUNDED_RECENT_64_EVIDENCE_ROWS'
        _close(ms)
