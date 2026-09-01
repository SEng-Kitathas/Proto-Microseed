
from __future__ import annotations

import importlib.util
from pathlib import Path
import types


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_bc_repair_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _route_proposal(m,fx,raw,tag,start_value):
    m.prepare_current(fx,raw,tag)
    fx['ms'].observe_value_state('V',float(start_value))
    return fx['ms'].nominate_current_raw_projection_conditioned_rehearsal(
        (),m.options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
        routing_task_id='MS2063',routing_channel_id='opaque-control')


def _execute_route_and_record(m,fx,raw,tag,start_value):
    p=_route_proposal(m,fx,raw,tag,start_value);assert p is not None
    intent=fx['ms'].nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=fx['ms'].execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    out=fx['ms'].record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),evidence_id=f'{tag}-OUT',capture_id=f'{tag}-CAP')
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return p,ex,out


def _install_nested_actual_outcome(m,top,middle):
    tw=top['world'];mm=middle['ms'];mw=middle['world'];counter={'n':0};log=[]
    def nested_request(self,target):
        target=str(target);idx=self.targets.index(target);n=counter['n'];counter['n']+=1
        raw=('MN0','H0','C0','MM0') if idx==0 else ('MN1','H0','C1','MM1')
        p=_route_proposal(m,middle,raw,f'MID-{n}-{idx}',0.0001*n)
        if p is None:
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            rec={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_NO_CURRENT_PROPOSAL'};self.receipts.append(rec);log.append({'idx':idx,'middle_status':'NO_PROPOSAL'});return rec
        intent=mm.nominate_bounded_action_intent(p.proposal_id,m.act_ob())
        if intent['status']!='ACTION_INTENT_NOMINATED':
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            rec={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_ABSTAIN'};self.receipts.append(rec);log.append({'idx':idx,'middle_status':'ABSTAIN'});return rec
        ex=mm.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
        mout=mm.record_bounded_action_outcome_via_observation_basis(
            ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
            basis_capability_id='BASIS',basis_obligation=m.basis_ob(),evidence_id=f'MID-{n}-{idx}-OUT',capture_id=f'MID-{n}-{idx}-CAP')
        leaf=ex['handler_value'];self.last_next=mw.last_next;self.last_effect=mw.last_effect
        rec={'status':'WORKABLE','target':target,'nested':True,'local_mean':'OPAQUE-MIDDLE-CONTROLLER','higher_context':self.higher};self.receipts.append(rec)
        log.append({'idx':idx,'middle_status':'EXECUTED','leaf_target':leaf['target'],'middle_effect':mout['outcome']['actual_value_effect']})
        return rec
    tw.request=types.MethodType(nested_request,tw)
    return log


def _flip_middle_effect(middle):
    mw=middle['world'];orig=mw.request
    def flipped(target):
        rec=orig(target)
        if rec['status']=='WORKABLE':
            mw.last_effect=-mw.last_effect;mw.last_next='HIGHER-BAD' if mw.last_effect<0 else 'HIGHER-GOOD'
        return rec
    mw.request=flipped


def test_hidden_middle_effect_drift_stales_middle_and_top_from_each_layers_own_routed_actual_outcomes():
    m=_m();top=m.build_integrated();middle=m.build_integrated();log=_install_nested_actual_outcome(m,top,middle)
    try:
        raw=('TN','H0','C1','TM')
        # One successful nested sample demonstrates lawful selection at both levels.
        p,_,out=_execute_route_and_record(m,top,raw,'PRE',0.0)
        assert p.sequence==(top['bound'][1].capability_id,)
        assert out['outcome']['actual_value_effect']==2.0
        assert log[-1]['leaf_target']==middle['target_tokens'][1]
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        _flip_middle_effect(middle)
        # Hidden law change is not magically pre-observed.
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        # Each nested execution produces a middle routed outcome and a top routed
        # outcome. The same actual -2 consequence crosses the opaque request boundary.
        failures=0
        for j in range(16):
            if top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING':
                break
            p,ex,out=_execute_route_and_record(m,top,raw,f'DRIFT-{j}',0.001*(j+1))
            assert p.sequence==(top['bound'][1].capability_id,)
            assert out['outcome']['actual_value_effect'] < 0.0
            failures += 1
            if ex['handler_value']['status']=='WORKABLE':
                assert ex['handler_value']['local_mean']=='OPAQUE-MIDDLE-CONTROLLER'
                assert log[-1]['middle_effect'] < 0.0
        # One pre-drift success plus 15 failures already fills two 8-sample
        # windows below the 0.75 threshold, so fail-closed may occur before a
        # sixteenth hostile execution is even proposed.
        assert failures>=15
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert _route_proposal(m,top,raw,'AFTER',0.1) is None
        assert not hasattr(top['ms'],'cross_level_currentness_manager')
    finally:
        top['td'].cleanup();middle['td'].cleanup()


def test_middle_structural_drift_is_local_immediately_top_stales_only_after_observed_request_failures():
    m=_m();top=m.build_integrated();middle=m.build_integrated();log=_install_nested_actual_outcome(m,top,middle)
    try:
        raw=('SN','H0','C1','SM')
        # Middle private dependency moves. Middle knows immediately; top does not.
        middle['ms'].change_capability_dependency('REQ-BASE',reason='HARDEN-NESTED-MIDDLE-STRUCTURAL-DRIFT')
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        for j in range(16):
            p,ex,out=_execute_route_and_record(m,top,raw,f'STRUCT-{j}',0.001*j)
            assert p.sequence==(top['bound'][1].capability_id,)
            assert ex['handler_value']['status']=='REFUSED'
            assert ex['handler_value']['reason']=='MIDDLE_NO_CURRENT_PROPOSAL'
            assert out['outcome']['actual_value_effect'] < 0.0
        # Top has learned only from the consequence of its own emitted request.
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert not hasattr(top['ms'],'middle_registry')
        assert not hasattr(top['ms'],'cross_level_currentness_manager')
    finally:
        top['td'].cleanup();middle['td'].cleanup()
