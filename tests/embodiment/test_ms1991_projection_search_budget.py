from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from microseed import Authority, Microseed, OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample, QualificationState
from scratch.ms1991_projection_search_budget_boundary import run_ms1991
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _frame(m:Microseed) -> None:
    m.register_operational_frame(OperationalFrameContract(
        'F','MS1991 test frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1991',),'CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
    ))


def test_ms1991_budget_preflight_distinguishes_incomplete_search_from_exhaustive_absence():
    result=run_ms1991()
    assert result['status']=='PASS'
    assert result['required_subset_evaluations']==528
    assert result['insufficient_budget']==527
    assert result['insufficient_status']=='DEFER_UNKNOWN'
    assert result['insufficient_reason']=='PROJECTION_SEARCH_SUBSET_EVALUATION_BUDGET_INSUFFICIENT'
    assert result['insufficient_subset_evaluations_performed']==0
    assert result['sufficient_status']=='EXHAUSTIVE_PROJECTION_SEARCH_COMPLETED'
    assert result['late_exact_positions']==[30,31]
    assert result['candidate_identity_preserved'] is True
    assert result['validation_accuracy']==1.0
    assert result['lift']==.5
    assert result['cost_examples']=={'N32_K2':528,'N64_K3':43744,'N128_K4':11017632}
    assert result['partial_search_used']=='NO'
    assert result['source_ids_nominated']=='NO'
    assert result['semantic_attention_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_ms1991_large_search_space_defers_before_any_subset_fit():
    td=tempfile.TemporaryDirectory(prefix='ms1991-large-preflight-'); m=Microseed(Path(td.name))
    try:
        _frame(m)
        raw=('0',)*128
        train=(ProjectionSample('T',raw,'H','E0','S','F',0),)
        validation=(ProjectionSample('V',raw,'H','E0','S','F',0),)
        cfg=ProjectionDiscoveryConfig(max_subset=4,min_train_support=1,min_key_action_support=1,max_candidates=4)
        before=len(m.epistemic_projection_candidates)
        out=m.discover_epistemic_projection_candidates_with_budget(
            train,validation,cfg,max_subset_evaluations=1_000_000,
        )
        assert out['status']=='DEFER_UNKNOWN'
        assert out['required_subset_evaluations']==11_017_632
        assert out['subset_evaluations_performed']==0
        assert out['search_complete'] is False
        assert len(m.epistemic_projection_candidates)==before
    finally:
        _close(m);td.cleanup()


def test_ms1991_nonpositive_search_budget_is_rejected():
    td=tempfile.TemporaryDirectory(prefix='ms1991-invalid-budget-'); m=Microseed(Path(td.name))
    try:
        _frame(m)
        row=ProjectionSample('R',('0',),'H','E0','S','F',0)
        for budget in (0,-1):
            with pytest.raises(ValueError,match='BOUNDED_PROJECTION_SEARCH_EVALUATION_BUDGET_REQUIRED'):
                m.discover_epistemic_projection_candidates_with_budget(
                    (row,),(row,),ProjectionDiscoveryConfig(min_train_support=1,min_key_action_support=1),
                    max_subset_evaluations=budget,
                )
    finally:
        _close(m);td.cleanup()
