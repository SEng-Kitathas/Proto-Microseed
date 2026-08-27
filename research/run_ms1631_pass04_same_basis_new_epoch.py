from __future__ import annotations
import json
from pathlib import Path
from microseed import Authority,EpistemicStatus,Observation,QualificationState,QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier,evaluate_action_outcome_holdout
from research.run_ms1629_pass02_split_historical_admission_basis import established
from research.run_ms1578_pass01_actual_stream_misbinding import prepare


def close_epoch1(m,eid,i):
    assert m.capabilities.epochs['HIST-ADMIT']==1
    live=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','live',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id=eid)
    obs=m.capabilities.invoke('OBS',QueryObligation('OBS-Q','obs',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),execution_id=eid)
    assert live['status']=='CAPABILITY_RESULT' and obs['status']=='CAPABILITY_RESULT'
    o=Observation(f'E1-C-{i}','CAPABILITY:OBS',f'action-execution:{eid}',dict(obs['value']),currentness_basis='HIST_ADMISSION_EPOCH1',authority=Authority.OBSERVATION_ONLY,lineage=('HIST-ADMIT@1',))
    return m.record_bounded_action_outcome(eid,o,evidence_id=f'E1-{i}',evidence_premise_epochs=(('HIST-ADMIT',1),))

def holdout(m,c,prefix):
    refs=[]
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs]}
    for i in range(12): refs.append(m.append_evidence(f'{prefix}-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source=prefix))
    return tuple(refs)

def main():
    td,m,old_c,old_rid=established()
    try:
        changed=sorted(m.capabilities.change_dependency('HIST-ADMIT',reason='STRUCTURAL_REPAIR_NEW_ADMISSION_EPOCH'))
        assert m.capabilities.epochs['HIST-ADMIT']==1
        old_after_epoch_change=m.action_outcome_predictive_relation_status(old_rid)
        # External boundary requalifies the same immutable role handle in the new epoch.
        hc=m.capabilities.contracts['HIST-ADMIT']; hc.qualification=QualificationState.SHADOW_QUALIFIED; hc.currentness='CURRENT'
        counts={}
        for i in range(8):
            eid,_=prepare(m,f'E1P{i}'); assert close_epoch1(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
            cs=[c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_epochs==(('HIST-ADMIT',1),)]
            counts[str(i+1)]=len(cs)
        c1=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_epochs==(('HIST-ADMIT',1),))
        oldrefs=holdout(m,old_c,'OLD-E0-H')
        olds=evaluate_action_outcome_holdout(c1,oldrefs,m.evidence)
        newrefs=holdout(m,c1,'NEW-E1-H')
        news=evaluate_action_outcome_holdout(c1,newrefs,m.evidence)
        rr=m.qualify_action_outcome_predictive_relation(ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c1,qualification_evidence=newrefs))
        out={'pass':'MS1631_PASS04','changed_on_new_epoch':changed,'old_relation_after_epoch_change':old_after_epoch_change,
             'fresh_candidate_counts':counts,'old_epoch_holdout_against_new_candidate':{'support':olds[0],'accuracy':olds[1]},'new_epoch_holdout':{'support':news[0],'accuracy':news[1]},'new_relation':rr['status'],
             'result':'SAME_BASIS_ID_NEW_EPOCH_ENFORCES_FRESH_DEBT_BY_EPOCH_NOT_JUST_ID','scar':'STRUCTURAL_REPAIR_NEW_EPOCH != OLD_BASIS_RESTORED','authority':'RESEARCH_ONLY','next':'TEST_TEMPORARY_ACCESS_RECOVERY_WITHOUT_REQUALIFYING_HISTORICAL_RELATION'}
        Path('research/MS1631_PASS04_SAME_BASIS_NEW_EPOCH.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
