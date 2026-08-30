from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from microseed import Microseed
from scratch.ms1990_source_family_scaling_boundary import run_ms1990
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_ms1990_explicit_source_count_ceiling_scales_beyond_16_without_source_selection_policy():
    result=run_ms1990()
    assert result['status']=='PASS'
    assert result['invalid_zero_rejection']=='BOUNDED_SOURCE_PROJECTION_COUNT_REQUIRED'
    assert result['caller_source_ids_supplied']=='NO'
    assert result['lexicographic_truncation_used']=='NO'
    assert result['new_source_selection_mechanism_added']=='NO'
    assert [case['source_count'] for case in result['cases']]==[17,32]
    assert [case['existing_learner_exact_positions'] for case in result['cases']]==[[0,16],[0,31]]
    for case in result['cases']:
        assert case['lower_bound_status']=='DEFER_UNKNOWN'
        assert case['lower_bound_reason']=='COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND'
        assert case['exact_bound_status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES'
        assert case['vector_width']==case['source_count']
        assert case['single_source_candidates']==0
        assert case['validation_accuracy']==1.0
        assert case['lift']==.5
    assert result['semantic_feature_selection_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_ms1990_nonpositive_source_count_ceiling_still_rejected():
    td=tempfile.TemporaryDirectory(prefix='ms1990-nonpositive-bound-')
    m=Microseed(Path(td.name))
    try:
        for value in (0,-1):
            with pytest.raises(ValueError,match='BOUNDED_SOURCE_PROJECTION_COUNT_REQUIRED'):
                m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=value)
    finally:
        _close(m); td.cleanup()
