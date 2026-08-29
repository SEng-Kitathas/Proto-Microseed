import tempfile
from pathlib import Path

from microseed import Authority, Observation
from scratch.ms1977_raw_coordinate_projection_boundary import World, build, obs_ob
from scratch.ms1983_owned_raw_projection_routing import (
    prepare_current_raw, run_ms1983, train_projection_and_routing,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_owned_current_raw_projection_derives_bucket_and_reuses_existing_qualified_routing():
    result=run_ms1983()
    assert result['status']=='PASS'
    assert result['input_positions']==[0,1]
    assert result['generic_wrong_bucket_relation']=='R-MS1983-ODD'
    assert result['owned_relation']=='R-MS1983-EVEN'
    assert result['bucket_derivation_basis']=='CURRENT_BOUNDED_RAW_OBSERVATION_PLUS_EXACT_ADMITTED_PROJECTION'
    assert result['new_routing_mechanism_added']=='NO'
    assert result['bucket_selection_authority']==result['semantic_projection_authority']==result['truth_authority']==result['execution_authority']==result['language_authority']=='NONE'


def _fixture(prefix):
    td=tempfile.TemporaryDirectory(prefix=prefix); world=World(); m=build(Path(td.name),world)
    c,bid,even,odd=train_projection_and_routing(m,world)
    return td,world,m,c,bid,even,odd


def test_owned_raw_projection_routing_requires_exact_single_current_raw_receipt():
    td,world,m,c,bid,even,odd=_fixture('ms1983-receipt-hostile-')
    try:
        pair=('0','0'); world.reset(pair); m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation('C-NONE','EXTERNAL','opaque-control','ALIAS',authority=Authority.OBSERVATION_ONLY),evidence_id='E-NONE-STATE')
        missing=m.resolve_current_raw_projection_conditioned_relation(bid,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert missing['status']=='DEFER_UNKNOWN'
        assert missing['reason']=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CURRENT_STATE_REQUIRED'
        assert missing['matching_receipt_count']==0

        # Same current state, two separately durable raw receipts: no implicit tie-break.
        a=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-DUP-RAW-A',capture_id='DUP-A',max_coordinates=4)
        b=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-DUP-RAW-B',capture_id='DUP-B',max_coordinates=4)
        assert a['status']==b['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        duplicate=m.resolve_current_raw_projection_conditioned_relation(bid,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert duplicate['status']=='DEFER_UNKNOWN'
        assert duplicate['reason']=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CURRENT_STATE_REQUIRED'
        assert duplicate['matching_receipt_count']==2
    finally:
        _close(m); world.close(); td.cleanup()


def test_owned_raw_projection_routing_does_not_treat_projection_record_as_recoverable_content():
    td,world,m,c,bid,even,odd=_fixture('ms1983-content-hostile-')
    try:
        prepare_current_raw(m,world,('0','0'),77)
        m.epistemic_projection_candidates.clear()
        out=m.resolve_current_raw_projection_conditioned_relation(bid,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='CURRENT_RAW_PROJECTION_CONTENT_NOT_RECOVERABLE'
        assert out['execution_authority']=='NONE'
    finally:
        _close(m); world.close(); td.cleanup()


def test_owned_raw_projection_routing_blocks_when_existing_binding_premises_drift():
    td,world,m,c,bid,even,odd=_fixture('ms1983-drift-hostile-')
    try:
        prepare_current_raw(m,world,('0','0'),88)
        m.frames.change('F',reason='MS1983-FRAME-DRIFT')
        out=m.resolve_current_raw_projection_conditioned_relation(bid,action_id='B',task_id='MS1983',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='ROUTING_BINDING_NOT_CURRENT'
        assert out['execution_authority']=='NONE'
    finally:
        _close(m); world.close(); td.cleanup()
