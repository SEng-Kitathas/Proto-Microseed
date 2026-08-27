from __future__ import annotations

from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, act_ob
from tests.embodiment.test_ms1757_pass10_trial_from_admitted_history import install_history_surface, add_history_transition


def test_no_current_relational_candidate_abstains_without_closure_or_depth_claim():
    td,m,calls,world,t,dc=fixture()
    try:
        outcomes=install_history_surface(m)
        # One structural C ~= A->B witness is below the relational owner's fixed
        # support floor. This is absence of a current represented candidate only.
        rows=(('s0','A','m0'),('m0','B','e0'),('s0','C','e0'))
        for idx,row in enumerate(rows): add_history_transition(m,outcomes,idx,*row)
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        r=m.discover_and_arbitrate_endogenous_epistemic_trial_from_admitted_history(
            deficit_id='D',decision_context=dc,obligation=act_ob())
        assert r['status']=='ABSTAIN'
        assert r['reason']=='NO_CURRENT_EXECUTABLE_DISCRIMINATOR'
        assert r['candidate_surface_count']==0
        assert len(m.action_closure.intents)==before_intents and len(m.action_closure.executions)==before_exec
        text=repr(r).lower()
        assert 'saturat' not in text and 'closure' not in text and 'search_depth' not in text and 'increase_depth' not in text
        assert r['physical_truth_authority']==r['evidence_independence_authority']=='NONE'
    finally: td.cleanup()
