
from __future__ import annotations

import importlib.util
from pathlib import Path


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_routing_repair_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _flip_world_effect(world):
    original=world.request
    def flipped(target):
        rec=original(target)
        if rec['status']=='WORKABLE':
            world.last_effect=-world.last_effect
            world.last_next='HIGHER-BAD' if world.last_effect<0 else 'HIGHER-GOOD'
        return rec
    world.request=flipped


def _route_episode(m,fx,raw,index,*,start_value):
    ms=fx['ms']
    m.prepare_current(fx,raw,f'ROUTE-{index}')
    ms.observe_value_state('V',float(start_value))
    proposal=ms.nominate_current_raw_projection_conditioned_rehearsal(
        (),m.options(fx),start_state_id='ALIAS',value_id='V',
        projection_routing_id=fx['routing_id'],routing_task_id='MS2063',routing_channel_id='opaque-control')
    assert proposal is not None
    intent=ms.nominate_bounded_action_intent(proposal.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    out=ms.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),
        evidence_id=f'HARDEN-ROUTE-OUT-{index}',capture_id=f'HARDEN-ROUTE-CAP-{index}')
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return proposal,ex,out


def test_historical_globally_stale_relation_remains_lawfully_reusable_inside_qualified_bucket():
    m=_m();fx=m.build_integrated();ms=fx['ms']
    try:
        cid=fx['bound'][0].capability_id
        old_rid=fx['old_rel'][cid]
        assert ms.action_outcome_predictive_relation_status(old_rid)['status']=='STALE_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        raw=('HX','H0','C0','HY')
        assert fx['ctx_candidate'].project(raw)==fx['bucket0']
        proposal,_,out=_route_episode(m,fx,raw,1,start_value=0.0)
        assert proposal.sequence==(cid,)
        assert out['outcome']['actual_value_effect']==2.0
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        scoped=ms.resolve_projection_conditioned_action_outcome_relation(
            fx['routing_id'],projection_bucket_id=fx['bucket0'],action_id=cid,
            task_id='MS2063',channel_id='opaque-control',horizon=2)
        assert scoped['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        assert scoped['relation_id']==old_rid
        assert scoped['global_relation_status']=='STALE_PREDICTIVE_RELATION'
    finally:
        fx['td'].cleanup()


def test_new_post_binding_scoped_drift_stales_routing_and_blocks_rehearsal_reentry():
    m=_m();fx=m.build_integrated();ms=fx['ms'];world=fx['world']
    try:
        cid=fx['bound'][1].capability_id
        rid=fx['new_rel'][cid]
        raw=('DN','H0','C1','DM')
        assert fx['ctx_candidate'].project(raw)==fx['bucket1']
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        _flip_world_effect(world)
        for j in range(16):
            proposal,_,out=_route_episode(m,fx,raw,100+j,start_value=0.001*j)
            assert proposal.sequence==(cid,)
            assert out['outcome']['actual_value_effect'] < 0.0
        # The scoped binding now owns enough descendant evidence to fail closed.
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        scoped=ms.resolve_projection_conditioned_action_outcome_relation(
            fx['routing_id'],projection_bucket_id=fx['bucket1'],action_id=cid,
            task_id='MS2063',channel_id='opaque-control',horizon=2)
        assert scoped['status']=='DEFER_UNKNOWN'
        assert scoped['reason']=='ROUTING_BINDING_NOT_CURRENT'
        m.prepare_current(fx,raw,'AFTER-SCOPED-DRIFT')
        proposal=ms.nominate_current_raw_projection_conditioned_rehearsal(
            (),m.options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
            routing_task_id='MS2063',routing_channel_id='opaque-control')
        assert proposal is None
    finally:
        fx['td'].cleanup()


def test_unrelated_non_routed_global_drift_does_not_poison_independently_qualified_scoped_binding():
    m=_m();fx=m.build_integrated();ms=fx['ms'];world=fx['world']
    try:
        cid=fx['bound'][1].capability_id
        rid=fx['new_rel'][cid]
        raw=('UN','H0','C1','UM')
        _flip_world_effect(world)
        # Exposure proposals are deliberately NOT descendants of the projection
        # routing binding. They may stale the global relation but must not be used
        # as scoped-routing currentness evidence.
        for j in range(16):
            receipt,out=m.execute_episode(ms,world,cid,raw,500000+j)
            assert out['outcome']['actual_value_effect'] < 0.0
        w=ms.assess_action_outcome_predictive_currentness(rid)
        assert w['status']=='DRIFT_WITNESS'
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
    finally:
        fx['td'].cleanup()

def test_scoped_empirical_drift_remains_stale_after_restart_and_exact_runtime_reregistration():
    m=_m();fx=m.build_integrated();ms=fx['ms'];world=fx['world'];root=Path(fx['td'].name)
    try:
        cid=fx['bound'][1].capability_id;rid=fx['new_rel'][cid];raw=('RN','H0','C1','RM')
        ids=tuple(x.capability_id for x in fx['bound']);sigs=tuple(x.computed_signature_sha256() for x in fx['bound']);tokens=tuple(fx['target_tokens']);bid=fx['routing_id']
        _flip_world_effect(world)
        for j in range(16):
            _route_episode(m,fx,raw,700+j,start_value=0.001*j)
        assert ms.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'

        # Fresh process state replays the durable proposal/intent/execution/outcome
        # ancestry, but executable contracts still require explicit re-registration.
        ms2=m.Microseed(root)
        assert bid in ms2.action_outcome_learning.projection_conditioned_bindings
        assert ms2.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        world2=m.TwoLevelWorld();world2.bind_targets(tokens)
        m.register_runtime(ms2,world2,register_frame_state=True)
        target_rec=ms2.epistemic_projections.records['TARGET-P']
        rebound=m.derive_bound_requests(ms2,world2,target_rec,tokens)
        assert tuple(x.capability_id for x in rebound)==ids
        assert tuple(x.computed_signature_sha256() for x in rebound)==sigs
        # Structural premises are restored exactly; empirical scoped drift remains.
        assert ms2.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert ms2.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        fx2={**fx,'ms':ms2,'world':world2,'bound':rebound}
        assert m.current_proposal(fx2,raw,'RESTART-AFTER-DRIFT') is None
    finally:
        fx['td'].cleanup()
