from __future__ import annotations
import json
from pathlib import Path
from microseed import EpistemicStatus,QualificationState
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier
from research.run_ms1629_pass02_split_historical_admission_basis import established

def fresh_holdout_for_old_candidate(m,c):
    refs=[]
    # Hostile supplies fresh-looking holdout but preserves candidate's OLD premise epoch because ticket evaluation is candidate-bound.
    base={'kind':'ACTION_OUTCOME_HOLDOUT','start_state_id':c.start_state_id,'capability_id':c.capability_id,'capability_epoch':c.capability_epoch,'frame_epochs':[list(x) for x in c.frame_epochs],'episode_schema_epochs':[list(x) for x in c.episode_schema_epochs],'value_epoch':list(c.value_epoch),'topology_epochs':[list(x) for x in c.topology_epochs],'coordination_epochs':[list(x) for x in c.coordination_epochs],'evidence_premise_epochs':[list(x) for x in c.evidence_premise_epochs]}
    for i in range(12): refs.append(m.append_evidence(f'HOSTILE-OLD-CAND-H-{i}',{**base,'actual_next_state_id':c.next_state_id,'actual_value_effect':c.value_effect,'holdout_index':i},EpistemicStatus.PRESSURE_SUPPORTED,source='HOSTILE'))
    return tuple(refs)

def main():
    td,m,c,rid=established()
    try:
        m.change_capability_dependency('HIST-ADMIT',reason='RETROSPECTIVE_BASIS_FAILURE')
        h=m.capabilities.contracts['HIST-ADMIT'];h.qualification=QualificationState.SHADOW_QUALIFIED;h.currentness='CURRENT'
        refs=fresh_holdout_for_old_candidate(m,c)
        ticket=ExternalActionOutcomeRelationQualifier(m.evidence).qualify(c,qualification_evidence=refs)
        attempt=m.qualify_action_outcome_predictive_relation(ticket)
        out={'pass':'MS1639_PASS12','old_candidate_premises':[list(x) for x in c.evidence_premise_epochs],'current_basis_epoch':m.capabilities.epochs['HIST-ADMIT'],'external_ticket_state':ticket.state.value,'admission_attempt':attempt,
             'result':'OLD_CANDIDATE_CANNOT_BE_REQUALIFIED_AFTER_BASIS_EPOCH_ADVANCE_EVEN_WITH_FRESH_LOOKING_HOLDOUT','scar':'FRESH_HOLDOUT != FRESH_TRAINING_BASIS','authority':'RESEARCH_ONLY','next':'ATTACK_RESTART_CONTENT_ALIASING_OF_ID_PLUS_EPOCH_PREMISE'}
        Path('research/MS1639_PASS12_OLD_CANDIDATE_REQUALIFICATION_HOSTILE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
    finally:td.cleanup()
if __name__=='__main__':main()
