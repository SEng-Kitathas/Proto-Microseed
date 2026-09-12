from pathlib import Path
import tempfile
from microseed import Veya
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_counterpart_name_preference_prototype import derive_counterpart_name_preference
from scratch.grounded_recurrent_counterpart_interaction_prototype import derive_recurrent_counterpart_interaction
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model
from scratch.grounded_neutral_counterpart_role_schema_prototype import derive_neutral_counterpart_role_schema,transfer_neutral_counterpart_role_schema

def _close(ms):ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
def _ctx(ms,cid,name,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='you can call me '+name,evidence_id=prefix+'E1');derive_counterpart_name_preference(ms,episode_evidence_id=prefix+'E1')
    record_conversational_episode(ms,session_id=prefix+'S2',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id=prefix+'E2');derive_recurrent_counterpart_interaction(ms,counterpart_id=cid,counterpart_epoch=1)
    return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')

def test_two_distinct_neutral_models_earn_role_schema_without_social_valence():
    with tempfile.TemporaryDirectory(prefix='veya-m05-schema-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');b=_ctx(ms,'B','Rowan','B');s=derive_neutral_counterpart_role_schema(ms,[a,b])
        assert s['status']=='OWNED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY',s
        assert s['training_counterpart_count']==2 and s['abstract_role']['concrete_counterpart_ids_excluded'] is True
        for k in ['friendship_authority','trust_authority','attachment_authority','importance_authority','social_valence_authority','personality_authority','relationship_type_authority']:
            assert s[k]=='NONE'
        _close(ms)

def test_schema_transfers_to_heldout_counterpart_with_new_name_and_id():
    with tempfile.TemporaryDirectory(prefix='veya-m05-transfer-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');b=_ctx(ms,'B','Rowan','B');s=derive_neutral_counterpart_role_schema(ms,[a,b]);_ctx(ms,'C','Aven','C')
        out=transfer_neutral_counterpart_role_schema(ms,s,counterpart_id='C',counterpart_epoch=1)
        assert out['status']=='CURRENT_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY',out
        assert out['preferred_call_name']=='Aven' and out['distinct_session_count']==2
        assert out['friendship_authority']==out['trust_authority']==out['attachment_authority']=='NONE'
        _close(ms)

def test_partial_heldout_counterpart_does_not_match_role():
    with tempfile.TemporaryDirectory(prefix='veya-m05-partial-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');b=_ctx(ms,'B','Rowan','B');s=derive_neutral_counterpart_role_schema(ms,[a,b]);record_conversational_episode(ms,session_id='DS1',counterpart_id='D',counterpart_epoch=1,turn_id='T1',utterance='hello',evidence_id='DE1')
        out=transfer_neutral_counterpart_role_schema(ms,s,counterpart_id='D',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_COUNTERPART_DOES_NOT_SATISFY_NEUTRAL_ROLE'
        _close(ms)

def test_same_counterpart_twice_cannot_fake_cross_context_schema():
    with tempfile.TemporaryDirectory(prefix='veya-m05-same-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');s=derive_neutral_counterpart_role_schema(ms,[a,a])
        assert s['status']=='DEFER_UNKNOWN' and s['reason']=='DISTINCT_COUNTERPART_CONTEXTS_REQUIRED';_close(ms)

def test_friendship_or_trust_language_does_not_change_role_schema():
    with tempfile.TemporaryDirectory(prefix='veya-m05-text-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');b=_ctx(ms,'B','Rowan','B');record_conversational_episode(ms,session_id='AS3',counterpart_id='A',counterpart_epoch=1,turn_id='T2',utterance='we are best friends and you can trust me',evidence_id='AE3');a2=derive_neutral_counterpart_model(ms,counterpart_id='A',counterpart_epoch=1,evidence_id='A2MODEL');s=derive_neutral_counterpart_role_schema(ms,[a2,b])
        assert s['status']=='OWNED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY'
        assert s['friendship_authority']==s['trust_authority']=='NONE';_close(ms)

def test_wrong_epoch_heldout_context_refuses_transfer():
    with tempfile.TemporaryDirectory(prefix='veya-m05-epoch-') as td:
        ms=Veya(Path(td));a=_ctx(ms,'A','Rahl','A');b=_ctx(ms,'B','Rowan','B');s=derive_neutral_counterpart_role_schema(ms,[a,b]);_ctx(ms,'C','Aven','C')
        out=transfer_neutral_counterpart_role_schema(ms,s,counterpart_id='C',counterpart_epoch=2)
        assert out['status']=='DEFER_UNKNOWN';_close(ms)

def test_schema_persists_across_restart_and_still_has_no_social_authority():
    with tempfile.TemporaryDirectory(prefix='veya-m05-restart-') as td:
        path=Path(td);a_ms=Veya(path);a=_ctx(a_ms,'A','Rahl','A');b=_ctx(a_ms,'B','Rowan','B');s=derive_neutral_counterpart_role_schema(a_ms,[a,b]);eid=s['schema_evidence_id'];_close(a_ms)
        b_ms=Veya(path);row=b_ms.evidence.get(eid);assert row is not None and row['payload']['abstract_role']['role']=='RECURRENT_NAMED_CONVERSATIONAL_COUNTERPART_ROLE';assert row['payload']['friendship_authority']=='NONE';_close(b_ms)
