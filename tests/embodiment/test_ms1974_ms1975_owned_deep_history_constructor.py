import pytest

from scratch.ms1974_deeper_history_constructor_boundary import run_ms1974
from scratch.ms1975_owned_history_constructor_bridge import run_ms1975
from scratch.ms1974_deeper_history_constructor_boundary import DeepAliasWorld, build, prepare_proposals, run_chain
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_supplied_history_localizes_missing_owned_history_bridge_not_constructor():
    result=run_ms1974()
    assert result['status']=='BOUNDARY_CONFIRMED'
    assert result['one_step_target_count']==0
    assert result['lag_depth_used']==2
    assert result['atoms']==['L2:P0']
    assert result['validation_accuracy']==1.0
    assert result['new_constructor_mechanism_required']=='NO'
    assert result['missing_owner']=='ENTITY_OWNED_AUTHENTICATED_HISTORY_TO_CONSTRUCTOR_SAMPLE_DERIVATION'
    assert result['history_slice_authority']=='HARNESS_SUPPLIED_ASSISTANCE'


def test_owned_authenticated_history_bridge_feeds_existing_lag2_constructor_without_semantic_authority():
    result=run_ms1975()
    assert result['status']=='PASS'
    assert result['owned_target_sample_count']==36
    assert result['history_basis']=='AUTHENTICATED_CONTROL_STATE_PREDECESSOR_CHAIN'
    assert result['atoms']==['L2:P0']
    assert result['lag_depth_used']==2
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['new_constructor_mechanism_added']=='NO'
    assert result['sample_persistence']=='NONE'
    assert result['qualification_authority']=='EXTERNAL_ONLY'
    assert result['semantic_projection_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_owned_history_bridge_has_bounded_lag_and_requires_current_temporal_ancestry():
    import tempfile
    from pathlib import Path
    td=tempfile.TemporaryDirectory(prefix='ms1975-hostile-');world=DeepAliasWorld();m=build(Path(td.name),world)
    try:
        proposals=prepare_proposals(m)
        run_chain(m,world,proposals,'s0',0)
        with pytest.raises(ValueError,match='BOUNDED_OWNED_HISTORY_LAG_REQUIRED'):
            m.derive_admitted_constructor_projection_samples(max_lag=5)
        m.episodes.change('EP',reason='MS1975-EPISODE-DRIFT')
        surface=m.derive_admitted_constructor_projection_samples(max_lag=2)
        # Current ordinary transitions may still exist, but temporal constructor rows
        # must not be emitted without exactly one current episode ancestry.
        assert all(len(row.raw_history)==1 for row in surface['samples'])
        assert any(reason=='EXACT_SINGLE_CURRENT_EPISODE_FOR_HISTORY_REQUIRED' for _,reason in surface['sample_rejections'])
    finally:
        _close(m);world.close();td.cleanup()
