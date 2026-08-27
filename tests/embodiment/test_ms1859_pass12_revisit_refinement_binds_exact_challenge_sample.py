from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1858_pass11_live_second_step_challenge_participates_in_owned_history_refinement import _install,_run_step,_add_history_pair


def test_revisit_exposes_only_refinement_containing_exact_admitted_challenge_sample():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        outcomes={};_install(m,outcomes)
        t1,b1=_run_step(m,outcomes,trial,dc,'A','s1','LIVE-A')
        assert b1['status']=='CONSENSUS_NONDISCRIMINATING'
        _,b2=_run_step(m,outcomes,t1,dc,'B','sx','LIVE-B')
        assert b2['status']=='MODEL_SPACE_CHALLENGE' and b2['revisit_status']=='REVISIT_REQUIRED'
        _add_history_pair(m,outcomes,0,'s0','sx');_add_history_pair(m,outcomes,1,'r','s2');_add_history_pair(m,outcomes,2,'r','s2')
        result=m.derive_revisit_one_step_visible_history_refinement('D')
        assert result['status']=='REVISIT_ONE_STEP_VISIBLE_HISTORY_REFINEMENT_CANDIDATE',result
        c=result['refinement']
        assert (c.start_token,c.action_token)==('s1','B')
        assert set(c.context_outcomes)=={('s0','sx',2),('r','s2',2)}
        assert result['challenge_sample_ids']
        assert set(result['challenge_sample_ids']).issubset(set(c.source_sample_ids))
        assert result['truth_authority']==result['hidden_state_authority']==result['model_replacement_authority']=='NONE'
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert calls==['A','B']
    finally:td.cleanup()
