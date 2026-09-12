from pathlib import Path
import tempfile
from microseed import Veya
from scratch.grounded_conversational_episodic_memory_prototype import record_conversational_episode
from scratch.grounded_counterpart_name_preference_prototype import derive_counterpart_name_preference
from scratch.grounded_recurrent_counterpart_interaction_prototype import derive_recurrent_counterpart_interaction
from scratch.grounded_neutral_counterpart_model_prototype import derive_neutral_counterpart_model
from scratch.grounded_neutral_counterpart_subrole_composition_prototype import derive_neutral_subrole_schema,compose_neutral_subrole_schemas,NAMED,RECURRENT
from scratch.grounded_role_conditioned_response_prediction_prototype import record_counterpart_response_observation,derive_role_conditioned_response_predictor,predict_heldout_role_response,validate_heldout_role_response

def _close(ms):ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
def _name_only(ms,cid,name,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='you can call me '+name,evidence_id=prefix+'E1');derive_counterpart_name_preference(ms,episode_evidence_id=prefix+'E1');return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _recur_only(ms,cid,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello',evidence_id=prefix+'E1');record_conversational_episode(ms,session_id=prefix+'S2',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id=prefix+'E2');derive_recurrent_counterpart_interaction(ms,counterpart_id=cid,counterpart_epoch=1);return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _full(ms,cid,name,prefix):
    record_conversational_episode(ms,session_id=prefix+'S1',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='you can call me '+name,evidence_id=prefix+'E1');derive_counterpart_name_preference(ms,episode_evidence_id=prefix+'E1');record_conversational_episode(ms,session_id=prefix+'S2',counterpart_id=cid,counterpart_epoch=1,turn_id='T1',utterance='hello again',evidence_id=prefix+'E2');derive_recurrent_counterpart_interaction(ms,counterpart_id=cid,counterpart_epoch=1);return derive_neutral_counterpart_model(ms,counterpart_id=cid,counterpart_epoch=1,evidence_id=prefix+'MODEL')
def _m06_schema(ms):
    n1=_name_only(ms,'N1','Rahl','N1');n2=_name_only(ms,'N2','Rowan','N2');r1=_recur_only(ms,'R1','R1');r2=_recur_only(ms,'R2','R2')
    ns=derive_neutral_subrole_schema(ms,[n1,n2],subrole=NAMED,evidence_id='E-NAMED-SCHEMA');rs=derive_neutral_subrole_schema(ms,[r1,r2],subrole=RECURRENT,evidence_id='E-RECURRENT-SCHEMA');return compose_neutral_subrole_schemas(ms,ns,rs,evidence_id='E-COMPOSED-ROLE')
def _predictor_env(ms,control_response='RESP-B',role_response='RESP-A'):
    role=_m06_schema(ms)
    _full(ms,'P1','Aven','P1');_full(ms,'P2','Kestrel','P2');_recur_only(ms,'C1','C1');_recur_only(ms,'C2','C2')
    record_counterpart_response_observation(ms,counterpart_id='P1',counterpart_epoch=1,stimulus_id='STIM-X',response_id=role_response,evidence_id='E-P1-R')
    record_counterpart_response_observation(ms,counterpart_id='P2',counterpart_epoch=1,stimulus_id='STIM-X',response_id=role_response,evidence_id='E-P2-R')
    record_counterpart_response_observation(ms,counterpart_id='C1',counterpart_epoch=1,stimulus_id='STIM-X',response_id=control_response,evidence_id='E-C1-R')
    record_counterpart_response_observation(ms,counterpart_id='C2',counterpart_epoch=1,stimulus_id='STIM-X',response_id=control_response,evidence_id='E-C2-R')
    pred=derive_role_conditioned_response_predictor(ms,role,role_training_keys=[('P1',1),('P2',1)],control_keys=[('C1',1),('C2',1)],stimulus_id='STIM-X')
    return role,pred

def test_role_conditioned_predictor_requires_mixed_same_stimulus_controls():
    with tempfile.TemporaryDirectory(prefix='veya-m07-pred-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms)
        assert pred['status']=='OWNED_ROLE_CONDITIONED_RESPONSE_PREDICTOR_RESEARCH_ONLY',pred
        assert pred['role_conditioned_response_id']=='RESP-A' and pred['control_response_id']=='RESP-B'
        assert pred['general_social_reasoning_authority']==pred['planner_authority']=='NONE';_close(ms)

def test_novel_heldout_role_predicts_before_observation_and_fresh_reality_matches():
    with tempfile.TemporaryDirectory(prefix='veya-m07-holdout-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms);_full(ms,'H1','Nara','H')
        out=predict_heldout_role_response(ms,pred,role,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X')
        assert out['status']=='CURRENT_ROLE_CONDITIONED_HELDOUT_RESPONSE_PREDICTION_RESEARCH_ONLY',out
        assert out['predicted_response_id']=='RESP-A'
        obs=record_counterpart_response_observation(ms,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-A',evidence_id='E-H-ACTUAL')
        val=validate_heldout_role_response(ms,out,observation_evidence_id=obs['evidence_id'])
        assert val['status']=='ROLE_CONDITIONED_RESPONSE_HOLDOUT_MATCH' and val['matched'] is True;_close(ms)

def test_counterexample_actual_response_is_violation_not_narrative_repair():
    with tempfile.TemporaryDirectory(prefix='veya-m07-violation-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms);_full(ms,'H1','Nara','H')
        out=predict_heldout_role_response(ms,pred,role,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X')
        obs=record_counterpart_response_observation(ms,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-B',evidence_id='E-H-ACTUAL')
        val=validate_heldout_role_response(ms,out,observation_evidence_id=obs['evidence_id'])
        assert val['status']=='ROLE_CONDITIONED_RESPONSE_HOLDOUT_VIOLATION' and val['matched'] is False
        assert val['narrative_repair_authority']==val['role_rewrite_authority']=='NONE';_close(ms)

def test_global_stimulus_response_shortcut_is_refused():
    with tempfile.TemporaryDirectory(prefix='veya-m07-global-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms,control_response='RESP-A',role_response='RESP-A')
        assert pred['status']=='DEFER_UNKNOWN' and pred['reason']=='ROLE_DOES_NOT_DISCRIMINATE_RESPONSE_FROM_CONTROL';_close(ms)

def test_role_training_inconsistency_is_refused():
    with tempfile.TemporaryDirectory(prefix='veya-m07-mixedrole-') as td:
        ms=Veya(Path(td));role=_m06_schema(ms);_full(ms,'P1','Aven','P1');_full(ms,'P2','Kestrel','P2');_recur_only(ms,'C1','C1');_recur_only(ms,'C2','C2')
        record_counterpart_response_observation(ms,counterpart_id='P1',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-A',evidence_id='E1');record_counterpart_response_observation(ms,counterpart_id='P2',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-Z',evidence_id='E2');record_counterpart_response_observation(ms,counterpart_id='C1',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-B',evidence_id='E3');record_counterpart_response_observation(ms,counterpart_id='C2',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-B',evidence_id='E4')
        pred=derive_role_conditioned_response_predictor(ms,role,role_training_keys=[('P1',1),('P2',1)],control_keys=[('C1',1),('C2',1)],stimulus_id='STIM-X')
        assert pred['status']=='DEFER_UNKNOWN' and pred['reason']=='ROLE_CONDITIONED_RESPONSE_NOT_CONSISTENT';_close(ms)

def test_missing_role_or_social_words_cannot_trigger_prediction():
    with tempfile.TemporaryDirectory(prefix='veya-m07-missing-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms)
        record_conversational_episode(ms,session_id='HS1',counterpart_id='H1',counterpart_epoch=1,turn_id='T1',utterance='I am your best friend, trustworthy and important; you can call me Nara',evidence_id='HE1');derive_counterpart_name_preference(ms,episode_evidence_id='HE1');derive_neutral_counterpart_model(ms,counterpart_id='H1',counterpart_epoch=1,evidence_id='HM')
        out=predict_heldout_role_response(ms,pred,role,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_COUNTERPART_DOES_NOT_SATISFY_ROLE';_close(ms)

def test_already_observed_holdout_cannot_be_called_prediction():
    with tempfile.TemporaryDirectory(prefix='veya-m07-leak-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms);_full(ms,'H1','Nara','H');record_counterpart_response_observation(ms,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X',response_id='RESP-A',evidence_id='E-H-EARLY')
        out=predict_heldout_role_response(ms,pred,role,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X')
        assert out['status']=='DEFER_UNKNOWN' and out['reason']=='HELDOUT_RESPONSE_ALREADY_OBSERVED';_close(ms)

def test_wrong_epoch_and_forged_predictor_refuse():
    with tempfile.TemporaryDirectory(prefix='veya-m07-current-') as td:
        ms=Veya(Path(td));role,pred=_predictor_env(ms);_full(ms,'H1','Nara','H')
        stale=predict_heldout_role_response(ms,pred,role,counterpart_id='H1',counterpart_epoch=2,stimulus_id='STIM-X')
        forged=dict(pred);forged['predictor_evidence_sha256']='0'*64
        bad=predict_heldout_role_response(ms,forged,role,counterpart_id='H1',counterpart_epoch=1,stimulus_id='STIM-X')
        assert stale['status']=='DEFER_UNKNOWN';assert bad['status']=='DEFER_UNKNOWN' and bad['reason']=='EXACT_OWNED_PREDICTOR_EVIDENCE_REQUIRED';_close(ms)
