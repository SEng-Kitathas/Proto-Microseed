
from __future__ import annotations

import importlib.util
from pathlib import Path

from microseed import (
    EpistemicStatus, ExternalProjectionConditionedRelationQualifier,
    RecruitmentOption, FeasibilityState,
)
from microseed.development.predictive_adaptation import (
    assess_action_outcome_predictive_currentness, PredictiveCurrentnessConfig,
)


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_bucket_isolation_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _same_relation_two_bucket_binding(m,fx):
    ms=fx['ms'];cid=fx['bound'][1].capability_id;rid=fx['new_rel'][cid]
    rel=ms.action_outcome_learning.relations[rid]
    prop=ms.append_evidence('HARD-BUCKET-ISO-PROP',{'kind':'ROUTING_PROPOSAL_ONLY'},EpistemicStatus.PRESSURE_SUPPORTED,source='HARDENING-PROPOSAL')
    cand=ms.nominate_projection_conditioned_relation_routing(
        projection_id=fx['ctx_rec'].projection_id,task_id='HARD-BUCKET-ISO',action_ids=(cid,),channel_ids=('opaque-control',),horizon=2,
        default_action_relations=((cid,rid),),bucket_action_overrides=(),source_evidence_ids=(prop.evidence_id,))
    refs=[]
    for bucket in (fx['bucket0'],fx['bucket1']):
        for i in range(8):
            refs.append(ms.append_evidence(
                f'HARD-BUCKET-ISO-H-{bucket[-5:]}-{i}',{
                    'kind':'PROJECTION_CONDITIONED_ACTION_OUTCOME_HOLDOUT','projection_id':fx['ctx_rec'].projection_id,
                    'projection_epoch':fx['ctx_rec'].epoch,'projection_signature_sha256':fx['ctx_rec'].signature_sha256,
                    'projection_bucket_id':bucket,'task_id':'HARD-BUCKET-ISO','action_id':cid,'channel_id':'opaque-control','horizon':2,
                    'actual_next_state_id':rel.next_state_id,'actual_value_effect':rel.value_effect,
                },EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-HARD-BUCKET-ISO'))
    ticket=ExternalProjectionConditionedRelationQualifier(ms.evidence,qualifier_id='EXTERNAL-HARD-BUCKET-ISO').qualify(
        cand,qualification_evidence=tuple(refs),relations=ms.action_outcome_learning.relations)
    out=ms.qualify_projection_conditioned_relation_routing(ticket)
    assert out['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    assert set(out['binding']['qualified_bucket_ids'])=={fx['bucket0'],fx['bucket1']}
    return cid,rid,rel,out['binding']['binding_id']


def _routed_episode(m,fx,bid,cid,raw,tag,start,desired_effect,desired_next):
    ms=fx['ms'];w=fx['world']
    m.prepare_current(fx,raw,tag);ms.observe_value_state('V',float(start))
    p=ms.nominate_current_raw_projection_conditioned_rehearsal(
        (),(RecruitmentOption(cid,FeasibilityState.FEASIBLE),),start_state_id='ALIAS',value_id='V',
        projection_routing_id=bid,routing_task_id='HARD-BUCKET-ISO',routing_channel_id='opaque-control')
    assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    # Vary start value only to avoid duplicate content-addressed proposal IDs, then
    # normalize the final observation so the measured effect remains exact.
    w.last_effect=float(start)+float(desired_effect);w.last_next=str(desired_next)
    out=ms.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),evidence_id=f'{tag}-OUT',capture_id=f'{tag}-CAP')
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return p,out


def test_bad_bucket_cannot_be_masked_by_good_outcomes_from_same_relation_in_other_qualified_bucket():
    m=_m();fx=m.build_integrated();ms=fx['ms']
    try:
        cid,rid,rel,bid=_same_relation_two_bucket_binding(m,fx)
        good_raw=('GOOD','H0','C1','GOOD-M')
        bad_raw=('BAD','H0','C0','BAD-M')
        assert fx['ctx_candidate'].project(good_raw)==fx['bucket1']
        assert fx['ctx_candidate'].project(bad_raw)==fx['bucket0']
        n=0;bad_eids=[]
        # 48 good + 16 bad interleaved 3:1. Pooled 8-row windows are exactly
        # 0.75, while the bad bucket alone has two complete 0.0 windows.
        for cycle in range(16):
            for k in range(3):
                start=0.00001*n;n+=1
                _,out=_routed_episode(m,fx,bid,cid,good_raw,f'GOOD-ISO-{cycle}-{k}',start,rel.value_effect,rel.next_state_id)
                assert out['outcome']['actual_value_effect']==rel.value_effect
            start=0.00001*n;n+=1
            _,out=_routed_episode(m,fx,bid,cid,bad_raw,f'BAD-ISO-{cycle}',start,-abs(rel.value_effect),'HIGHER-BAD')
            assert out['outcome']['actual_value_effect']==-abs(rel.value_effect)
            bad_eids.append(out['outcome']['evidence_id'])

        binding=ms.action_outcome_learning.projection_conditioned_bindings[bid]
        pooled=ms._projection_conditioned_post_binding_relation_experiences(binding,rel)
        pooled_w=assess_action_outcome_predictive_currentness(rel,pooled,PredictiveCurrentnessConfig())
        bad_rows=tuple(x for x in pooled if x.evidence_id in set(bad_eids))
        bad_w=assess_action_outcome_predictive_currentness(rel,bad_rows,PredictiveCurrentnessConfig())
        assert len(pooled)==64 and len(bad_rows)==16
        assert pooled_w.window_accuracies==(0.75,)*8
        assert bad_w.window_accuracies==(0.0,0.0)
        assert bad_w.status=='DRIFT_WITNESS'

        # Constitutional requirement: qualified bucket0's new empirical drift may
        # not be diluted by bucket1 evidence merely because both routes reuse the
        # same relation object. Binding-level fail-closed is acceptable; masking is not.
        assert ms.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
    finally:
        try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
        finally:fx['td'].cleanup()
