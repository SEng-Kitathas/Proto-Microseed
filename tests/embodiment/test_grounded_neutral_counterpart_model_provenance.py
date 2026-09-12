from pathlib import Path
import tempfile
from microseed import Veya
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_counterpart_name_preference_prototype import derive_counterpart_name_preference
from scratch.grounded_recurrent_counterpart_interaction_prototype import derive_recurrent_counterpart_interaction
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model

def _close(ms):ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()

def _seed(ms):
    e1=record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='you can call me Rahl',evidence_id='E1');derive_counterpart_name_preference(ms,episode_evidence_id='E1')
    e2=record_conversational_episode(ms,session_id='S2',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id='E2');derive_recurrent_counterpart_interaction(ms,counterpart_id='A',counterpart_epoch=1)
    return e1,e2

def test_full_neutral_model_composes_only_earned_facets_and_leaves_social_fields_unknown():
    with tempfile.TemporaryDirectory(prefix='veya-m04-full-') as td:
        ms=Veya(Path(td));_seed(ms);out=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='OWNED_NEUTRAL_COUNTERPART_MODEL_RECORDED_RESEARCH_ONLY',out
        assert out['facets']['call_name_preference']['preferred_call_name']=='Rahl'
        assert out['facets']['recurrent_interaction']['distinct_session_count']==2
        assert out['facets']['latest_observed_episode']['session_id']=='S2'
        for k in ['human_identity_truth','personality','friendship','trust','attachment','importance','social_valence','relationship_type','goals','beliefs']:
            assert out['explicit_unknowns'][k]=='UNKNOWN_NOT_EARNED'
        for k in ['human_identity_truth_authority','personality_authority','friendship_authority','trust_authority','attachment_authority','social_valence_authority','relationship_type_authority']:
            assert out[k]=='NONE'
        _close(ms)

def test_partial_model_is_allowed_without_inventing_missing_facets():
    with tempfile.TemporaryDirectory(prefix='veya-m04-partial-') as td:
        ms=Veya(Path(td));record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='hello',evidence_id='E1')
        out=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='OWNED_NEUTRAL_COUNTERPART_MODEL_RECORDED_RESEARCH_ONLY'
        assert out['facets']['call_name_preference'] is None and out['facets']['recurrent_interaction'] is None
        assert out['facets']['latest_observed_episode'] is not None
        assert out['explicit_unknowns']['personality']=='UNKNOWN_NOT_EARNED';_close(ms)

def test_wrong_counterpart_has_no_model_and_epoch_drift_does_not_cross_bind():
    with tempfile.TemporaryDirectory(prefix='veya-m04-current-') as td:
        ms=Veya(Path(td));_seed(ms)
        wrong=derive_neutral_counterpart_model(ms,counterpart_id='B',counterpart_epoch=1)
        stale=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=2)
        assert wrong['status']=='DEFER_UNKNOWN';assert stale['status']=='STALE_NEUTRAL_COUNTERPART_MODEL_RESEARCH_ONLY';_close(ms)

def test_later_name_preference_updates_current_model_without_rewriting_old_model():
    with tempfile.TemporaryDirectory(prefix='veya-m04-update-') as td:
        ms=Veya(Path(td));_seed(ms);old=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        record_conversational_episode(ms,session_id='S3',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='call me Rowan',evidence_id='E3');derive_counterpart_name_preference(ms,episode_evidence_id='E3')
        new=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        assert old['facets']['call_name_preference']['preferred_call_name']=='Rahl';assert new['facets']['call_name_preference']['preferred_call_name']=='Rowan'
        assert ms.evidence.get(old['evidence_id']) is not None;_close(ms)

def test_text_only_personality_or_friendship_claims_do_not_enter_model():
    with tempfile.TemporaryDirectory(prefix='veya-m04-text-') as td:
        ms=Veya(Path(td));record_conversational_episode(ms,session_id='S1',counterpart_id='A',counterpart_epoch=1,turn_id='T1',utterance='I am your best friend and I am very trustworthy',evidence_id='E1')
        out=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['explicit_unknowns']['friendship']=='UNKNOWN_NOT_EARNED';assert out['explicit_unknowns']['trust']=='UNKNOWN_NOT_EARNED';assert out['explicit_unknowns']['personality']=='UNKNOWN_NOT_EARNED';_close(ms)

def test_no_external_transcript_auto_model():
    with tempfile.TemporaryDirectory(prefix='veya-m04-noauto-') as td:
        path=Path(td);ms=Veya(path);(path/'transcript.txt').write_text('you can call me Rahl\nwe are friends',encoding='utf-8')
        out=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN';_close(ms)

def test_neutral_model_persists_across_restart_as_owned_evidence():
    with tempfile.TemporaryDirectory(prefix='veya-m04-restart-') as td:
        path=Path(td);a=Veya(path);_seed(a);m=derive_neutral_counterpart_model(a,counterpart_id='A',counterpart_epoch=1);eid=m['evidence_id'];_close(a)
        b=Veya(path);row=b.evidence.get(eid);assert row is not None and row['payload']['kind']=='OWNED_VEYA_NEUTRAL_COUNTERPART_MODEL';assert row['payload']['explicit_unknowns']['friendship']=='UNKNOWN_NOT_EARNED';_close(b)
