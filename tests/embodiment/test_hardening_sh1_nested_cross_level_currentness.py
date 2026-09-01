
from __future__ import annotations

import importlib.util
from pathlib import Path
import types

from microseed import FeasibilityState


def _m():
    path=Path(__file__).with_name('test_ms2063_end_to_end_two_level_hierarchy_transfer.py')
    spec=importlib.util.spec_from_file_location('_sh1_ms2063',path)
    assert spec and spec.loader
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def _current_bucket_relation(fx):
    # Use bucket-1/class-1, which is backed by the globally CURRENT replacement relation.
    cid=fx['cap_ids'][1]
    return cid,fx['new_rel'][cid]


def _install_hidden_middle_phenotype(world,*,preserve_effect:bool):
    def request(self,target):
        target=str(target);f=self.target_feasibility(target)
        if f!=FeasibilityState.FEASIBLE:
            receipt={'status':f.value,'target':target,'child_state':self.child_state,'local_mean':None};self.receipts.append(receipt);return receipt
        idx=self.targets.index(target);child_bit=0 if self.child_state=='C0' else 1
        mean='Z0' if idx==child_bit else 'Z1';wanted=self.class_index();good=wanted is not None and idx==wanted
        if preserve_effect:
            self.last_next='HIGHER-GOOD' if good else 'HIGHER-BAD';self.last_effect=2.0 if good else -2.0
        else:
            self.last_next='HIGHER-BAD' if good else 'HIGHER-GOOD';self.last_effect=-2.0 if good else 2.0
        receipt={'status':'WORKABLE','target':target,'child_state':self.child_state,'local_mean':mean,'higher_context':self.higher,'hidden_phenotype':'SH1-PRESERVE' if preserve_effect else 'SH1-FLIP'}
        self.receipts.append(receipt);return receipt
    world.request=types.MethodType(request,world)


def _install_reality_coupled_middle(m,top,middle):
    tw=top['world'];mm=middle['ms'];mw=middle['world'];counter={'n':0};selected={};blocked=set();log=[]
    def nested_request(self,target):
        target=str(target);idx=self.targets.index(target);raw=('MID-N0','H0','C0','MID-M0') if idx==0 else ('MID-N1','H0','C1','MID-M1')
        # One genuine current routed selection per L1 request class. Subsequent
        # samples use the repository's unique exposure-proposal path only to gather
        # outcome evidence for that already-selected capability.
        if idx in blocked:
            self.last_next='NESTED-REFUSED';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_NO_CURRENT_PROPOSAL','local_mean':'OPAQUE-MIDDLE-CONTROLLER'}
            self.receipts.append(receipt);log.append({'top_target':target,'middle_proposal':None,'top_effect':self.last_effect});return receipt
        if idx not in selected:
            proposal=m.current_proposal(middle,raw,f'SH1-MID-SELECT-{idx}')
            if proposal is None:
                blocked.add(idx)
                self.last_next='NESTED-REFUSED';self.last_effect=-2.0
                receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_NO_CURRENT_PROPOSAL','local_mean':'OPAQUE-MIDDLE-CONTROLLER'}
                self.receipts.append(receipt);log.append({'top_target':target,'middle_proposal':None,'top_effect':self.last_effect});return receipt
            selected[idx]=proposal.sequence[0]
            assert selected[idx]==middle['bound'][idx].capability_id
        cid=selected[idx]
        # If internal currentness has explicitly failed, the subordinate must not
        # execute a cached leaf choice merely because it was once selected.
        if not mm.capabilities.is_current(cid) or mm.projection_conditioned_relation_routing_status(middle['routing_id'])['status']!='CURRENT_PROJECTION_CONDITIONED_ROUTING':
            self.last_next='NESTED-REFUSED';self.last_effect=-2.0
            receipt={'status':'REFUSED','target':target,'nested':True,'reason':'MIDDLE_CURRENTNESS_BLOCK','local_mean':'OPAQUE-MIDDLE-CONTROLLER'}
            self.receipts.append(receipt);log.append({'top_target':target,'middle_proposal':'CACHED-BUT-STALE','top_effect':self.last_effect});return receipt
        n=counter['n'];counter['n']+=1
        leaf,obs=m.execute_episode(mm,mw,cid,raw,9000+n)
        assert obs['status']=='ACTION_OUTCOME_OBSERVED'
        self.last_next=mw.last_next;self.last_effect=mw.last_effect
        receipt={'status':'WORKABLE','target':target,'nested':True,'local_mean':'OPAQUE-MIDDLE-CONTROLLER','higher_context':self.higher};self.receipts.append(receipt)
        log.append({'top_target':target,'middle_capability':cid,'leaf_target':leaf['target'],'leaf_local_mean':leaf['local_mean'],'middle_effect':mw.last_effect,'top_effect':self.last_effect})
        return receipt
    tw.request=types.MethodType(nested_request,tw)
    return log


def _select_top_once(m,top,raw,tag):
    p=m.current_proposal(top,raw,tag);assert p is not None
    return p.sequence[0]


def _top_sample(m,top,cid,raw,index):
    receipt,out=m.execute_episode(top['ms'],top['world'],cid,raw,12000+index)
    return receipt,out


def test_hidden_middle_effect_drift_is_not_clairvoyantly_propagated_but_actual_nested_outcomes_stale_both_layers():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        top_cid,top_rid=_current_bucket_relation(top);mid_cid,mid_rid=_current_bucket_relation(middle)
        top_sig=top['ms'].capabilities.contracts[top_cid].computed_signature_sha256();mid_sig=middle['ms'].capabilities.contracts[mid_cid].computed_signature_sha256()
        _install_hidden_middle_phenotype(middle['world'],preserve_effect=False);log=_install_reality_coupled_middle(m,top,middle)
        selected=_select_top_once(m,top,('SEL','H0','C1','SEL-M'),'SH1-TOP-SELECT-FLIP');assert selected==top_cid
        assert top['ms'].capabilities.contracts[top_cid].computed_signature_sha256()==top_sig
        assert middle['ms'].capabilities.contracts[mid_cid].computed_signature_sha256()==mid_sig
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        assert middle['ms'].action_outcome_predictive_relation_status(mid_rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        for i in range(16):
            receipt,_=_top_sample(m,top,selected,(f'T{i}','H0','C1',f'M{i}'),i)
            assert receipt['local_mean']=='OPAQUE-MIDDLE-CONTROLLER';assert top['world'].last_effect==-2.0
        assert len(log)==16 and all(x['middle_effect']==x['top_effect']==-2.0 for x in log)
        mw=middle['ms'].assess_action_outcome_predictive_currentness(mid_rid);tw=top['ms'].assess_action_outcome_predictive_currentness(top_rid)
        assert mw['status']==tw['status']=='DRIFT_WITNESS'
        assert mw['witness']['window_accuracies']==tw['witness']['window_accuracies']==[0.0,0.0]
        assert mw['witness']['drift_cause_authority']==tw['witness']['drift_cause_authority']=='NONE'
        assert middle['ms'].action_outcome_predictive_relation_status(mid_rid)['status']=='STALE_PREDICTIVE_RELATION'
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally: top['td'].cleanup();middle['td'].cleanup()


def test_effect_preserving_middle_phenotype_change_remains_current_at_both_layers_after_reality_contact():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        top_cid,top_rid=_current_bucket_relation(top);_,mid_rid=_current_bucket_relation(middle)
        _install_hidden_middle_phenotype(middle['world'],preserve_effect=True);log=_install_reality_coupled_middle(m,top,middle)
        selected=_select_top_once(m,top,('SEL','H0','C1','SEL-M'),'SH1-TOP-SELECT-PRESERVE');assert selected==top_cid
        for i in range(16):
            _top_sample(m,top,selected,(f'P{i}','H0','C1',f'PM{i}'),100+i);assert top['world'].last_effect==2.0
        mw=middle['ms'].assess_action_outcome_predictive_currentness(mid_rid);tw=top['ms'].assess_action_outcome_predictive_currentness(top_rid)
        assert mw['status']==tw['status']=='CURRENT_WITHIN_BOUNDS'
        assert mw['witness']['window_accuracies']==tw['witness']['window_accuracies']==[1.0,1.0]
        assert all(x['middle_effect']==x['top_effect']==2.0 for x in log)
    finally: top['td'].cleanup();middle['td'].cleanup()


def test_explicit_middle_dependency_drift_does_not_magically_stale_top_but_nested_refusal_reality_eventually_does():
    m=_m();top=m.build_integrated();middle=m.build_integrated()
    try:
        top_cid,top_rid=_current_bucket_relation(top);log=_install_reality_coupled_middle(m,top,middle)
        selected=_select_top_once(m,top,('SEL','H0','C1','SEL-M'),'SH1-TOP-SELECT-DRIFT');assert selected==top_cid
        top_sig=top['ms'].capabilities.contracts[top_cid].computed_signature_sha256()
        stale=middle['ms'].change_capability_dependency('REQ-BASE',reason='SH1-MIDDLE-REQUEST-DRIFT')
        assert set(middle['cap_ids']).issubset(set(stale))
        assert middle['ms'].projection_conditioned_relation_routing_status(middle['routing_id'])['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        assert top['ms'].capabilities.contracts[top_cid].computed_signature_sha256()==top_sig
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='CURRENT_PREDICTIVE_RELATION'
        leaf_before=len(middle['world'].receipts)
        for i in range(16):
            receipt,_=_top_sample(m,top,selected,(f'D{i}','H0','C1',f'DM{i}'),200+i)
            assert receipt['status']=='REFUSED';assert receipt['reason'] in {'MIDDLE_NO_CURRENT_PROPOSAL','MIDDLE_CURRENTNESS_BLOCK'};assert top['world'].last_effect==-2.0
        assert len(middle['world'].receipts)==leaf_before
        assert len(log)==16 and all(x.get('middle_proposal') in {None,'CACHED-BUT-STALE'} for x in log)
        tw=top['ms'].assess_action_outcome_predictive_currentness(top_rid)
        assert tw['status']=='DRIFT_WITNESS';assert tw['witness']['window_accuracies']==[0.0,0.0];assert tw['witness']['drift_cause_authority']=='NONE'
        assert top['ms'].action_outcome_predictive_relation_status(top_rid)['status']=='STALE_PREDICTIVE_RELATION'
    finally: top['td'].cleanup();middle['td'].cleanup()
