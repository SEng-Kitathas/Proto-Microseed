from pathlib import Path
import tempfile
from microseed import Veya
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_recurrent_counterpart_interaction_prototype import derive_recurrent_counterpart_interaction,resolve_current_recurrent_counterpart_interaction

def _close(ms):
    ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()

def _ep(ms,sid,turn,text='hello',counterpart='A',epoch=1):
    out=record_conversational_episode(ms,session_id=sid,counterpart_id=counterpart,counterpart_epoch=epoch,turn_id=turn,utterance=text)
    assert out['status']=='OWNED_CONVERSATIONAL_EPISODE_RECORDED_RESEARCH_ONLY',out
    return out

def test_two_distinct_sessions_earn_recurrent_interaction_without_relationship_claim():
    with tempfile.TemporaryDirectory(prefix='veya-m03-two-') as td:
        ms=Veya(Path(td));_ep(ms,'S1','T1');_ep(ms,'S2','T1')
        out=derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='OWNED_RECURRENT_COUNTERPART_INTERACTION_RECORDED_RESEARCH_ONLY',out
        assert out['distinct_session_count']==2
        assert out['friendship_authority']==out['trust_authority']==out['attachment_authority']==out['relationship_type_authority']=='NONE'
        _close(ms)

def test_duplicate_episodes_in_one_session_do_not_inflate_distinct_session_requirement():
    with tempfile.TemporaryDirectory(prefix='veya-m03-dupe-') as td:
        ms=Veya(Path(td));_ep(ms,'S1','T1');_ep(ms,'S1','T2');_ep(ms,'S1','T3')
        out=derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['distinct_session_count']==1
        _close(ms)

def test_recurrent_interaction_persists_across_restart():
    with tempfile.TemporaryDirectory(prefix='veya-m03-restart-') as td:
        path=Path(td);a=Veya(path);_ep(a,'S1','T1');_ep(a,'S2','T1');rec=derive_recurrent_counterpart_interaction(a,counterpart_id='A',counterpart_epoch=1);assert rec['status'].startswith('OWNED_');_close(a)
        b=Veya(path);out=resolve_current_recurrent_counterpart_interaction(b,counterpart_id='A',counterpart_epoch=1);assert out['status']=='CURRENT_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY';assert out['distinct_session_count']==2;_close(b)

def test_wrong_counterpart_and_epoch_do_not_reuse_interaction_relation():
    with tempfile.TemporaryDirectory(prefix='veya-m03-current-') as td:
        ms=Veya(Path(td));_ep(ms,'S1','T1');_ep(ms,'S2','T1');derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        wrong=resolve_current_recurrent_counterpart_interaction(ms,counterpart_id='B',counterpart_epoch=1)
        stale=resolve_current_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=2)
        assert wrong['status']=='DEFER_UNKNOWN';assert stale['status']=='STALE_RECURRENT_COUNTERPART_INTERACTION_RESEARCH_ONLY';_close(ms)

def test_many_sessions_still_do_not_create_friendship_trust_attachment_or_importance():
    with tempfile.TemporaryDirectory(prefix='veya-m03-many-') as td:
        ms=Veya(Path(td))
        for i in range(12):_ep(ms,f'S{i}','T1',text=f'hello {i}')
        rec=derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        out=resolve_current_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        assert rec['distinct_session_count']==12 and out['distinct_session_count']==12
        for k in ['friendship_authority','trust_authority','attachment_authority','social_valence_authority','importance_authority','relationship_type_authority']:
            assert out[k]=='NONE'
        _close(ms)

def test_external_transcript_or_unowned_evidence_does_not_create_recurrent_relation():
    with tempfile.TemporaryDirectory(prefix='veya-m03-noauto-') as td:
        path=Path(td);ms=Veya(path);(path/'echo-transcript.txt').write_text('session1\nsession2',encoding='utf-8')
        out=derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN';_close(ms)

def test_relation_counts_historical_episodes_but_claim_is_repeated_interaction_only():
    with tempfile.TemporaryDirectory(prefix='veya-m03-count-') as td:
        ms=Veya(Path(td));_ep(ms,'S1','T1');_ep(ms,'S1','T2');_ep(ms,'S2','T1')
        rec=derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        out=resolve_current_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
        assert rec['episode_count']==3 and rec['distinct_session_count']==2
        assert out['interaction_semantics']=='REPEATED_OBSERVED_CONVERSATIONAL_INTERACTION_ONLY'
        assert out['human_identity_truth_authority']=='NONE';_close(ms)
