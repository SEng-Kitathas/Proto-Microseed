from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from microseed import Microseed
from scratch.ms1987_depth3_recursive_bucket_composition import run_ms1987
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_ms1987_depth3_recursive_bucket_composition_and_currentness_hostiles():
    result=run_ms1987()
    assert result['status']=='PASS'
    assert result['flat_source_projection_ids']==['P-MS1987-A','P-MS1987-B','P-MS1987-D']
    assert result['flat_C_rejection']=='SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND'
    assert result['flat_depth3_candidates']==0
    assert result['recursive_source_projection_ids']==['P-MS1987-A','P-MS1987-B','P-MS1987-C','P-MS1987-D']
    assert result['recursive_depth']==1
    assert result['single_source_candidates']==0
    assert result['depth3_positions']==[2,3]
    assert result['validation_accuracy']==1.0
    assert result['lift']>=.49
    assert result['external_holdout_count']==64
    assert [x[0] for x in result['C_source_projection_epochs']]==['P-MS1987-A','P-MS1987-B','P-MS1987-D']
    assert [x[0] for x in result['E_source_projection_epochs']]==['P-MS1987-A','P-MS1987-B','P-MS1987-C','P-MS1987-D']
    assert result['missing_C_content_refused'] is True
    assert result['C_change_staled_E'] is True
    assert result['A_change_staled_C'] is True
    assert result['new_projection_search_mechanism_added']=='NO'
    assert result['new_representation_manager_added']=='NO'
    assert result['sample_persistence']=='NONE'
    assert result['semantic_recursion_authority']==result['semantic_symbol_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_recursive_projection_evaluation_depth_is_bounded():
    td=tempfile.TemporaryDirectory(prefix='ms1987-depth-bound-')
    m=Microseed(Path(td.name))
    try:
        with pytest.raises(ValueError,match='BOUNDED_PROJECTION_EVALUATION_DEPTH_REQUIRED'):
            m.derive_admitted_projection_samples_from_owned_projection_buckets(max_projection_depth=-1)
        with pytest.raises(ValueError,match='BOUNDED_PROJECTION_EVALUATION_DEPTH_REQUIRED'):
            m.derive_admitted_projection_samples_from_owned_projection_buckets(max_projection_depth=9)
    finally:
        _close(m);td.cleanup()
