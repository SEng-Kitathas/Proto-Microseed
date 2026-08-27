from dataclasses import replace

import pytest

from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext
from microseed.development.relational_algebra import OpaqueTransitionSample
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, candidate, act_ob, rel


def _context_without_routes(dc):
    return EpistemicDecisionBearingContext(dc.relation_sets, ())


def _samples_two_origins():
    return (
        OpaqueTransitionSample('a0','oa0','s0','A','m0','F',0),
        OpaqueTransitionSample('b0','ob0','m0','B','e0','F',0),
        OpaqueTransitionSample('c0','oc0','s0','C','e0','F',0),
        OpaqueTransitionSample('a1','oa1','s1','A','m1','F',0),
        OpaqueTransitionSample('b1','ob1','m1','B','e1','F',0),
        OpaqueTransitionSample('c1','oc1','s1','C','e1','F',0),
    )


def _samples_one_origin_family():
    return (
        OpaqueTransitionSample('a0','o0','s0','A','m0','F',0),
        OpaqueTransitionSample('b0','o0','m0','B','e0','F',0),
        OpaqueTransitionSample('c0','o0','s0','C','e0','F',0),
    )


def test_one_live_candidate_instantiates_inert_trial_without_intent_or_effect():
    td,m,calls,world,t,dc=fixture()
    try:
        before=(len(m.action_closure.intents),len(m.action_closure.executions))
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        assert r['trial'].status=='OPEN'
        assert r['execution_authority']==r['truth_authority']=='NONE'
        assert (len(m.action_closure.intents),len(m.action_closure.executions))==before
        assert calls==[]
    finally: td.cleanup()


def test_nondiscriminating_candidate_abstains_without_trial_exposure():
    td,m,calls,world,t,dc=fixture()
    try:
        same=EpistemicDecisionBearingContext((dc.relation_sets[0],dc.relation_sets[0]),())
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=same,obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert 'DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION' in r['candidate_reasons'] or r['reason']=='DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION'
        assert calls==[]
    finally: td.cleanup()


@pytest.mark.parametrize('state', ['REFUSED','UNKNOWN'])
def test_first_step_nonfeasible_abstains_before_priority_relabels_it(state):
    td,m,calls,world,t,dc=fixture()
    try:
        world['A']=state
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        reasons='|'.join(r.get('candidate_reasons',(r.get('reason',''),)))
        assert reasons == ('EPISTEMIC_PROGRAM_STEP_REFUSED' if state=='REFUSED' else 'EPISTEMIC_PROGRAM_STEP_UNRESOLVED')
        assert calls==[]
    finally: td.cleanup()


def test_missing_first_step_feasibility_route_stays_a_route_failure_not_priority_failure():
    td,m,calls,world,t,dc=fixture()
    try:
        m.capabilities.contracts['FEAS-A'].currentness='STALE'
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert 'NO_CURRENT_FIRST_STEP_FEASIBILITY_ROUTE' in r.get('candidate_reasons',(r.get('reason'),))
        assert calls==[]
    finally: td.cleanup()


def test_stale_candidate_frame_blocks_instantiation():
    td,m,calls,world,t,dc=fixture()
    try:
        m.change_operational_frame('F',reason='FRAME_DRIFT')
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert any('RELATIONAL_FRAME_NOT_CURRENT' in x for x in r['candidate_reasons'])
        assert calls==[]
    finally: td.cleanup()


def test_no_represented_candidate_abstains_not_deeper_search():
    td,m,calls,world,t,dc=fixture()
    try:
        r=m.arbitrate_endogenous_epistemic_trial_candidates((),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert r['execution_authority']=='NONE'
        assert calls==[]
    finally: td.cleanup()


def test_same_program_different_relation_provenance_remains_multiple():
    td,m,calls,world,t,dc=fixture()
    try:
        c1=candidate()
        c2=replace(c1,candidate_id=c1.candidate_id+'-other',support_origin_signatures=('different-origin-signature',))
        r=m.arbitrate_endogenous_epistemic_trial_candidates((c1,c2),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES'
        assert set(r['candidate_ids'])=={c1.candidate_id,c2.candidate_id}
        assert r['selection_authority']==r['execution_authority']=='NONE'
        assert calls==[]
    finally: td.cleanup()


def test_candidate_input_order_cannot_change_ambiguous_result():
    td,m,calls,world,t,dc=fixture()
    try:
        c1=candidate(); c2=replace(c1,candidate_id=c1.candidate_id+'-other',support_origin_signatures=('different-origin-signature',))
        a=m.arbitrate_endogenous_epistemic_trial_candidates((c1,c2),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        b=m.arbitrate_endogenous_epistemic_trial_candidates((c2,c1),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert a['status']==b['status']=='MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES'
        assert a['candidate_ids']==b['candidate_ids']
    finally: td.cleanup()


def test_relational_discovery_can_supply_candidate_surface_without_caller_selection():
    td,m,calls,world,t,dc=fixture()
    try:
        r=m.discover_and_arbitrate_endogenous_epistemic_trial(_samples_two_origins(),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['candidate_surface_count']>=1
        assert r['sample_provenance_authority']=='SUPPLIED_FRAME_BOUND_VALUES_ONLY'
        assert r['observation_admission_authority']==r['evidence_independence_authority']=='NONE'
        assert calls==[]
    finally: td.cleanup()


def test_single_origin_family_cannot_tune_support_floor_through_trial_wrapper():
    td,m,calls,world,t,dc=fixture()
    try:
        r=m.discover_and_arbitrate_endogenous_epistemic_trial(_samples_one_origin_family(),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['candidate_surface_count']==0
        assert r['status']=='ABSTAIN'
        assert calls==[]
    finally: td.cleanup()


def test_caller_feasibility_routes_are_ignored_by_new_front_end():
    td,m,calls,world,t,dc=fixture()
    try:
        bogus=EpistemicDecisionBearingContext(dc.relation_sets,(('A','DOES-NOT-EXIST',dc.feasibility_routes[0][2]),))
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=bogus,obligation=act_ob())
        assert r['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        assert calls==[]
    finally: td.cleanup()


def test_route_disagreement_blocks_trial_as_unknown_not_pick_first():
    from microseed import CapabilityContract, QualificationState
    td,m,calls,world,t,dc=fixture()
    try:
        m.register_capability(CapabilityContract(
            'FEAS-A-2','feas-A-2',{'target_capability_id':'A'},{},(),(),Authority.DERIVED_READ_ONLY,('MS1746',),'CURRENT',{},
            dependencies=('A',),query_obligation_id='QF-A-2',qualification=QualificationState.SHADOW_QUALIFIED,
            handler=lambda **_:{'feasibility':'REFUSED','reason':'DISAGREE'},operational_scope_id='S'))
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert calls==[]
    finally: td.cleanup()


def test_current_control_state_missing_blocks_trial_without_fabrication():
    td,m,calls,world,t,dc=fixture()
    try:
        m.action_closure.current_state=None
        r=m.arbitrate_endogenous_epistemic_trial_candidates((candidate(),),deficit_id='D',decision_context=_context_without_routes(dc),obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert 'CURRENT_CONTROL_STATE_REQUIRED' in r['candidate_reasons'] or r['reason']=='CURRENT_CONTROL_STATE_REQUIRED'
        assert calls==[]
    finally: td.cleanup()
