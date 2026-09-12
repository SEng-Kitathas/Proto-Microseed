from __future__ import annotations
import hashlib,json
from typing import Any
from microseed import EpistemicStatus
from scratch.grounded_neutral_counterpart_subrole_composition_prototype import SOURCE as M06_SOURCE, transfer_composed_neutral_role

SOURCE='VEYA-CLEAN-ROLE-CONDITIONED-RESPONSE-PREDICTION'
OBS_KIND='OWNED_VEYA_COUNTERPART_STIMULUS_RESPONSE_OBSERVATION'
PRED_KIND='OWNED_VEYA_ROLE_CONDITIONED_RESPONSE_PREDICTOR'

def _sha(v:object)->str:
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

def record_counterpart_response_observation(ms,*,counterpart_id:str,counterpart_epoch:int,stimulus_id:str,response_id:str,evidence_id:str|None=None)->dict[str,Any]:
    payload={'kind':OBS_KIND,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'stimulus_id':str(stimulus_id),'response_id':str(response_id),'response_semantics':'OPAQUE_OBSERVED_COUNTERPART_RESPONSE_ONLY','truth_authority':'OBSERVATION_ONLY','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','social_valence_authority':'NONE','personality_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE','authority_gain':'NONE'}
    eid=evidence_id or 'E-VEYA-ROLE-RESP-'+_sha(payload)[:24]
    existing=ms.evidence.get(eid)
    if existing is None:
        ref=ms.append_evidence(eid,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE);sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'ROLE_RESPONSE_OBSERVATION_EVIDENCE_ID_COLLISION','predictive_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_COUNTERPART_RESPONSE_OBSERVATION_RESEARCH_ONLY','evidence_id':eid,'evidence_sha256':sha,'counterpart_id':str(counterpart_id),'counterpart_epoch':int(counterpart_epoch),'stimulus_id':str(stimulus_id),'response_id':str(response_id),'truth_authority':'OBSERVATION_ONLY','predictive_authority':'NONE'}

def _responses(ms,key:tuple[str,int],stimulus_id:str,limit:int=512):
    rows=[]
    for row in ms.evidence.recent(max(1,min(int(limit),1024))):
        if row is None or row.get('negative') or row.get('source')!=SOURCE: continue
        p=dict(row.get('payload') or {})
        if p.get('kind')!=OBS_KIND: continue
        if (str(p.get('counterpart_id')),int(p.get('counterpart_epoch',-1)))!=key: continue
        if str(p.get('stimulus_id'))!=str(stimulus_id): continue
        rows.append((row,p))
    return rows

def derive_role_conditioned_response_predictor(ms,role_schema:dict[str,Any],*,role_training_keys:list[tuple[str,int]],control_keys:list[tuple[str,int]],stimulus_id:str,evidence_id:str='E-VEYA-M07-ROLE-PREDICTOR')->dict[str,Any]:
    if role_schema.get('status')!='OWNED_COMPOSED_NEUTRAL_COUNTERPART_ROLE_SCHEMA_RESEARCH_ONLY':
        return {'status':'DEFER_UNKNOWN','reason':'OWNED_M06_COMPOSED_ROLE_SCHEMA_REQUIRED','predictive_authority':'NONE'}
    sr=ms.evidence.get(str(role_schema.get('schema_evidence_id','')))
    if sr is None or sr.get('sha256')!=role_schema.get('schema_evidence_sha256') or sr.get('source')!=M06_SOURCE:
        return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_M06_ROLE_SCHEMA_EVIDENCE_REQUIRED','predictive_authority':'NONE'}
    role_keys=[(str(a),int(b)) for a,b in role_training_keys]; controls=[(str(a),int(b)) for a,b in control_keys]
    if len(role_keys)<2 or len(controls)<2:
        return {'status':'DEFER_UNKNOWN','reason':'AT_LEAST_TWO_ROLE_AND_TWO_CONTROL_CONTEXTS_REQUIRED','predictive_authority':'NONE'}
    if len(set(role_keys))!=len(role_keys) or len(set(controls))!=len(controls) or set(role_keys)&set(controls):
        return {'status':'DEFER_UNKNOWN','reason':'ROLE_AND_CONTROL_CONTEXTS_MUST_BE_DISTINCT','predictive_authority':'NONE'}
    role_responses=[];control_responses=[];refs=[]
    for key in role_keys:
        tr=transfer_composed_neutral_role(ms,role_schema,counterpart_id=key[0],counterpart_epoch=key[1])
        if tr.get('status')!='CURRENT_COMPOSED_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY':
            return {'status':'DEFER_UNKNOWN','reason':'ROLE_TRAINING_CONTEXT_MUST_SATISFY_COMPOSED_ROLE','counterpart_key':list(key),'predictive_authority':'NONE'}
        rows=_responses(ms,key,stimulus_id)
        if not rows:return {'status':'DEFER_UNKNOWN','reason':'ROLE_TRAINING_RESPONSE_EVIDENCE_REQUIRED','counterpart_key':list(key),'predictive_authority':'NONE'}
        vals={str(p['response_id']) for _,p in rows}
        if len(vals)!=1:return {'status':'DEFER_UNKNOWN','reason':'ROLE_TRAINING_RESPONSE_AMBIGUOUS','counterpart_key':list(key),'predictive_authority':'NONE'}
        role_responses.append(next(iter(vals)));refs.extend([[r['evidence_id'],r['sha256']] for r,_ in rows])
    for key in controls:
        tr=transfer_composed_neutral_role(ms,role_schema,counterpart_id=key[0],counterpart_epoch=key[1])
        if tr.get('status')=='CURRENT_COMPOSED_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY':
            return {'status':'DEFER_UNKNOWN','reason':'CONTROL_CONTEXT_MUST_NOT_SATISFY_COMPOSED_ROLE','counterpart_key':list(key),'predictive_authority':'NONE'}
        rows=_responses(ms,key,stimulus_id)
        if not rows:return {'status':'DEFER_UNKNOWN','reason':'CONTROL_RESPONSE_EVIDENCE_REQUIRED','counterpart_key':list(key),'predictive_authority':'NONE'}
        vals={str(p['response_id']) for _,p in rows}
        if len(vals)!=1:return {'status':'DEFER_UNKNOWN','reason':'CONTROL_RESPONSE_AMBIGUOUS','counterpart_key':list(key),'predictive_authority':'NONE'}
        control_responses.append(next(iter(vals)));refs.extend([[r['evidence_id'],r['sha256']] for r,_ in rows])
    if len(set(role_responses))!=1:
        return {'status':'DEFER_UNKNOWN','reason':'ROLE_CONDITIONED_RESPONSE_NOT_CONSISTENT','predictive_authority':'NONE'}
    if len(set(control_responses))!=1:
        return {'status':'DEFER_UNKNOWN','reason':'CONTROL_RESPONSE_NOT_CONSISTENT','predictive_authority':'NONE'}
    target=role_responses[0]; control=control_responses[0]
    if target==control:
        return {'status':'DEFER_UNKNOWN','reason':'ROLE_DOES_NOT_DISCRIMINATE_RESPONSE_FROM_CONTROL','predictive_authority':'NONE'}
    payload={'kind':PRED_KIND,'predictor_id':'VEYA-M07-PRED-'+_sha({'role':role_schema['schema_id'],'stimulus':stimulus_id,'target':target,'control':control})[:24],'role_schema_ref':[role_schema['schema_evidence_id'],role_schema['schema_evidence_sha256']],'stimulus_id':str(stimulus_id),'role_conditioned_response_id':target,'control_response_id':control,'role_training_keys':[list(k) for k in role_keys],'control_keys':[list(k) for k in controls],'response_evidence_refs':refs,'prediction_semantics':'EMPIRICAL_ROLE_CONDITIONED_OPAQUE_RESPONSE_PREDICTION_ONLY','general_social_reasoning_authority':'NONE','planner_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE','attachment_authority':'NONE','importance_authority':'NONE','personality_authority':'NONE','social_valence_authority':'NONE','relationship_type_authority':'NONE','human_identity_truth_authority':'NONE','authority_gain':'NONE'}
    existing=ms.evidence.get(evidence_id)
    if existing is None:
        ref=ms.append_evidence(evidence_id,payload,EpistemicStatus.PRESSURE_SUPPORTED,source=SOURCE);sha=ref.sha256
    else:
        if existing.get('negative') or existing.get('payload')!=payload or existing.get('source')!=SOURCE:
            return {'status':'DEFER_UNKNOWN','reason':'ROLE_PREDICTOR_EVIDENCE_ID_COLLISION','predictive_authority':'NONE'}
        sha=str(existing.get('sha256',''))
    return {'status':'OWNED_ROLE_CONDITIONED_RESPONSE_PREDICTOR_RESEARCH_ONLY','predictor_id':payload['predictor_id'],'predictor_evidence_id':evidence_id,'predictor_evidence_sha256':sha,'role_schema_ref':payload['role_schema_ref'],'stimulus_id':str(stimulus_id),'role_conditioned_response_id':target,'control_response_id':control,'role_training_keys':payload['role_training_keys'],'control_keys':payload['control_keys'],'general_social_reasoning_authority':'NONE','planner_authority':'NONE'}

def predict_heldout_role_response(ms,predictor:dict[str,Any],role_schema:dict[str,Any],*,counterpart_id:str,counterpart_epoch:int,stimulus_id:str)->dict[str,Any]:
    if predictor.get('status')!='OWNED_ROLE_CONDITIONED_RESPONSE_PREDICTOR_RESEARCH_ONLY':return {'status':'DEFER_UNKNOWN','reason':'OWNED_ROLE_CONDITIONED_PREDICTOR_REQUIRED','predictive_authority':'NONE'}
    pr=ms.evidence.get(str(predictor.get('predictor_evidence_id','')))
    if pr is None or pr.get('sha256')!=predictor.get('predictor_evidence_sha256') or pr.get('source')!=SOURCE:
        return {'status':'DEFER_UNKNOWN','reason':'EXACT_OWNED_PREDICTOR_EVIDENCE_REQUIRED','predictive_authority':'NONE'}
    if str(stimulus_id)!=str(predictor.get('stimulus_id')):return {'status':'DEFER_UNKNOWN','reason':'PREDICTOR_STIMULUS_MISMATCH','predictive_authority':'NONE'}
    key=(str(counterpart_id),int(counterpart_epoch))
    seen={tuple(x) for x in predictor.get('role_training_keys',[])}|{tuple(x) for x in predictor.get('control_keys',[])}
    if key in seen:return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_COUNTERPART_MUST_BE_NOVEL','predictive_authority':'NONE'}
    if _responses(ms,key,stimulus_id):return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_RESPONSE_ALREADY_OBSERVED','predictive_authority':'NONE'}
    tr=transfer_composed_neutral_role(ms,role_schema,counterpart_id=key[0],counterpart_epoch=key[1])
    if tr.get('status')!='CURRENT_COMPOSED_NEUTRAL_COUNTERPART_ROLE_TRANSFER_RESEARCH_ONLY':
        return {'status':'DEFER_UNKNOWN','reason':'HELDOUT_COUNTERPART_DOES_NOT_SATISFY_ROLE','predictive_authority':'NONE'}
    return {'status':'CURRENT_ROLE_CONDITIONED_HELDOUT_RESPONSE_PREDICTION_RESEARCH_ONLY','predictor_id':predictor['predictor_id'],'counterpart_id':key[0],'counterpart_epoch':key[1],'stimulus_id':str(stimulus_id),'predicted_response_id':predictor['role_conditioned_response_id'],'prediction_basis':'OWNED_M06_ROLE_PLUS_EMPIRICAL_ROLE_CONDITIONED_RESPONSE_RELATION','general_social_reasoning_authority':'NONE','planner_authority':'NONE','friendship_authority':'NONE','trust_authority':'NONE'}

def validate_heldout_role_response(ms,prediction:dict[str,Any],*,observation_evidence_id:str)->dict[str,Any]:
    if prediction.get('status')!='CURRENT_ROLE_CONDITIONED_HELDOUT_RESPONSE_PREDICTION_RESEARCH_ONLY':return {'status':'DEFER_UNKNOWN','reason':'CURRENT_HELDOUT_PREDICTION_REQUIRED'}
    row=ms.evidence.get(str(observation_evidence_id))
    if row is None or row.get('negative') or row.get('source')!=SOURCE:return {'status':'DEFER_UNKNOWN','reason':'EXACT_FRESH_RESPONSE_OBSERVATION_REQUIRED'}
    p=dict(row.get('payload') or {})
    same=(p.get('kind')==OBS_KIND and str(p.get('counterpart_id'))==prediction['counterpart_id'] and int(p.get('counterpart_epoch',-1))==prediction['counterpart_epoch'] and str(p.get('stimulus_id'))==prediction['stimulus_id'])
    if not same:return {'status':'DEFER_UNKNOWN','reason':'FRESH_RESPONSE_OBSERVATION_CONTEXT_MISMATCH'}
    matched=str(p.get('response_id'))==str(prediction['predicted_response_id'])
    return {'status':'ROLE_CONDITIONED_RESPONSE_HOLDOUT_MATCH' if matched else 'ROLE_CONDITIONED_RESPONSE_HOLDOUT_VIOLATION','matched':matched,'predicted_response_id':prediction['predicted_response_id'],'observed_response_id':str(p.get('response_id')),'counterpart_id':prediction['counterpart_id'],'stimulus_id':prediction['stimulus_id'],'narrative_repair_authority':'NONE','role_rewrite_authority':'NONE'}
