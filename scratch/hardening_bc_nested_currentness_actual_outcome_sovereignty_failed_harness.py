# FAILED EXPLORATORY HARNESS — NOT SCIENTIFIC VERDICT
# Created during Wave-3 recovery. Failed on wrong receipt-field assumption and
# deterministic rehearsal-ID collision before reaching the intended verdict.
# Superseded by the already-existing focused repair fixtures on this branch.


from __future__ import annotations

import importlib.util
from pathlib import Path
import types

from microseed import FeasibilityState


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_hardening_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _install_outcome_coupled_middle(m, top, middle):
    top_world=top['world']; middle_ms=middle['ms']; middle_world=middle['world']
    log=[]; counter={'n':0}
    def nested_request(self,target):
        target=str(target); top_idx=self.targets.index(target)
        if self.target_feasibility(target)!=FeasibilityState.FEASIBLE:
            receipt={'status':self.target_feasibility(target).value,'target':target,'nested':True}
            self.receipts.append(receipt);return receipt
        raw=(('MID-N0','H0','C0','MID-M0') if top_idx==0 else ('MID-N1','H0','C1','MID-M1'))
        tag=f'HARD-MID-{counter["n"]}-{top_idx}';counter['n']+=1
        proposal=m.current_proposal(middle,raw,tag)
        if proposal is None:
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_NO_CURRENT_PROPOSAL'}
            self.receipts.append(receipt);log.append({'top_idx':top_idx,'middle_proposal':None});return receipt
        intent=middle_ms.nominate_bounded_action_intent(proposal.proposal_id,m.act_ob())
        if intent['status']!='ACTION_INTENT_NOMINATED':
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_ABSTAIN'}
            self.receipts.append(receipt);log.append({'top_idx':top_idx,'middle_proposal':proposal.proposal_id,'middle_intent_status':intent['status']});return receipt
        ex=middle_ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
        leaf=ex['handler_value']
        out=middle_ms.record_bounded_action_outcome_via_observation_basis(
            ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
            basis_capability_id='BASIS',basis_obligation=m.basis_ob(),
            evidence_id=f'HARD-MID-OUT-{counter["n"]}',capture_id=f'HARD-MID-OUT-CAP-{counter["n"]}',
        )
        assert out['status']=='ACTION_OUTCOME_OBSERVED'
        # Critical hardening change from the original C_SCALE fixture: L2 observes
        # the consequence actually realized by L1/L0. No synthetic top success label.
        self.last_next=middle_world.last_next
        self.last_effect=middle_world.last_effect
        receipt={'status':'WORKABLE','target':target,'nested':True,'child_state':self.child_state,
                 'local_mean':'OPAQUE-MIDDLE-CONTROLLER','higher_context':self.higher}
        self.receipts.append(receipt)
        log.append({'top_idx':top_idx,'middle_capability_id':proposal.sequence[0],
                    'leaf_target':leaf['target'],'leaf_local_mean':leaf['local_mean'],
                    'middle_next':middle_world.last_next,'middle_effect':middle_world.last_effect})
        return receipt
    top_world.request=types.MethodType(nested_request,top_world)
    return log


def _execute_top_and_record(m,top,raw,tag):
    ms=top['ms'];p=m.current_proposal(top,raw,tag);assert p is not None
    intent=ms.nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=ms.execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
    out=ms.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=m.obs_ob(),
        basis_capability_id='BASIS',basis_obligation=m.basis_ob(),
        evidence_id=f'HARD-TOP-OUT-{tag}',capture_id=f'HARD-TOP-OUT-CAP-{tag}',
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return p,ex,out


def _flip_middle_good_effect(middle):
    world=middle['world']; original=world.request
    def drifted(self,target):
        receipt=original(target)
        if receipt['status']=='WORKABLE' and self.last_effect==2.0:
            self.last_next='HIGHER-BAD';self.last_effect=-2.0
            receipt=dict(receipt);receipt['hidden_effect_regime']='FLIPPED_AFTER_LOCAL_EXECUTION'
            self.receipts[-1]=receipt
        return receipt
    world.request=types.MethodType(drifted,world)


def test_hidden_middle_effect_drift_is_not_magically_visible_upward_and_each_level_stales_from_its_own_actual_outcomes():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        log=_install_outcome_coupled_middle(m,top,middle)
        top_cid=top['bound'][1].capability_id; mid_cid=middle['bound'][1].capability_id
        top_rel=top['new_rel'][top_cid]; mid_rel=middle['new_rel'][mid_cid]
        assert top['ms'].action_outcome_predictive_relation_status(top_rel)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert middle['ms'].action_outcome_predictive_relation_status(mid_rel)['status']=='CURRENT_PREDICTIVE_RELATION'

        # Baseline nested consequence is genuinely inherited from the middle outcome.
        _,_,base=_execute_top_and_record(m,top,('BASE','H0','C1','BASE-M'),'BASE')
        assert middle['world'].last_effect==top['world'].last_effect==2.0
        assert base['experience']['actual_value_effect']==2.0

        # Internal middle world law changes without touching capability/projection/
        # routing signatures. Neither controller may know this before new outcomes.
        top_sig=top['ms'].capabilities.contracts[top_cid].computed_signature_sha256()
        mid_sig=middle['ms'].capabilities.contracts[mid_cid].computed_signature_sha256()
        _flip_middle_good_effect(middle)
        assert top['ms'].capabilities.contracts[top_cid].computed_signature_sha256()==top_sig
        assert middle['ms'].capabilities.contracts[mid_cid].computed_signature_sha256()==mid_sig
        assert top['ms'].action_outcome_predictive_relation_status(top_rel)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert middle['ms'].action_outcome_predictive_relation_status(mid_rel)['status']=='CURRENT_PREDICTIVE_RELATION'

        # Two full failure windows at the same class-1 relation. L2 never receives
        # middle relation IDs/currentness witnesses; it sees only changed consequences.
        for i in range(16):
            _,ex,out=_execute_top_and_record(m,top,(f'N{i}','H0','C1',f'M{i}'),f'DRIFT-{i}')
            assert ex['handler_value']['local_mean']=='OPAQUE-MIDDLE-CONTROLLER'
            assert 'middle_relation_id' not in ex['handler_value']
            assert top['world'].last_effect==middle['world'].last_effect==-2.0
            assert out['experience']['actual_value_effect']==-2.0

        # Middle can now establish its own drift from its own recorded leaf outcomes.
        mw=middle['ms'].assess_action_outcome_predictive_currentness(mid_rel)
        assert mw['status']=='DRIFT_WITNESS'
        assert mw['witness']['window_accuracies']==[0.0,0.0]
        assert middle['ms'].action_outcome_predictive_relation_status(mid_rel)['status']=='STALE_PREDICTIVE_RELATION'

        # No magical cross-registry invalidation: top remains structurally/currentness
        # current until it assesses its own post-admission consequences.
        assert top['ms'].action_outcome_predictive_relation_status(top_rel)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='CURRENT_PROJECTION_CONDITIONED_ROUTING'

        tw=top['ms'].assess_action_outcome_predictive_currentness(top_rel)
        assert tw['status']=='DRIFT_WITNESS'
        # One baseline + sixteen drift rows means the assessor consumes two complete
        # eight-row windows: first contains one success + seven failures, second all failures.
        assert tw['witness']['window_accuracies']==[0.125,0.0]
        assert top['ms'].action_outcome_predictive_relation_status(top_rel)['status']=='STALE_PREDICTIVE_RELATION'
        assert top['ms'].projection_conditioned_relation_routing_status(top['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert all('middle_relation_id' not in row for row in log)
    finally:
        top['td'].cleanup();middle['td'].cleanup()


def test_once_middle_has_local_drift_witness_top_request_may_be_attempted_but_subordinate_currentness_blocks_leaf_execution():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        _install_outcome_coupled_middle(m,top,middle);_flip_middle_good_effect(middle)
        mid_cid=middle['bound'][1].capability_id;mid_rel=middle['new_rel'][mid_cid]
        # Generate only middle post-admission evidence through nested requests. Top
        # outcomes are also recorded, but top currentness is intentionally unassessed.
        for i in range(16): _execute_top_and_record(m,top,(f'X{i}','H0','C1',f'Y{i}'),f'MIDSTALE-{i}')
        assert middle['ms'].assess_action_outcome_predictive_currentness(mid_rel)['status']=='DRIFT_WITNESS'
        before_leaf=len(middle['world'].receipts)
        p=m.current_proposal(top,('AFTER','H0','C1','AFTER-M'),'AFTER-MID-STALE')
        assert p is not None
        intent=top['ms'].nominate_bounded_action_intent(p.proposal_id,m.act_ob());assert intent['status']=='ACTION_INTENT_NOMINATED'
        ex=top['ms'].execute_bounded_action(intent['intent']['intent_id'],m.act_ob());assert ex['status']=='ACTION_EXECUTED'
        assert ex['handler_value']['status']=='REFUSED'
        assert ex['handler_value']['reason']=='MIDDLE_NO_CURRENT_PROPOSAL'
        assert len(middle['world'].receipts)==before_leaf
    finally:
        top['td'].cleanup();middle['td'].cleanup()
