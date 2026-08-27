from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_state_only_epistemic_surprise_does_not_enter_value_bearing_action_outcome_learning():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        before={x.evidence_id for x in m._action_outcome_experiences()}
        t2=_execute_first_and_advance(m,trial,dc,next_state='sx',evidence_id='E-1840-X')
        bearing=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE'
        after={x.evidence_id for x in m._action_outcome_experiences()}
        assert 'E-1840-X' not in after
        assert after==before
        # A state-only probe result cannot create a value-effect predictive candidate by itself.
        candidates=m.nominate_action_outcome_predictive_candidates(min_support=2,min_consistency=0.51)
        assert all('E-1840-X' not in c.source_evidence_ids for c in candidates)
        assert bearing['model_replacement_authority']=='NONE'
        assert calls==['A']
    finally:
        td.cleanup()
