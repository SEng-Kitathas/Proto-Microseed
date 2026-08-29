import tempfile
from pathlib import Path

import pytest

from microseed import Authority, Observation
from scratch.ms1981_temporal_raw_constructor_boundary import (
    World, act_ob, basis_ob, build, obs_ob, proposals, run_ms1981,
)
from scratch.ms1982_owned_temporal_raw_constructor import run_ms1982
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_supplied_temporal_raw_history_localizes_missing_owned_bridge_not_constructor():
    result=run_ms1981()
    assert result['status']=='BOUNDARY_CONFIRMED'
    assert result['current_raw_only_candidates']==0
    assert set(result['atoms'])=={'L0:P0','L1:P0'}
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['missing_owner']=='ENTITY_OWNED_RAW_OBSERVATION_PREDECESSOR_CHAIN_TO_CONSTRUCTOR_SAMPLE'
    assert result['new_constructor_mechanism_required']=='NO'
    assert result['raw_history_authority']=='HARNESS_SUPPLIED_ASSISTANCE'


def test_owned_temporal_raw_receipts_feed_existing_constructor_without_semantic_authority():
    result=run_ms1982()
    assert result['status']=='PASS'
    assert result['target_sample_count']==48
    assert result['history_basis']=='AUTHENTICATED_RAW_OBSERVATION_PREDECESSOR_CHAIN'
    assert result['current_only_candidates']==0
    assert set(result['atoms'])=={'L0:P0','L1:P0'}
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert result['new_constructor_mechanism_added']=='NO'
    assert result['sample_persistence']=='NONE'
    assert result['qualification_authority']=='EXTERNAL_ONLY'
    assert result['semantic_coordinate_authority']==result['semantic_projection_authority']==result['truth_authority']==result['language_authority']=='NONE'


def _step(m,proposal,tag):
    intent=m.nominate_bounded_action_intent(proposal.proposal_id,act_ob()); assert intent['status']=='ACTION_INTENT_NOMINATED'
    ex=m.execute_bounded_action(intent['intent']['intent_id'],act_ob()); assert ex['status']=='ACTION_EXECUTED'
    out=m.record_bounded_action_outcome_via_observation_basis(
        ex['execution']['execution_id'],observation_capability_id='OBS',observation_obligation=obs_ob(),
        basis_capability_id='BASIS',basis_obligation=basis_ob(),evidence_id=f'E-H-{tag}',capture_id=f'C-H-{tag}'
    )
    assert out['status']=='ACTION_OUTCOME_OBSERVED'
    return out


def test_temporal_raw_bridge_is_lag_bounded_and_does_not_arbitrate_duplicate_predecessor_receipts():
    td=tempfile.TemporaryDirectory(prefix='ms1982-hostile-'); w=World(); m=build(Path(td.name),w)
    try:
        ps=proposals(m); bits=('0','1'); w.reset(bits); m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation('C-H0','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-H-STATE0')
        a=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-H-RAW0-A',capture_id='H0A',max_coordinates=1)
        b=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-H-RAW0-B',capture_id='H0B',max_coordinates=1)
        assert a['status']==b['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        _step(m,ps['PREP'],'PREP')
        current=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-H-RAW1',capture_id='H1',max_coordinates=1)
        assert current['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        _step(m,ps[bits],'B')

        with pytest.raises(ValueError,match='BOUNDED_OWNED_RAW_HISTORY_LAG_REQUIRED'):
            m.derive_admitted_raw_constructor_projection_samples(max_lag=5)

        surface=m.derive_admitted_raw_constructor_projection_samples(max_lag=1)
        b_rows=[row for row in surface['samples'] if row.action_token=='B']
        assert b_rows and all(len(row.raw_history)==1 for row in b_rows)
    finally:
        _close(m); w.close(); td.cleanup()


def test_temporal_raw_bridge_requires_current_episode_for_multistep_samples():
    td=tempfile.TemporaryDirectory(prefix='ms1982-episode-hostile-'); w=World(); m=build(Path(td.name),w)
    try:
        ps=proposals(m); bits=('0','1'); w.reset(bits); m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation('C-E0','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-E-STATE0')
        first=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-E-RAW0',capture_id='E0',max_coordinates=1)
        assert first['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        _step(m,ps['PREP'],'E-PREP')
        second=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-E-RAW1',capture_id='E1',max_coordinates=1)
        assert second['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        _step(m,ps[bits],'E-B')
        before=m.derive_admitted_raw_constructor_projection_samples(max_lag=1)
        assert any(row.action_token=='B' and len(row.raw_history)==2 for row in before['samples'])

        m.episodes.change('EP',reason='MS1982-EPISODE-DRIFT')
        drift=m.derive_admitted_raw_constructor_projection_samples(max_lag=1)
        assert not any(row.action_token=='B' and len(row.raw_history)==2 for row in drift['samples'])
        assert any(reason=='EXACT_SINGLE_CURRENT_EPISODE_FOR_RAW_HISTORY_REQUIRED' for _,reason in drift['sample_rejections'])
    finally:
        _close(m); w.close(); td.cleanup()
