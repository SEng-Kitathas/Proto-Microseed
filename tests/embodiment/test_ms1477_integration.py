from __future__ import annotations

from pathlib import Path
import tempfile

from microseed.runtime.entity import Microseed
from microseed.runtime.types import (
    Authority, CapabilityContract, EpistemicStatus, FeasibilityState,
    OperationalFrameContract, EpisodeSchemaContract, QualificationState,
    ValueVariableContract, EvidenceRef,
)
from microseed.development.recruitment import RecruitmentOption
from microseed.development.action_learning import (
    QualifiedActionOutcomePredictiveRelation,
    ExternalProjectionConditionedRelationQualifier,
)
from microseed.development.predictive_adaptation import (
    ActionOutcomePredictiveCurrentnessWitness, PredictiveCurrentnessConfig,
)


def make_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1477-')
    return td,Microseed(Path(td.name))


def setup(ms:Microseed):
    ms.register_operational_frame(OperationalFrameContract('F','opaque','f'*64,Authority.DERIVED_READ_ONLY,('MS878-902',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    ms.register_value_variable(ValueVariableContract('V','opaque',-10.0,10.0,'v'*64,Authority.DERIVED_READ_ONLY,('MS953-977',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,assistance_ancestry=('SUPPLIED_CONSTITUTIONAL_VALUE_VARIABLE',)))
    ms.observe_value_state('V',0.0)
    ms.register_capability(CapabilityContract('A','opaque',{},{},(),(),Authority.EFFECT,('MS1477',),'CURRENT',{},query_obligation_id='ACT',qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_: {'receipt':'A'},operational_scope_id='SCOPE'))
    ms.register_episode_schema(EpisodeSchemaContract('E','opaque','e'*64,Authority.DERIVED_READ_ONLY,('MS1103-1127',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED,frame_epochs=(('F',0),),value_epochs=(('V',0),)))
    ms.register_epistemic_projection('P','c'*64,assistance_ancestry=('MS1203-1227_OPAQUE_PROJECTION_LINEAGE',))
    for eid in ('REL-OLD-TRAIN','REL-OLD-QUAL','REL-NEW-TRAIN','REL-NEW-QUAL','ROUTE-PROP'):
        ms.append_evidence(eid,{'kind':'LINEAGE_FIXTURE','id':eid},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-FIXTURE')
    old=QualifiedActionOutcomePredictiveRelation(
        relation_id='R-OLD',candidate_id='C-OLD',candidate_sha256='a'*64,
        start_state_id='S0',capability_id='A',next_state_id='S1',value_effect=1.5,
        support=12,consistency=1.0,source_evidence_ids=('REL-OLD-TRAIN',),qualification_evidence_ids=('REL-OLD-QUAL',),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),episode_schema_epochs=(('E',0),),value_epoch=('V',0),
    )
    new=QualifiedActionOutcomePredictiveRelation(
        relation_id='R-NEW',candidate_id='C-NEW',candidate_sha256='b'*64,
        start_state_id='S0',capability_id='A',next_state_id='S2',value_effect=2.5,
        support=12,consistency=1.0,source_evidence_ids=('REL-NEW-TRAIN',),qualification_evidence_ids=('REL-NEW-QUAL',),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),episode_schema_epochs=(('E',0),),value_epoch=('V',0),
    )
    ms.action_outcome_learning.add_relation(old);ms.action_outcome_learning.add_relation(new)
    ms.action_outcome_learning.currentness_witnesses['R-OLD']=ActionOutcomePredictiveCurrentnessWitness(
        witness_id='W-OLD',relation_id='R-OLD',relation_candidate_sha256='a'*64,status='DRIFT_WITNESS',
        window_accuracies=(0.0,0.0),assessed_evidence_ids=('D1','D2'),drift_evidence_ids=('D1','D2'),drift_window=1,
        config=PredictiveCurrentnessConfig(),
    )
    return old,new


def candidate(ms:Microseed):
    return ms.nominate_projection_conditioned_relation_routing(
        projection_id='P',task_id='TASK',action_ids=('A',),channel_ids=('CH',),horizon=2,
        default_action_relations=(('A','R-NEW'),),bucket_action_overrides=(('k0','A','R-OLD'),),
        source_evidence_ids=('ROUTE-PROP',),
    )


def holdout(ms:Microseed,c,*,prefix='H',n=12,bad=False,overlap_id=None):
    refs=[]
    for i in range(n):
        bucket='k0' if i%2==0 else 'k1'
        ns,ef=('S1',1.5) if bucket=='k0' else ('S2',2.5)
        if bad and i==n-1: ns='BAD'
        eid=overlap_id if i==0 and overlap_id is not None else f'{prefix}{i}'
        refs.append(ms.append_evidence(eid,{
            'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':'P','projection_epoch':0,
            'projection_signature_sha256':'c'*64,'projection_bucket_id':bucket,'task_id':'TASK','action_id':'A',
            'channel_id':'CH','horizon':2,'actual_next_state_id':ns,'actual_value_effect':ef,
        },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-ROUTING-HOLDOUT'))
    return tuple(refs)


def qualify(ms:Microseed,c):
    t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=holdout(ms,c),relations=ms.action_outcome_learning.relations)
    out=ms.qualify_projection_conditioned_relation_routing(t)
    assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    return out['binding']['binding_id']


def test_ms1477_reuses_v24_projection_lineage_not_second_state_registry():
    td,ms=make_ms()
    try:
        setup(ms);c=candidate(ms)
        assert c.projection_id=='P' and c.projection_signature_sha256=='c'*64
        assert 'P' in ms.epistemic_projections.records
        assert not hasattr(ms,'predictive_state_registry') and not hasattr(ms,'predictive_partitions')
    finally: td.cleanup()


def test_routing_candidate_is_proposal_only_and_uses_existing_relation_ids():
    td,ms=make_ms()
    try:
        setup(ms);c=candidate(ms)
        assert c.authority=='MODEL_OUTPUT_ONLY' and c.qualification_authority=='NONE'
        assert c.relation_id_for('k0','A')=='R-OLD' and c.relation_id_for('k1','A')=='R-NEW'
    finally: td.cleanup()


def test_routing_qualification_requires_disjoint_candidate_evidence():
    td,ms=make_ms()
    try:
        setup(ms);c=candidate(ms)
        refs=list(holdout(ms,c,prefix='D'))
        # Reuse the proposal evidence as one qualification ref: must reject.
        row=ms.evidence.get('ROUTE-PROP'); refs[0]=EvidenceRef('ROUTE-PROP',row['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False)
        t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=tuple(refs),relations=ms.action_outcome_learning.relations)
        assert t.state==QualificationState.REJECTED and t.reason=='ROUTING_PROPOSAL_QUALIFICATION_EVIDENCE_OVERLAP'
    finally: td.cleanup()


def test_routing_qualification_cannot_reuse_relation_training_or_qualification_evidence():
    td,ms=make_ms()
    try:
        setup(ms);c=candidate(ms)
        refs=list(holdout(ms,c,prefix='R'))
        row=ms.evidence.get('REL-OLD-TRAIN'); refs[0]=EvidenceRef('REL-OLD-TRAIN',row['sha256'],EpistemicStatus.PRESSURE_SUPPORTED,False)
        t=ExternalProjectionConditionedRelationQualifier(ms.evidence).qualify(c,qualification_evidence=tuple(refs),relations=ms.action_outcome_learning.relations)
        assert t.state==QualificationState.REJECTED and t.reason=='ROUTING_QUALIFICATION_RELATION_EVIDENCE_OVERLAP'
    finally: td.cleanup()


def test_globally_stale_relation_can_be_scoped_without_global_reactivation():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms))
        assert ms.action_outcome_predictive_relation_status('R-OLD')['status']=='STALE_PREDICTIVE_RELATION'
        x=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        assert x['status']=='CURRENT_PARTITION_SCOPED_RELATION' and x['relation_id']=='R-OLD'
        assert x['global_relation_status']=='STALE_PREDICTIVE_RELATION'
        assert ms.action_outcome_predictive_relation_status('R-OLD')['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_other_bucket_routes_new_relation_without_semantic_regime_identity():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms))
        x=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k1',action_id='A',task_id='TASK',channel_id='CH',horizon=2)
        assert x['status']=='CURRENT_PARTITION_SCOPED_RELATION' and x['relation_id']=='R-NEW'
        assert x['semantic_regime_authority']==x['model_switch_authority']=='NONE'
    finally: td.cleanup()


def test_projection_epoch_change_stales_binding_without_erasing_it():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms))
        ms.change_epistemic_projection('P',new_signature_sha256='d'*64,reason='SELECTOR-BOUNDARY-CHANGED')
        st=ms.projection_conditioned_relation_routing_status(bid)
        assert st['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert bid in ms.action_outcome_learning.projection_conditioned_bindings
    finally: td.cleanup()


def test_scope_mismatch_defers_instead_of_falling_back_to_global_switch():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms))
        for kwargs in (
            dict(task_id='OTHER',channel_id='CH',horizon=2),
            dict(task_id='TASK',channel_id='OTHER',horizon=2),
            dict(task_id='TASK',channel_id='CH',horizon=3),
        ):
            x=ms.resolve_projection_conditioned_action_outcome_relation(bid,projection_bucket_id='k0',action_id='A',**kwargs)
            assert x['status']=='DEFER_UNKNOWN'
    finally: td.cleanup()


def test_partition_scoped_relation_reenters_existing_rehearsal_without_new_state_engine():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms));opts=(RecruitmentOption('A',FeasibilityState.FEASIBLE),)
        p0=ms.nominate_counterfactual_rehearsal((),opts,start_state_id='S0',value_id='V',projection_routing_id=bid,projection_bucket_id='k0',routing_task_id='TASK',routing_channel_id='CH')
        p1=ms.nominate_counterfactual_rehearsal((),opts,start_state_id='S0',value_id='V',projection_routing_id=bid,projection_bucket_id='k1',routing_task_id='TASK',routing_channel_id='CH')
        assert p0 is not None and p0.predicted_state_path==('S0','S1')
        assert p1 is not None and p1.predicted_state_path==('S0','S2')
        assert ms.action_outcome_predictive_relation_status('R-OLD')['status']=='STALE_PREDICTIVE_RELATION'
    finally: td.cleanup()


def test_restart_preserves_binding_history_but_does_not_restore_runtime_structural_authority():
    td,ms=make_ms()
    try:
        setup(ms);bid=qualify(ms,candidate(ms))
        ms2=Microseed(Path(td.name))
        assert bid in ms2.action_outcome_learning.projection_conditioned_bindings
        assert ms2.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
    finally: td.cleanup()


def test_no_semantic_regime_auto_split_or_model_switch_api():
    td,ms=make_ms()
    try:
        setup(ms)
        assert not hasattr(ms,'discover_semantic_regime')
        assert not hasattr(ms,'auto_split_predictive_state')
        assert not hasattr(ms,'auto_switch_action_outcome_relation')
        assert not hasattr(ms,'self_qualify_projection_conditioned_routing')
    finally: td.cleanup()
