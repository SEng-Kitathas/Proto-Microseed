from __future__ import annotations
import gc,hashlib,json
from pathlib import Path
from microseed import Authority,CapabilityContract,EpisodeSchemaContract,Microseed,OperationalFrameContract,QualificationState,ValueVariableContract
from research.run_ms1629_pass02_split_historical_admission_basis import established

def rehydrate_minimal(root:Path, *, altered_hist:bool):
    m=Microseed(root)
    m.register_operational_frame(OperationalFrameContract('F','opaque-regulatory-frame',hashlib.sha256(b'F').hexdigest(),Authority.DERIVED_READ_ONLY,('RESTART',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_value_variable(ValueVariableContract('ENERGY','opaque-regulatory',4.,8.,hashlib.sha256(b'ENERGY:4.0:8.0').hexdigest(),Authority.DERIVED_READ_ONLY,('RESTART',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.register_episode_schema(EpisodeSchemaContract('E-ENERGY','opaque-single-value-effect-binding',hashlib.sha256(b'E-ENERGY').hexdigest(),Authority.DERIVED_READ_ONLY,('RESTART',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('ENERGY',0),)))
    m.register_capability(CapabilityContract('REST','opaque-action',{}, {},(),(),Authority.EFFECT,('RESTART',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'action':'REST'},operational_scope_id='R2'))
    purpose='DIFFERENT_CONTENT_MASQUERADING_AS_OLD_HISTORICAL_BASIS' if altered_hist else 'historical evidence admission basis'
    invariants=('NO_TRUTH_AUTHORITY','ALTERED_CONTENT') if altered_hist else ('NO_TRUTH_AUTHORITY','HISTORICAL_ONLY')
    m.register_capability(CapabilityContract('HIST-ADMIT',purpose,{'altered':altered_hist}, {},invariants,(),Authority.DERIVED_READ_ONLY,('RESTART-ALTERED' if altered_hist else 'RESTART-SAME',),'CURRENT',{},query_obligation_id='HIST-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'DIFFERENT' if altered_hist else 'SAME'},operational_scope_id='R2'))
    m.observe_value_state('ENERGY',3.2)
    return m

def main():
    td,m,c,rid=established();root=Path(td.name)
    try:
        before=m.action_outcome_predictive_relation_status(rid)
        # Release the old runtime; durable relation remains in the store.
        del m;gc.collect()
        m2=rehydrate_minimal(root,altered_hist=True)
        after=m2.action_outcome_predictive_relation_status(rid)
        r=m2.action_outcome_learning.relations[rid]
        out={'pass':'MS1640_PASS13','before_restart':before,'loaded_relation_premise_epochs':[list(x) for x in r.evidence_premise_epochs],'rehydrated_basis_id':'HIST-ADMIT','rehydrated_basis_epoch':m2.capabilities.epochs['HIST-ADMIT'],'rehydrated_basis_purpose':m2.capabilities.contracts['HIST-ADMIT'].purpose,'after_restart_with_different_content_same_id_epoch':after,
             'result':'FALSE_GREEN__ID_PLUS_RUNTIME_EPOCH_CAN_ALIAS_DIFFERENT_ADMISSION_CONTENT_ACROSS_RESTART' if after['status']=='CURRENT_PREDICTIVE_RELATION' else 'CONTENT_ALIAS_BLOCKED','scar':'PREMISE_ID_PLUS_EPHEMERAL_EPOCH != CONTENT_BOUND_HISTORICAL_ADMISSION_IDENTITY','next':'QUARRY_EXISTING_CONTENT_BOUND_SIGNATURE/HASH_PATTERNS_BEFORE_EXTENDING_PREMISE_CARRIER','authority':'RESEARCH_ONLY'}
        Path('research/MS1640_PASS13_RESTART_CONTENT_ALIASING.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
