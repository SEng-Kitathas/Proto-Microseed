
from __future__ import annotations

import importlib.util
from pathlib import Path


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_routing_ms2063',path)
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


def test_post_qualification_empirical_drift_does_not_currently_stale_projection_routing_and_can_reenter_rehearsal():
    m=_m();fx=m.build_integrated();ms=fx['ms'];world=fx['world']
    try:
        # H0/C1 projects to b1, which uses the current new relation. Capability 1
        # is the +2 action in that scope.
        raw=('HARD-N','H0','C1','HARD-M')
        cid=fx['bound'][1].capability_id
        rid=fx['new_rel'][cid]
        assert fx['ctx_candidate'].project(raw)==fx['bucket1']
        assert ms.action_outcome_learning.relations[rid].value_effect==2.0
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        # Change only the external effect law; all structural premises remain exact.
        _flip_world_effect(world)
        for j in range(16):
            receipt,out=m.execute_episode(ms,world,cid,raw,300000+j)
            assert receipt['target']==fx['target_tokens'][1]
            assert out['outcome']['actual_value_effect']==-2.0

        witness=ms.assess_action_outcome_predictive_currentness(rid)
        assert witness['status']=='DRIFT_WITNESS'
        assert witness['witness']['window_accuracies']==[0.0,0.0]
        assert ms.action_outcome_predictive_relation_status(rid)['status']=='STALE_PREDICTIVE_RELATION'

        # Hostile finding: routing currentness ignores empirical relation stale state.
        route=ms.projection_conditioned_relation_routing_status(fx['routing_id'])
        assert route['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        scoped=ms.resolve_projection_conditioned_action_outcome_relation(
            fx['routing_id'],projection_bucket_id=fx['bucket1'],action_id=cid,
            task_id='MS2063',channel_id='opaque-control',horizon=2)
        assert scoped['status']=='CURRENT_PARTITION_SCOPED_RELATION'
        assert scoped['relation_id']==rid
        assert scoped['global_relation_status']=='STALE_PREDICTIVE_RELATION'

        # Worse: the stale scoped relation can still re-enter current rehearsal.
        proposal=m.current_proposal(fx,raw,'POST-DRIFT-ROUTING')
        assert proposal is not None
        assert proposal.sequence==(cid,)
        assert proposal.execution_authority=='NONE'
    finally:
        fx['td'].cleanup()
