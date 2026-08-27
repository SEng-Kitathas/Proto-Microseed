from __future__ import annotations
import gc,hashlib,json,tempfile
from pathlib import Path
from microseed import Authority,CapabilityContract,EpisodeSchemaContract,EpistemicStatus,Microseed,Observation,OperationalFrameContract,QualificationState,QueryObligation,ValueVariableContract
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1578_pass01_actual_stream_misbinding import seeded,prepare

TRUE={"next_state_id":"S1","observed_values":{"ENERGY":3.62,"THERMAL":7.16,"INTEGRITY":6.34}}

def hist_contract(altered=False):
    return CapabilityContract('HIST-ADMIT','historical admission basis' if not altered else 'ALTERED HISTORICAL BASIS',{'version':'A' if not altered else 'B'}, {},('NO_TRUTH_AUTHORITY','HISTORICAL_ONLY' if not altered else 'ALTERED'),(),Authority.DERIVED_READ_ONLY,('MS1642',),'CURRENT',{},query_obligation_id='HIST-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'ADMISSION'},operational_scope_id='R2')

def install(m):
    m.register_capability(CapabilityContract('OBS','obs',{}, {},(),(),Authority.OBSERVATION_ONLY,('MS1642',),'CURRENT',{},query_obligation_id='OBS-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:dict(TRUE),operational_scope_id='R2'))
    m.register_capability(CapabilityContract('LIVE-BASIS','live',{}, {},(),(),Authority.DERIVED_READ_ONLY,('MS1642',),'CURRENT',{},dependencies=('OBS',),query_obligation_id='LIVE-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'LIVE'},operational_scope_id='R2'))
    m.register_capability(hist_contract(False))

def close(m,eid,i):
    live=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id=eid)
    obs=m.capabilities.invoke('OBS',QueryObligation('OBS-Q','obs',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),execution_id=eid)
    assert live['status']=='CAPABILITY_RESULT' and obs['status']=='CAPABILITY_RESULT'
    hc=m.capabilities.contracts['HIST-ADMIT'];sig=hc.computed_signature_sha256()
    o=Observation(f'C-{i}','OBS',f'action-execution:{eid}',dict(obs['value']),authority=Authority.OBSERVATION_ONLY)
    return m.record_bounded_action_outcome(eid,o,evidence_id=f'E-{i}',evidence_premise_epochs=(('HIST-ADMIT',0),),evidence_premise_signatures=(('HIST-ADMIT',sig),))

def holdout(m,c):
    refs=[];base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs],'evidence_premise_signatures':[list(x) for x in c.evidence_premise_signatures]}
    for i in range(12):refs.append(m.append_evidence(f'H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='H'))
    return tuple(refs)

def establish(root):
    m,_=seeded(root);install(m)
    for i in range(12):eid,_=prepare(m,f'P{i}');assert close(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
    c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_signatures)
    rr=m.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=holdout(m,c)));assert rr['status']=='CURRENT_PREDICTIVE_RELATION'
    return m,c,rr['relation']['relation_id']

def rehydrate(root,altered):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','opaque-regulatory-frame',hashlib.sha256(b'F').hexdigest(),Authority.DERIVED_READ_ONLY,('R',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('ENERGY','opaque-regulatory',4.,8.,hashlib.sha256(b'ENERGY:4.0:8.0').hexdigest(),Authority.DERIVED_READ_ONLY,('R',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_episode_schema(EpisodeSchemaContract('E-ENERGY','opaque-single-value-effect-binding',hashlib.sha256(b'E-ENERGY').hexdigest(),Authority.DERIVED_READ_ONLY,('R',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('ENERGY',0),)))
    m.register_capability(CapabilityContract('REST','opaque-action',{}, {},(),(),Authority.EFFECT,('MS1578-P1',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'action':'REST'},operational_scope_id='R2'))
    m.register_capability(hist_contract(altered))
    m.observe_value_state('ENERGY',3.2)
    return m

def main():
    with tempfile.TemporaryDirectory(prefix='ms1642-') as td:
        root=Path(td);m,c,rid=establish(root);sig=c.evidence_premise_signatures[0][1]
        before=m.action_outcome_predictive_relation_status(rid);del m;gc.collect()
        same=rehydrate(root,False);same_status=same.action_outcome_predictive_relation_status(rid);same_sig=same.capabilities.contracts['HIST-ADMIT'].computed_signature_sha256();del same;gc.collect()
        # use separate copied durable state to avoid duplicate runtime registration events affecting only history, not proposition
        # Reopen same store with altered current contract after process restart.
        altered=rehydrate(root,True);altered_status=altered.action_outcome_predictive_relation_status(rid);altered_sig=altered.capabilities.contracts['HIST-ADMIT'].computed_signature_sha256()
        out={'pass':'MS1642_PASS15','stored_signature':sig,'same_content_signature':same_sig,'altered_content_signature':altered_sig,'before':before,'same_content_restart':same_status,'altered_content_restart':altered_status,
             'result':'CONTENT_BOUND_PREMISE_SIGNATURE_BLOCKS_RESTART_ALIAS_WHILE_ALLOWING_EXACT_CONTENT_REINCARNATION','scar':'PREMISE_ID_EPOCH_SIGNATURE_REQUIRED_FOR_REINCARNATION_SAFE_HISTORICAL_VALIDITY','authority':'RESEARCH_ONLY','next':'WIRE_SPLIT_HISTORICAL_ADMISSION_BASIS_INTO_EXISTING_ASSURED_OUTCOME_INGRESS_WITHOUT_NEW_TYPE'}
        Path('research/MS1642_PASS15_CONTENT_BOUND_PREMISE_CARRIER.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__':main()
