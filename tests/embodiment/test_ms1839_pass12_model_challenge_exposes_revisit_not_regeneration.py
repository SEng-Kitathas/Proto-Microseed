from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_model_space_challenge_exposes_revisit_surface_and_blocks_same_surface_regeneration():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        t2=_execute_first_and_advance(m,trial,dc,next_state='sx',evidence_id='E-1839-X')
        bearing=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE'
        assert m.epistemic_revisit_required_ids()==('D',)
        assert 'D' not in m.epistemic_development_pressure_ids()
        # The existing generated surface may still be reconstructible historically, but it cannot instantiate
        # a new trial while the deficit is awaiting revisit.
        again=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
        assert again['status']!='EPISTEMIC_TRIAL_INSTANTIATED', again
        assert not hasattr(m,'schedule_question_revisits')
        assert m.status()['question_revisit_scheduler']=='NOT_INTEGRATED__ELIGIBILITY_SURFACE_ONLY'
        assert calls==['A']
    finally:
        td.cleanup()
