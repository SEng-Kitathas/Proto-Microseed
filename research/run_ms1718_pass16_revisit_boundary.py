from pathlib import Path
from tests.embodiment.test_ms1713_tick_reauthorization import two_tick_fixture

td,m,calls,world,trial,dc=two_tick_fixture()
try:
    checks={
        'revisit_surface_exists': hasattr(m,'epistemic_revisit_required_ids'),
        'no_question_revisit_scheduler': not hasattr(m,'schedule_question_revisits'),
        'no_epistemic_answer_method': not hasattr(m,'answer_epistemic_deficit'),
        'no_experiment_scheduler': not hasattr(m,'schedule_epistemic_program'),
        'no_macro_executor': not hasattr(m,'execute_epistemic_macro'),
    }
    assert all(checks.values()),checks
    out={'pass':'MS1718','disposition':'SURVIVED_BOUNDARY__REVISIT_IS_ELIGIBILITY_NOT_ANSWER_AUTHORITY','checks':checks}
    Path('research/MS1718_PASS16_REVISIT_BOUNDARY.json').write_text(__import__('json').dumps(out,indent=2,sort_keys=True))
    print(out)
finally: td.cleanup()
