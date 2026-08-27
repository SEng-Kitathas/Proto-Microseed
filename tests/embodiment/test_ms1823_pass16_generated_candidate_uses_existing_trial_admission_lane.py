from microseed import Authority, Observation
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture,act_ob
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_effect_c,_add_recurrent_chain
from tests.embodiment.test_ms1822_pass15_three_locus_shared_background_priority import _add_shared_fallback


def test_owned_three_locus_generated_program_enters_same_inert_trial_admission_lane():
    td,m,calls,_,_,_=fixture()
    try:
        _add_effect_c(m,calls); _add_shared_fallback(m,calls)
        for prefix,effect,end in (('P1',1.0,'u'),('P2',1.0,'u'),('N1',-1.0,'v'),('N2',-1.0,'v')):
            _add_recurrent_chain(m,prefix,effect,end)
        m.observe_opaque_control_state(Observation('CS-1823','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1823')
        before_intents=len(m.action_closure.intents); before_exec=len(m.action_closure.executions)
        result=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
        assert result['status']=='EPISTEMIC_TRIAL_INSTANTIATED', result
        assert result['trial'].steps==('A','B','C')
        assert result['priority']['commitment']=='YES' and result['information']['commitment']=='YES'
        assert result['generated_program_candidate_count']>=1
        assert result['generated_program_authority']=='PROPOSAL_ONLY_EPHEMERAL'
        assert result['closure_authority']==result['world_model_authority']==result['execution_authority']=='NONE'
        assert len(m.action_closure.intents)==before_intents and len(m.action_closure.executions)==before_exec
        assert calls==[]
    finally:
        td.cleanup()
