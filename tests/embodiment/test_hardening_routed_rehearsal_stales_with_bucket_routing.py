
from __future__ import annotations

import importlib.util
from pathlib import Path


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_routed_rehearsal_stale_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _route_episode(m,fx,raw,tag,start):
    ms=fx['ms'];m.prepare_current(fx,raw,tag);ms.observe_value_state('V',float(start))
    p=ms.nominate_current_raw_projection_conditioned_rehearsal(
        (),m.options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
        routing_task_id='MS2063',routing_channel_id='opaque-control')
    assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    out=ms.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),evidence_id=f'{tag}-OUT',capture_id=f'{tag}-CAP')
    return p,out


def test_preexisting_routed_rehearsal_cannot_remain_current_after_its_bucket_routing_empirically_stales():
    m=_m();fx=m.build_integrated();ms=fx['ms'];world=fx['world']
    try:
        raw=('RR','H0','C1','RRM')
        m.prepare_current(fx,raw,'PREEXIST');ms.observe_value_state('V',0.0)
        old=ms.nominate_current_raw_projection_conditioned_rehearsal(
            (),m.options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
            routing_task_id='MS2063',routing_channel_id='opaque-control')
        assert old is not None and old.projection_routing_id==fx['routing_id'] and old.projection_bucket_id==fx['bucket1']
        assert ms.counterfactual_rehearsal_status(old.proposal_id)['status']=='CURRENT_REHEARSAL_PROPOSAL'

        original=world.request
        def flipped(target):
            rec=original(target)
            if rec['status']=='WORKABLE':
                world.last_effect=-world.last_effect;world.last_next='HIGHER-BAD' if world.last_effect<0 else 'HIGHER-GOOD'
            return rec
        world.request=flipped
        for j in range(16):
            _,out=_route_episode(m,fx,raw,f'RR-DRIFT-{j}',0.001*(j+1))
            assert out['outcome']['actual_value_effect']<0.0
        assert ms.projection_conditioned_relation_routing_status(fx['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'

        # Durable proposal history is not an independent currentness source.
        status=ms.counterfactual_rehearsal_status(old.proposal_id)
        assert status['status']=='UNKNOWN_INCOMPLETE'
        assert status['reason'].startswith('REHEARSAL_PROJECTION_ROUTING_NOT_CURRENT')
        commitment=ms.derive_bounded_action_commitment(old.proposal_id)
        assert commitment.commitment.value=='UNKNOWN'
        assert 'ROUTING_NOT_CURRENT' in commitment.reason
    finally:
        try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
        finally:fx['td'].cleanup()
