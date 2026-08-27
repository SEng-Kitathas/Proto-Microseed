from __future__ import annotations
from dataclasses import replace
from microseed.development.action_learning import (
    ExternalProjectionConditionedRelationQualifier,
    ProjectionConditionedRelationQualificationTicket,
)
from microseed.runtime.types import EvidenceRef, EpistemicStatus, QualificationState
from test_ms1477_integration import make_ms, setup, candidate, holdout, qualify

def eref(ms,eid):
    row=ms.evidence.get(eid)
    return EvidenceRef(eid,row['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False)

def run():
    checks={}
    # 1 proposal/qualification overlap
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); refs=list(holdout(ms,c,prefix='HP')) ; refs[0]=eref(ms,'ROUTE-PROP')
        t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs,relations=ms.action_outcome_learning.relations)
        checks['proposal_evidence_cannot_qualify_routing']=t.state==QualificationState.REJECTED
    finally: td.cleanup()
    # 2 selected relation ancestry overlap
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); refs=list(holdout(ms,c,prefix='HR')) ; refs[0]=eref(ms,'REL-OLD-TRAIN')
        t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs,relations=ms.action_outcome_learning.relations)
        checks['selected_relation_evidence_cannot_qualify_routing']=t.state==QualificationState.REJECTED
    finally: td.cleanup()
    # 3 bad candidate digest
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); refs=holdout(ms,c,prefix='HD'); t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs,relations=ms.action_outcome_learning.relations)
        bad=replace(t,candidate_sha256='0'*64)
        checks['candidate_digest_tamper_rejected']=ms.qualify_projection_conditioned_relation_routing(bad)['status']=='ROUTING_REJECTED'
    finally: td.cleanup()
    # 4 non-external qualifier identity
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); refs=holdout(ms,c,prefix='HQ'); t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=refs,relations=ms.action_outcome_learning.relations)
        bad=replace(t,qualifier_id='MICROSEED-SELF')
        checks['self_qualifier_identity_rejected']=ms.qualify_projection_conditioned_relation_routing(bad)['status']=='ROUTING_REJECTED'
    finally: td.cleanup()
    # 5 insufficient holdout
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout(ms,c,prefix='HS',n=4),relations=ms.action_outcome_learning.relations)
        checks['insufficient_holdout_rejected']=t.state==QualificationState.REJECTED
    finally: td.cleanup()
    # 6 inaccurate holdout
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout(ms,c,prefix='HA',bad=True),relations=ms.action_outcome_learning.relations,min_accuracy=0.95)
        checks['inaccurate_holdout_rejected']=t.state==QualificationState.REJECTED
    finally: td.cleanup()
    # 7 projection changes after nomination/qualification ticket creation
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout(ms,c,prefix='HE'),relations=ms.action_outcome_learning.relations)
        ms.change_epistemic_projection('P',new_signature_sha256='d'*64,reason='HOSTILE_SELECTOR_DRIFT')
        checks['projection_epoch_drift_blocks_admission']=ms.qualify_projection_conditioned_relation_routing(t)['status']=='ROUTING_REJECTED'
    finally: td.cleanup()
    # 8 structural relation premise loss blocks the binding
    td,ms=make_ms()
    try:
        setup(ms); c=candidate(ms); ms.change_capability_dependency('A',reason='HOSTILE_CAPABILITY_DRIFT')
        t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout(ms,c,prefix='HC'),relations=ms.action_outcome_learning.relations)
        checks['structural_relation_drift_blocks_admission']=ms.qualify_projection_conditioned_relation_routing(t)['status']=='ROUTING_REJECTED'
    finally: td.cleanup()
    # 9 scope mismatch cannot fall back to global relation
    td,ms=make_ms()
    try:
        setup(ms); bid=qualify(ms,candidate(ms)); x=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',task_id='OTHER',channel_id='CH',horizon=2)
        checks['scope_mismatch_defers']=x['status']=='DEFER_UNKNOWN'
    finally: td.cleanup()
    # 10 arbitrary unseen bucket cannot inherit the default relation merely because shared structure exists.
    td,ms=make_ms()
    try:
        setup(ms); bid=qualify(ms,candidate(ms))
        x=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='unknown',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        checks['unknown_bucket_defers_without_fabricated_relation']=x['status']=='DEFER_UNKNOWN' and x['reason']=='PROJECTION_BUCKET_NOT_QUALIFIED'
    finally: td.cleanup()
    # 11 scoped requalification must not reactivate global empirical currentness
    td,ms=make_ms()
    try:
        setup(ms); bid=qualify(ms,candidate(ms)); before=ms.action_outcome_predictive_relation_status('R-OLD')['status']; ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',task_id='TASK',channel_id='CH',horizon=2); after=ms.action_outcome_predictive_relation_status('R-OLD')['status']
        checks['scoped_use_does_not_globally_reactivate_old_relation']=before==after=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()
    # 12 no second state system / semantic switch surfaces
    td,ms=make_ms()
    try:
        setup(ms)
        checks['no_second_state_or_semantic_switch_api']=all(not hasattr(ms,n) for n in ('predictive_state_registry','predictive_partitions','discover_semantic_regime','auto_split_predictive_state','auto_switch_action_outcome_relation','self_qualify_projection_conditioned_routing'))
    finally: td.cleanup()
    return checks

if __name__=='__main__':
    import json
    c=run(); out={'passed':sum(c.values()),'total':len(c),'all_pass':all(c.values()),'checks':c}; print(json.dumps(out,indent=2,sort_keys=True)); raise SystemExit(0 if out['all_pass'] else 1)
