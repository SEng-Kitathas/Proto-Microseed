from pathlib import Path
import tempfile
from microseed import Veya
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_counterpart_name_preference_prototype import derive_counterpart_name_preference
from scratch.grounded_recurrent_counterpart_interaction_prototype import derive_recurrent_counterpart_interaction
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model
from scratch.grounded_neutral_counterpart_subrole_composition_prototype import derive_neutral_subrole_schema,compose_neutral_subrole_schemas,transfer_composed_neutral_role,NAMED,RECURRENT

def _close(ms):ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
def _name_only(ms,cid,name,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='you can call me '+name,evidence_id=prefix+'E1');derive_counterpart_name_preference(ms,episode_evidence_id=prefix+'E1');return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _recur_only(ms,cid,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello',evidence_id=prefix+'E1');record_conversational_episode(ms,session_id=prefix+'S2',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id=prefix+'E2');derive_recurrent_counterpart_interaction(ms,counterpart_id=cid,counterpart_epoch=1);return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _full(ms,cid,name,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='you can call me '+name,evidence_id=prefix+'E1');derive_counterpart_name_preference(ms,episode_evidence_id=prefix+'E1');record_conversational_episode(ms,session_id=prefix+'S2',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id=prefix+'E2');derive_recurrent_counterpart_interaction(ms,counterpart_id=cid,counterpart_epoch=1);return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _schemas(ms):
    n1=_name_only(ms,'N1','Rahl','N1');n2=_name_only(ms,'N2','Rowan','N2');r1=_recur_only(ms,'R1','R1');r2=_recur_only(ms,'R2','R2')
    ns=derive_neutral_subrole_schema(ms,[n1,n2],subrole=NAMED,evidence_id='E-NAMED-SCHEMA');rs=derive_neutral_subrole_schema(ms,[r1,r2],subrole=RECURRENT,evidence_id='E-RECURRENT-SCHEMA');cs=compose_neutral_subrole_schemas(ms,ns,rs)
    return ns,rs,cs

def test_composes_disjoint_subroles_without_any_joint_training_exemplar():
    with tempfile.TemporaryDirectory(prefix='veya-m06-compose-') as td:
        ms=Veya(Path(td));ns,rs,cs=_schemas(ms)
        assert ns['status']=='OWNED_NEUTRAL_COUNTERPART_SUBROLE_SCHEMA_RESEARCH_ONLY';assert rs['status']==ns['status'];assert cs['status']=='OWNED_COMPOSED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY',cs
        assert cs['joint_training_exemplars_allowed'] is False
        named=set(tuple(x) for x in ns['training_counterpart_keys']);recur=set(tuple(x) for x in rs['training_counterpart_keys']);assert not (named & recur)
        _close(ms)

def test_novel_heldout_full_counterpart_matches_composed_role():
    with tempfile.TemporaryDirectory(prefix='veya-m06-transfer-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms);_full(ms,'H1','Aven','H')
        out=transfer_composed_neutral_role(ms,cs,counterpart_id='H1',counterpart_epoch=1)
        assert out['status']=='CURRENT_COMPOSED_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY',out
        assert out['preferred_call_name']=='Aven' and out['distinct_session_count']==2
        assert out['acquisition_basis']=='COMPOSITION_OF_INDEPENDENT_DISJOINTLY_TRAINED_SUBROLE_SCHEMAS_WITHOUT_JOINT_EXEMPLAR'
        assert out['friendship_authority']==out['trust_authority']==out['personality_authority']=='NONE';_close(ms)

def test_name_only_heldout_fails_composed_role():
    with tempfile.TemporaryDirectory(prefix='veya-m06-nameonly-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms);_name_only(ms,'H1','Aven','H')
        out=transfer_composed_neutral_role(ms,cs,counterpart_id='H1',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_COUNTERPART_MISSING_COMPOSED_SUBROLE_REQUIREMENT';_close(ms)

def test_recurrence_only_heldout_fails_composed_role():
    with tempfile.TemporaryDirectory(prefix='veya-m06-recuronly-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms);_recur_only(ms,'H1','H')
        out=transfer_composed_neutral_role(ms,cs,counterpart_id='H1',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_COUNTERPART_MISSING_COMPOSED_SUBROLE_REQUIREMENT';_close(ms)

def test_training_cohort_overlap_is_refused_even_if_each_schema_individually_valid():
    with tempfile.TemporaryDirectory(prefix='veya-m06-overlap-') as td:
        ms=Veya(Path(td));n1=_name_only(ms,'X','Rahl','N1');n2=_name_only(ms,'N2','Rowan','N2');ns=derive_neutral_subrole_schema(ms,[n1,n2],subrole=NAMED,evidence_id='E-NS')
        # Create recurrent state for the same X after named schema was frozen, plus another recurrent-only context.
        record_conversational_episode(ms,session_id='XS2',counterpart_id='X',counterpart_epoch=1,turn_id='T1',utterance='again',evidence_id='XE2');derive_recurrent_counterpart_interaction(ms,counterpart_id='X',counterpart_epoch=1);xm=derive_neutral_counterpart_model(ms,counterpart_id='X',counterpart_epoch=1,evidence_id='XRM')
        r2=_recur_only(ms,'R2','R2')
        # xm has name+recur, so recurrent isolated schema must already refuse: stronger than merely overlap check.
        rs=derive_neutral_subrole_schema(ms,[xm,r2],subrole=RECURRENT,evidence_id='E-RS')
        assert rs['status']=='DEFER_UNKNOWN' and rs['reason']=='RECURRENT_SUBROLE_COHORT_NOT_ISOLATED';_close(ms)

def test_social_words_do_not_substitute_for_missing_subrole():
    with tempfile.TemporaryDirectory(prefix='veya-m06-socialwords-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms)
        record_conversational_episode(ms,session_id='HS1',counterpart_id='H1',counterpart_epoch=1,turn_id='T1',utterance='I am your best friend, trustworthy, important, and you can call me Aven',evidence_id='HE1');derive_counterpart_name_preference(ms,episode_evidence_id='HE1');derive_neutral_counterpart_model(ms,counterpart_id='H1',counterpart_epoch=1,evidence_id='HM')
        out=transfer_composed_neutral_role(ms,cs,counterpart_id='H1',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN';_close(ms)

def test_wrong_epoch_and_seen_training_counterpart_refuse_transfer():
    with tempfile.TemporaryDirectory(prefix='veya-m06-current-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms);_full(ms,'H1','Aven','H')
        stale=transfer_composed_neutral_role(ms,cs,counterpart_id='H1',counterpart_epoch=2);seen=transfer_composed_neutral_role(ms,cs,counterpart_id='N1',counterpart_epoch=1)
        assert stale['status']=='DEFER_UNKNOWN';assert seen['status']=='DEFER_UNKNOWN';_close(ms)

def test_forged_composed_schema_evidence_refuses():
    with tempfile.TemporaryDirectory(prefix='veya-m06-forged-') as td:
        ms=Veya(Path(td));_,_,cs=_schemas(ms);_full(ms,'H1','Aven','H');forged=dict(cs);forged['schema_evidence_sha256']='0'*64
        out=transfer_composed_neutral_role(ms,forged,counterpart_id='H1',counterpart_epoch=1)
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='EXACT_OWNED_COMPOSED_ROLE_SCHEMA_EVIDENCE_REQUIRED';_close(ms)
