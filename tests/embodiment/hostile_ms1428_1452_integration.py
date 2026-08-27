from __future__ import annotations

from dataclasses import replace
from microseed.development.predictive_adaptation import PredictiveCurrentnessConfig, assess_action_outcome_predictive_currentness, nominate_drift_replacement_candidates
from microseed.development.action_learning import ActionOutcomeRelationQualificationTicket, ExternalActionOutcomeRelationQualifier
from microseed.runtime.types import QualificationState, EvidenceRef, EpistemicStatus
from test_ms1452_integration import make_ms, setup, establish_old_law, current_proposal, execute_actual, holdout_refs, opts


def run():
    checks={}
    for label, kwargs in [
        ('window_size_1_rejected',{'window_size':1}),
        ('accuracy_gt_1_rejected',{'min_accuracy':1.1}),
        ('zero_consecutive_rejected',{'consecutive_failure_windows':0}),
    ]:
        try:
            PredictiveCurrentnessConfig(**kwargs); checks[label]=False
        except ValueError: checks[label]=True

    td,ms=make_ms()
    try:
        setup(ms); old=establish_old_law(ms); p=current_proposal(ms)
        # Current witness cannot nominate replacement.
        for i in range(8): execute_actual(ms,p,i,next_state='S1',post=1.5,prefix='HGOOD')
        cur=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        checks['current_witness_cannot_nominate_replacement']=ms.nominate_action_outcome_replacement_candidates(old.relation_id,cur['witness']['witness_id'])==()

        # Create real drift.
        for i in range(16): execute_actual(ms,p,8+i,next_state='S2',post=2.5,prefix='HDR')
        dr=ms.assess_action_outcome_predictive_currentness(old.relation_id)
        checks['drift_has_no_switch_authority']=dr['model_switch_authority']=='NONE'
        checks['drift_has_no_cause_or_regime_authority']=dr['drift_cause_authority']==dr['semantic_regime_authority']=='NONE'
        cands=ms.nominate_action_outcome_replacement_candidates(old.relation_id,dr['witness']['witness_id'])
        checks['drift_replacement_is_proposal_only']=len(cands)==1 and cands[0].qualification_authority=='NONE'
        c=cands[0]

        # Drift/proposal evidence cannot self-qualify.
        refs=[]
        for eid in c.source_evidence_ids:
            row=ms.evidence.get(eid); refs.append(EvidenceRef(eid,row['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False))
        fake=ActionOutcomeRelationQualificationTicket(c.candidate_id,c.digest(),QualificationState.SHADOW_QUALIFIED,'HSP-EXTERNAL','fake',tuple(refs),len(refs),1.0)
        checks['replacement_proposal_evidence_cannot_self_qualify']=ms.qualify_action_outcome_predictive_relation(fake)['reason']=='PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP'

        # Proposal does not resume rehearsal.
        checks['proposal_does_not_auto_resume_rehearsal']=ms.nominate_counterfactual_rehearsal((),opts(),start_state_id='S0',value_id='V') is None

        # Fresh qualification can admit but does not retroactively reactivate old relation.
        t=ExternalActionOutcomeRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout_refs(ms,c,12,next_state='S2',effect=2.5,prefix='HQA',one_miss=True))
        q=ms.qualify_action_outcome_predictive_relation(t)
        checks['fresh_qualification_admits_replacement']=q['status']=='CURRENT_PREDICTIVE_RELATION'
        checks['old_relation_stays_stale_after_replacement']=ms.action_outcome_predictive_relation_status(old.relation_id)['status']=='STALE_PREDICTIVE_RELATION'
        checks['no_auto_switch_or_cause_classifier_api']=not hasattr(ms,'auto_switch_action_outcome_relation') and not hasattr(ms,'classify_action_outcome_drift_cause')
    finally:
        td.cleanup()
    return checks

if __name__=='__main__':
    import json
    c=run(); out={'passed':sum(c.values()),'total':len(c),'all_pass':all(c.values()),'checks':c}; print(json.dumps(out,indent=2,sort_keys=True)); raise SystemExit(0 if out['all_pass'] else 1)
