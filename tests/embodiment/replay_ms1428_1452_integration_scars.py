from __future__ import annotations
import json
from pathlib import Path
from test_ms1452_integration import (
    make_ms, setup, establish_old_law, current_proposal, execute_actual, holdout_refs, opts,
)
from microseed.runtime.types import Authority, Observation
from microseed.development.action_learning import ExternalActionOutcomeRelationQualifier


def main():
    td,ms=make_ms(); checks={}
    try:
        setup(ms); old=establish_old_law(ms); p=current_proposal(ms)
        for i in range(16): execute_actual(ms,p,i,next_state='S2',post=2.5,prefix='SCAR')
        w=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        checks['prediction_error_not_model_switch_authority']=w['status']=='DRIFT_WITNESS' and w['model_switch_authority']=='NONE'
        checks['drift_witness_not_drift_cause_identity']=w['drift_cause_authority']=='NONE' and w['semantic_regime_authority']=='NONE'
        checks['old_law_history_preserved']=old.relation_id in ms.action_outcome_learning.relations and ms.action_outcome_predictive_relation_status(old.relation_id)['status']=='STALE_PREDICTIVE_RELATION'
        c=ms.nominate_action_outcome_replacement_candidates(old.relation_id,w['witness']['witness_id'])[0]
        checks['replacement_is_proposal_only']=c.authority=='MODEL_OUTPUT_ONLY' and c.qualification_authority=='NONE'
        ms.observe_value_state('V',0.0); ms.observe_opaque_control_state(Observation('SC-PRE','EXT','opaque-control','S0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-SC-PRE')
        checks['proposal_cannot_resume_rehearsal']=ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V') is None
        ticket=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout_refs(ms,c,12,next_state='S2',effect=2.5,prefix='SCQ',one_miss=True))
        q=ms.qualify_action_outcome_predictive_relation(ticket)
        checks['independent_requalification_required']=q['status']=='CURRENT_PREDICTIVE_RELATION' and q['replacement_of']==old.relation_id
        p2=current_proposal(ms)
        checks['qualified_replacement_resumes_rehearsal']=p2.predicted_state_path==('S0','S2')
        checks['parent_model_not_child_current_capability']=ms.action_outcome_learning_status()['model_switch_authority']=='NONE'
        checks['failed_intention_can_still_learn_actual']=c.next_state_id=='S2' and c.value_effect==2.5
        checks['no_general_cause_or_switch_api']=not hasattr(ms,'classify_action_outcome_drift_cause') and not hasattr(ms,'auto_switch_action_outcome_relation')
        out={'all_pass':all(checks.values()),'checks':checks}
        Path(__file__).resolve().parents[2].joinpath('MS1428_1452_MAINDEV_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print(json.dumps(out,indent=2,sort_keys=True))
        return 0 if out['all_pass'] else 1
    finally: td.cleanup()

if __name__=='__main__': raise SystemExit(main())
