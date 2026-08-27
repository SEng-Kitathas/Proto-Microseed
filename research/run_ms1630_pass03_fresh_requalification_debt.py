from __future__ import annotations
import json
from pathlib import Path
from microseed import Authority,CapabilityContract,EpistemicStatus,Observation,QualificationState,QueryObligation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier,evaluate_action_outcome_holdout
from research.run_ms1629_pass02_split_historical_admission_basis import established,TRUE
from research.run_ms1578_pass01_actual_stream_misbinding import prepare


def install_v2(m):
    m.register_capability(CapabilityContract('HIST-ADMIT-V2','fresh historical evidence admission basis',{}, {},('NO_TRUTH_AUTHORITY','FRESH_REQUALIFICATION_EPOCH'),(),Authority.DERIVED_READ_ONLY,('MS1630',),'CURRENT',{},query_obligation_id='HIST2-Q',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:{'claim':'FRESH_EVIDENCE_ADMISSIBLE_AT_ACQUISITION'},operational_scope_id='R2'))

def close_v2(m,eid,i):
    # Live observation route is still current in this case; only the old historical basis was falsified.
    live=m.capabilities.invoke('LIVE-BASIS',QueryObligation('LIVE-Q','current observation use',Authority.DERIVED_READ_ONLY,operational_scope_id='R2'),execution_id=eid)
    obs=m.capabilities.invoke('OBS',QueryObligation('OBS-Q','observe',Authority.OBSERVATION_ONLY,operational_scope_id='R2'),execution_id=eid)
    assert live['status']=='CAPABILITY_RESULT' and obs['status']=='CAPABILITY_RESULT'
    o=Observation(f'V2-C-{i}','CAPABILITY:OBS',f'action-execution:{eid}',dict(obs['value']),currentness_basis='FRESH_HISTORICAL_ADMISSION_V2',authority=Authority.OBSERVATION_ONLY,lineage=('HIST-ADMIT-V2@0',))
    return m.record_bounded_action_outcome(eid,o,evidence_id=f'V2-E-{i}',evidence_premise_epochs=(('HIST-ADMIT-V2',0),))

def v2_holdout(m,c,n=12,prefix='V2-H'):
    refs=[]
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs]}
    for i in range(n): refs.append(m.append_evidence(f'{prefix}-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='FRESH-V2-HOLDOUT'))
    return tuple(refs)

def main():
    td,m,old_c,old_rid=established()
    try:
        m.invalidate_capability('HIST-ADMIT',reason='RETROSPECTIVE_ADMISSION_FALSIFIED')
        old_after=m.action_outcome_predictive_relation_status(old_rid)
        install_v2(m)
        counts={}
        # One fresh sample cannot inherit old support because premise epochs differ.
        for i in range(8):
            eid,_=prepare(m,f'V2P{i}'); assert close_v2(m,eid,i)['status']=='ACTION_OUTCOME_OBSERVED'
            cs=[c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_epochs==(('HIST-ADMIT-V2',0),)]
            counts[str(i+1)]=len(cs)
        fresh_c=next(c for c in m.nominate_action_outcome_predictive_candidates() if c.capability_id=='REST' and c.value_epoch[0]=='ENERGY' and c.evidence_premise_epochs==(('HIST-ADMIT-V2',0),))
        # Old-basis holdout must be unusable for the fresh-basis candidate.
        old_refs=v2_holdout(m,old_c,n=12,prefix='OLD-REPLAY-H')
        old_support,old_acc=evaluate_action_outcome_holdout(fresh_c,old_refs,m.evidence)
        new_refs=v2_holdout(m,fresh_c)
        new_support,new_acc=evaluate_action_outcome_holdout(fresh_c,new_refs,m.evidence)
        t=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(fresh_c,qualification_evidence=new_refs)
        rr=m.qualify_action_outcome_predictive_relation(t)
        out={
          'pass':'MS1630_PASS03','old_relation_after_retrospective_falsification':old_after,
          'fresh_candidate_counts_by_new_samples':counts,
          'fresh_candidate_support':fresh_c.support,'fresh_candidate_premises':[list(x) for x in fresh_c.evidence_premise_epochs],
          'old_holdout_against_fresh_candidate':{'support':old_support,'accuracy':old_acc},
          'new_holdout_against_fresh_candidate':{'support':new_support,'accuracy':new_acc},
          'fresh_relation_status':rr['status'],
          'result':'EXISTING_PREMISE_GROUPING_AND_HOLDOUT_MATCHING_ENFORCE_FRESH_REQUALIFICATION_DEBT_ACROSS_NEW_ADMISSION_BASIS',
          'scar':'OLD_BASIS_EVIDENCE != FRESH_BASIS_SUPPORT',
          'next':'ATTACK_SAME_CAPABILITY_NEW_EPOCH_TO_ENSURE_EPOCH_NOT_ID_ONLY_ENFORCES_DEBT',
          'authority':'RESEARCH_ONLY'
        }
        Path('research/MS1630_PASS03_FRESH_REQUALIFICATION_DEBT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print(json.dumps(out,indent=2,sort_keys=True))
    finally: td.cleanup()
if __name__=='__main__':main()
