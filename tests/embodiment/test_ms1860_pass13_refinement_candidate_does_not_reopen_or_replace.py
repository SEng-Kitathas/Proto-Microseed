from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install,_run_step,_add_history_pair
from tests.embodiment.test_ms1837_pass10_full_generated_three_tick_realization import _add_feas_c


def test_challenge_bound_refinement_is_proposal_only_and_cannot_reopen_or_replace_model():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={};_install(m,outcomes)
        t1,b1=_run_step(m,outcomes,trial,dc,'A','s1','LIVE-A')
        assert b1['status']=='CONSENSUS_NONDISCRIMINATING',b1
        t2,b2=_run_step(m,outcomes,t1,dc,'B','sx','LIVE-B')
        assert b2['status']=='MODEL_SPACE_CHALLENGE' and b2['revisit_status']=='REVISIT_REQUIRED',b2
        _add_history_pair(m,outcomes,0,'s0','sx')
        _add_history_pair(m,outcomes,1,'r','s2')
        _add_history_pair(m,outcomes,2,'r','s2')

        before_state=m.epistemic_deficits.records['D'].state.value
        before_intents=len(m.action_closure.intents)
        before_value_experiences=len(m._action_outcome_experiences())
        before_relations=len(m.action_outcome_learning.relations)

        refinement=m.derive_revisit_one_step_visible_history_refinement('D')
        assert refinement['status']=='REVISIT_ONE_STEP_VISIBLE_HISTORY_REFINEMENT_CANDIDATE',refinement
        assert refinement['model_replacement_authority']=='NONE'
        assert refinement['execution_authority']=='NONE'
        assert refinement['truth_authority']=='NONE'

        # Deriving structural refinement does not mutate the deficit lifecycle,
        # manufacture value-bearing experience/relation, or nominate an action.
        assert before_state=='REVISIT_REQUIRED'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert len(m._action_outcome_experiences())==before_value_experiences
        assert len(m.action_outcome_learning.relations)==before_relations
        assert len(m.action_closure.intents)==before_intents

        # The still-open old trial cannot continue merely because a structural
        # refinement candidate now exists.  The existing need gate requires a
        # current ACTION_LIMITED deficit and therefore stops at revisit.
        _add_feas_c(m)
        continuation=m.nominate_endogenous_epistemic_program_step_intent_from_current_surface(t2,dc,act_ob())
        assert continuation['status']=='ABSTAIN',continuation
        assert continuation['reason']=='ACTION_LIMITED_OR_EXACT_BOUND_PROBE_AVAILABLE_REQUIRED',continuation
        assert len(m.action_closure.intents)==before_intents
        assert calls==['A','B']
    finally:
        td.cleanup()
