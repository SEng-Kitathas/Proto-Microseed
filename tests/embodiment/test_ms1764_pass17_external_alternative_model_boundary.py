from __future__ import annotations

from microseed import Authority, Observation
from microseed.development.epistemic_action import EpistemicDecisionBearingContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob
from tests.embodiment.test_ms1757_pass10_trial_from_admitted_history import install_history_surface, add_history_transition


def test_same_admitted_history_can_change_information_verdict_only_when_external_relation_sets_change():
    td,m,calls,world,t,dc=fixture()
    try:
        outcomes=install_history_surface(m)
        rows=(('s0','A','m0'),('m0','B','e0'),('s0','C','e0'),('s1','A','m1'),('m1','B','e1'),('s1','C','e1'))
        for idx,row in enumerate(rows): add_history_transition(m,outcomes,idx,*row)
        m.observe_opaque_control_state(Observation('CS-RESET','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-RESET')

        before=tuple(m.store.events())
        informative=m.discover_and_arbitrate_endogenous_epistemic_trial_from_admitted_history(
            deficit_id='D',decision_context=dc,obligation=act_ob())
        same_models=EpistemicDecisionBearingContext((dc.relation_sets[0],dc.relation_sets[0]),dc.feasibility_routes)
        nondiscriminating=m.discover_and_arbitrate_endogenous_epistemic_trial_from_admitted_history(
            deficit_id='D',decision_context=same_models,obligation=act_ob())
        after=tuple(m.store.events())

        assert informative['admitted_sample_count']==nondiscriminating['admitted_sample_count']==6
        assert informative['candidate_surface_count']==nondiscriminating['candidate_surface_count']>=1
        assert informative['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        assert nondiscriminating['status']!='EPISTEMIC_TRIAL_INSTANTIATED'
        assert before==after  # arbitration/instantiation remains inert
        assert informative['physical_truth_authority']==informative['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
