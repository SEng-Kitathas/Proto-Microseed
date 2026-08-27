from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture, _execute_first_and_advance


def _bearing_events(m,wid):
    return [e for e in m.store.events() if e.get('kind')=='EPISTEMIC_PROGRAM_STEP_BEARING_WITNESS' and e.get('payload',{}).get('witness_id')==wid]


def test_reassessing_same_program_step_bearing_is_duplicate_not_new_witness_event():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        t2=_execute_first_and_advance(m,trial,dc,next_state='sx',evidence_id='E-1842-X')
        first=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        second=m.assess_epistemic_program_step_outcome_bearing(trial,t2,dc)
        assert first['status']=='MODEL_SPACE_CHALLENGE' and second['status']=='MODEL_SPACE_CHALLENGE'
        wid=first['witness']['witness_id']
        assert second['witness']['witness_id']==wid
        assert second.get('duplicate') is True
        assert len(_bearing_events(m,wid))==1
        assert m.epistemic_deficits.records[trial.deficit_id].relevant_evidence_ids.count('E-1842-X')==1
        assert calls==['A']
    finally:
        td.cleanup()
