from pathlib import Path
from microseed import Microseed
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def test_model_challenge_revisit_survives_restart_but_trial_and_effect_authority_do_not():
    td,m,calls,trial,dc=_generated_fixture()
    root=Path(td.name)
    try:
        t2=_execute_first_and_advance(m,trial,dc,next_state='sx',evidence_id='E-1841-X')
        bearing=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        assert bearing['status']=='MODEL_SPACE_CHALLENGE'
        assert m.epistemic_revisit_required_ids()==('D',)
        del m
        m2=Microseed(root)
        assert m2.epistemic_revisit_required_ids()==('D',)
        assert 'D' not in m2.epistemic_development_pressure_ids()
        # Trials are ephemeral carriers; there is no program/trial registry to resurrect.
        assert not hasattr(m2,'epistemic_program_trials')
        assert not hasattr(m2,'trial_registry')
        # Capability history may replay, but executable handlers/contracts are not restored as current effect authority.
        assert all(c.handler is None for c in m2.capabilities.contracts.values())
        assert m2.status()['question_revisit_scheduler']=='NOT_INTEGRATED__ELIGIBILITY_SURFACE_ONLY'
    finally:
        td.cleanup()
