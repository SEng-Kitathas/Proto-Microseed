from pathlib import Path
from microseed import Microseed
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def _count(m,wid):
    return sum(1 for e in m.store.events() if e.get('kind')=='EPISTEMIC_PROGRAM_STEP_BEARING_WITNESS' and e.get('payload',{}).get('witness_id')==wid)


def test_program_step_bearing_replay_is_suppressed_across_restart_without_restoring_trial_authority():
    td,m,calls,trial,dc=_generated_fixture(); root=Path(td.name)
    try:
        t2=_execute_first_and_advance(m,trial,dc,next_state='sx',evidence_id='E-1844-X')
        first=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        wid=first['witness']['witness_id']
        assert _count(m,wid)==1
        del m
        m2=Microseed(root)
        replay=m2.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        assert replay['status']=='MODEL_SPACE_CHALLENGE'
        assert replay['duplicate'] is True
        assert replay['witness']['witness_id']==wid
        assert _count(m2,wid)==1
        assert m2.epistemic_revisit_required_ids()==('D',)
        assert not hasattr(m2,'trial_registry')
    finally:
        td.cleanup()
