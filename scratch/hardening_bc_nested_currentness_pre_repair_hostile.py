# PRE-REPAIR / EARLY HARDENING HOSTILE SPECIMEN — NOT POST-REPAIR ACCEPTANCE
# This fixture expected the 16th bad routed proposal to remain available.
# The repair correctly fails closed before that point once two full bad windows
# exist. Preserved for defect chronology; superseded by
# tests/embodiment/test_hardening_bc_nested_currentness_repair.py.


from __future__ import annotations

import importlib.util
from pathlib import Path
import types


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_hard_bc_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _current_unique(m,fx,raw,tag,value):
    m.prepare_current(fx,raw,tag)
    fx['ms'].observe_value_state('V',float(value))
    return fx['ms'].nominate_current_raw_projection_conditioned_rehearsal(
        (),m.options(fx),start_state_id='ALIAS',value_id='V',projection_routing_id=fx['routing_id'],
        routing_task_id='MS2063',routing_channel_id='opaque-control',
    )


def _record_outcome(m,fx,execution_id,tag):
    return fx['ms'].record_bounded_action_outcome_via_observation_basis(
        execution_id,observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),
        evidence_id=f'HARD-BC-OUT-{tag}',capture_id=f'HARD-BC-CAP-{tag}',
    )


def _install_reality_coupled_middle(m,top,middle):
    top_world=top['world']; middle_ms=middle['ms']; middle_world=middle['world']; log=[]; counter={'n':0}
    def request(self,target):
        target=str(target); idx=self.targets.index(target)
        raw=('MID-HARD-N0','H0','C0','MID-HARD-M0') if idx==0 else ('MID-HARD-N1','H0','C1','MID-HARD-M1')
        n=counter['n']; counter['n']+=1
        proposal=_current_unique(m,middle,raw,f'MID-{n}',0.01+(n%80)*0.005)
        if proposal is None:
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_NO_CURRENT_PROPOSAL'}
            self.receipts.append(receipt);log.append({'n':n,'top_target':target,'middle_proposal':None,'top_effect':-2.0});return receipt
        intent=middle_ms.nominate_bounded_action_intent(proposal.proposal_id,m.act_ob())
        if intent['status']!='ACTION_INTENT_NOMINATED':
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_ABSTAIN'}
            self.receipts.append(receipt);log.append({'n':n,'top_target':target,'middle_proposal':proposal.proposal_id,'middle_intent':intent['status'],'top_effect':-2.0});return receipt
        ex=middle_ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
        leaf=ex['handler_value'];out=_record_outcome(m,middle,ex['execution']['execution_id'],f'MID-{n}')
        # Parent consequence is now reality-coupled to the middle controller's actual
        # observed consequence, not manufactured from the parent's desired class.
        self.last_effect=float(middle_world.last_effect)
        self.last_next='HIGHER-GOOD' if self.last_effect>0 else 'HIGHER-BAD'
        receipt={'status':'WORKABLE','target':target,'nested':True,'local_mean':'OPAQUE-MIDDLE-CONTROLLER','higher_context':self.higher}
        self.receipts.append(receipt)
        log.append({'n':n,'top_target':target,'middle_proposal':proposal.proposal_id,'middle_capability':proposal.sequence[0],
                    'leaf_target':leaf['target'],'middle_effect':middle_world.last_effect,'top_effect':self.last_effect,'middle_outcome':out['status']})
        return receipt
    top_world.request=types.MethodType(request,top_world)
    return log


def _execute_top_episode(m,top,raw,tag,value):
    p=_current_unique(m,top,raw,tag,value);assert p is not None
    intent=top['ms'].nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=top['ms'].execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    out=_record_outcome(m,top,ex['execution']['execution_id'],f'TOP-{tag}')
    return p,ex,out


def _flip_middle_effect_only(middle):
    world=middle['world']; original=world.request
    def flipped(target):
        receipt=original(target)
        if receipt.get('status')=='WORKABLE':
            world.last_effect=-float(world.last_effect)
            world.last_next='HIGHER-GOOD' if world.last_effect>0 else 'HIGHER-BAD'
            receipt=dict(receipt);receipt['hidden_effect_regime']='FLIPPED';world.receipts[-1]=receipt
        return receipt
    world.request=flipped


def _class1_relation(fx):
    cid=fx['bound'][1].capability_id
    return cid,fx['new_rel'][cid]


def test_hidden_middle_empirical_drift_is_private_until_parent_observes_nested_request_failure():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        log=_install_reality_coupled_middle(m,top,middle)
        top_cid,top_rid=_class1_relation(top);mid_cid,mid_rid=_class1_relation(middle)
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        # Change only the middle external effect law. Then generate routed outcomes
        # *inside the middle controller only*. The parent receives no request/outcome
        # evidence at all during this phase.
        _flip_middle_effect_only(middle)
        for i in range(16):
            p,ex,out=_execute_top_episode(m,middle,(f'MD{i}','H0','C1',f'MDM{i}'),f'MIDDLE-DRIFT-{i}',0.01+i*0.005)
            assert p.sequence==(mid_cid,)
            assert ex['handler_value']['status']=='WORKABLE'
            assert middle['world'].last_effect==-2.0
            assert out['status']=='ACTION_OUTCOME_OBSERVED'
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'

        # No magical upward epistemic sharing: a separate parent's registry remains
        # current because it has received no evidence about the subordinate change.
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        # Now the parent acts. The stale middle refuses before leaf execution; those
        # refusals become the parent's own actual request-effect evidence.
        leaf_before=len(middle['world'].receipts)
        parent_failures=0
        for i in range(16):
            if top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING':
                break
            p,ex,out=_execute_top_episode(m,top,(f'T{i}','H0','C1',f'TM{i}'),f'PARENT-AFTER-MID-STALE-{i}',0.02+i*0.005)
            assert p.sequence==(top_cid,)
            assert ex['handler_value']['status']=='REFUSED'
            assert ex['handler_value']['reason']=='MIDDLE_NO_CURRENT_PROPOSAL'
            assert top['world'].last_effect==-2.0
            assert out['status']=='ACTION_OUTCOME_OBSERVED'
            parent_failures+=1
        assert parent_failures==16
        assert len(middle['world'].receipts)==leaf_before
        assert all(x.get('middle_proposal') is None for x in log)
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'

        # Optional global relation assessment reaches the same bounded evidence
        # conclusion, but scoped routing already failed closed without waiting for it.
        top_w=top['ms'].assess_action_outcome_predictive_currentness(top_rid)
        assert top_w['status']=='DRIFT_WITNESS'
        assert top_w['witness']['window_accuracies']==[0.0,0.0]
        assert top_w['witness']['drift_cause_authority']=='NONE'
    finally:
        top['td'].cleanup();middle['td'].cleanup()

def test_explicit_middle_dependency_drift_blocks_middle_before_leaf_execution_but_parent_stales_only_from_observed_refusals():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        log=_install_reality_coupled_middle(m,top,middle)
        top_cid,top_rid=_class1_relation(top);_,mid_rid=_class1_relation(middle)
        stale=middle['ms'].change_capability_dependency('REQ-BASE',reason='HARD-BC-MIDDLE-REQUEST-DEPENDENCY-DRIFT')
        assert middle['bound'][1].capability_id in stale
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'
        leaf_before=len(middle['world'].receipts)
        for i in range(16):
            p,ex,out=_execute_top_episode(m,top,(f'R{i}','H0','C1',f'RM{i}'),f'REF-{i}',0.04+i*0.005)
            assert p.sequence==(top_cid,)
            assert ex['handler_value']['status']=='REFUSED'
            assert ex['handler_value']['reason']=='MIDDLE_NO_CURRENT_PROPOSAL'
            assert top['world'].last_effect==-2.0
            assert out['status']=='ACTION_OUTCOME_OBSERVED'
        assert len(middle['world'].receipts)==leaf_before
        assert all(x.get('middle_proposal') is None for x in log)
        # Parent is not structurally stale merely because a separate subordinate is;
        # its own observed request-effect evidence is the lawful demotion route.
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        top_w=top['ms'].assess_action_outcome_predictive_currentness(top_rid)
        assert top_w['status']=='DRIFT_WITNESS'
        assert top_w['witness']['window_accuracies']==[0.0,0.0]
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
    finally:
        top['td'].cleanup();middle['td'].cleanup()
