from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture
from tests.embodiment.test_ms1837_pass10_full_generated_three_tick_realization import _add_feas_c, _run_one


def test_completed_program_evidence_is_derived_bundle_with_step_outcome_ancestry_not_second_physical_observation():
    td,m,calls,trial,dc=_generated_fixture()
    try:
        _add_feas_c(m)
        t1,_=_run_one(m,trial,dc,'A','s1','E-1838-A')
        t2,_=_run_one(m,t1,dc,'B','s2','E-1838-B')
        t3,b3=_run_one(m,t2,dc,'C','u','E-1838-C')
        assert b3['status']=='DISCRIMINATES_LIVE_SET'
        result=m.record_completed_epistemic_program_evidence(t3,evidence_id='E-1838-COMPLETE')
        assert result['status']=='PROGRAM_EVIDENCE_RECORDED', result
        ev=m.evidence.get('E-1838-COMPLETE')
        assert ev is not None
        assert ev['source']=='EPISTEMIC_PROGRAM_TRIAL'
        payload=ev['payload']
        assert [r['outcome_evidence_id'] for r in payload['step_records']]==['E-1838-A','E-1838-B','E-1838-C']
        assert payload['truth_authority']=='NONE'
        assert payload['execution_authority_gain']=='NONE'
        # The derived bundle has its own content identity but visibly depends on the physical outcomes.
        assert ev['sha256'] not in {m.evidence.get(x)['sha256'] for x in ('E-1838-A','E-1838-B','E-1838-C')}
        assert set(m.epistemic_deficits.records[trial.deficit_id].relevant_evidence_ids)>={'E-1838-C','E-1838-COMPLETE'}
    finally:
        td.cleanup()
