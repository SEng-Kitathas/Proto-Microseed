import tempfile
from pathlib import Path

from microseed import Authority, Observation
from scratch.ms1981_temporal_raw_constructor_boundary import World, build, obs_ob, step
from scratch.ms1984_owned_temporal_constructor_projection_routing import (
    BITS, install_routing, prepare_current_temporal_history, run_ms1984,
    train_constructor_projection,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def test_owned_temporal_constructor_projection_reuses_existing_qualified_routing_without_caller_bucket():
    result=run_ms1984()
    assert result['status']=='PASS'
    assert set(result['atoms'])=={'L0:P0','L1:P0'}
    assert result['generic_wrong_bucket_relation']=='R-MS1984-SAME'
    assert result['owned_relation']=='R-MS1984-DIFF'
    assert result['raw_history_lag_depth']==1
    assert len(result['raw_history_evidence_ids'])==2
    assert result['bucket_derivation_basis']=='CURRENT_AUTHENTICATED_RAW_HISTORY_PLUS_EXACT_ADMITTED_CONSTRUCTOR_PROJECTION'
    assert result['new_routing_mechanism_added']==result['new_constructor_mechanism_added']=='NO'
    assert result['bucket_selection_authority']==result['semantic_temporal_relation_authority']==result['truth_authority']==result['execution_authority']==result['language_authority']=='NONE'


def _fixture(prefix):
    td=tempfile.TemporaryDirectory(prefix=prefix); world=World(); m=build(Path(td.name),world)
    ps,c,rec=train_constructor_projection(m,world)
    bid,bucket_same,bucket_diff=install_routing(m,c,rec)
    return td,world,m,ps,c,bid,bucket_same,bucket_diff


def test_temporal_projection_routing_does_not_arbitrate_duplicate_predecessor_raw_receipts():
    td,world,m,ps,c,bid,same,diff=_fixture('ms1984-dup-hostile-')
    try:
        bits=('0','1'); world.reset(bits);m.observe_value_state('V',0.0)
        m.observe_opaque_control_state(Observation('C-DUP0','EXTERNAL','opaque-control','ALIAS0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-DUP-STATE0')
        a=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-DUP-RAW0-A',capture_id='DUP0A',max_coordinates=1)
        b=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-DUP-RAW0-B',capture_id='DUP0B',max_coordinates=1)
        assert a['status']==b['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        prep=step(m,ps['PREP'],'DUP-PREP'); assert prep['outcome']['actual_next_state_id']=='ALIAS1'
        current=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-DUP-RAW1',capture_id='DUP1',max_coordinates=1); assert current['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        out=m.resolve_current_raw_constructor_projection_conditioned_relation(bid,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_RAW_HISTORY_REQUIRED'
        assert out['lag']==1 and out['matching_receipt_count']==2
        assert out['execution_authority']=='NONE'
    finally:
        _close(m);world.close();td.cleanup()


def test_temporal_projection_routing_requires_exact_predecessor_outcome_ancestry():
    td,world,m,ps,c,bid,same,diff=_fixture('ms1984-predecessor-hostile-')
    try:
        bits=('0','1');world.reset(bits);m.observe_value_state('V',0.0)
        # Construct a current ALIAS1 witness and current raw receipt without an actual PREP outcome.
        m.observe_opaque_control_state(Observation('C-NO-PRED','EXTERNAL','opaque-control','ALIAS1',authority=Authority.OBSERVATION_ONLY),evidence_id='E-NO-PRED-STATE')
        current=m.record_bounded_raw_observation_coordinates('OBS',obs_ob(),evidence_id='E-NO-PRED-RAW',capture_id='NO-PRED',max_coordinates=1); assert current['status']=='BOUNDED_RAW_OBSERVATION_RECORDED'
        out=m.resolve_current_raw_constructor_projection_conditioned_relation(bid,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='RAW_HISTORY_PREDECESSOR_OUTCOME_NOT_UNIQUE'
        assert out['predecessor_outcome_count']==0
        assert out['execution_authority']=='NONE'
    finally:
        _close(m);world.close();td.cleanup()


def test_temporal_projection_routing_requires_recoverable_constructor_content():
    td,world,m,ps,c,bid,same,diff=_fixture('ms1984-content-hostile-')
    try:
        prepare_current_temporal_history(m,world,ps,('0','1'),7)
        m.epistemic_constructor_candidates.clear()
        out=m.resolve_current_raw_constructor_projection_conditioned_relation(bid,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='CURRENT_RAW_CONSTRUCTOR_PROJECTION_CONTENT_NOT_RECOVERABLE'
        assert out['execution_authority']=='NONE'
    finally:
        _close(m);world.close();td.cleanup()


def test_temporal_projection_routing_checks_constructor_episode_currentness_independently_of_route_relation_episode():
    td,world,m,ps,c,bid,same,diff=_fixture('ms1984-episode-hostile-')
    try:
        prepare_current_temporal_history(m,world,ps,('0','1'),8)
        # Routing relations use EP-ROUTE, but the admitted constructor projection itself
        # carries EP ancestry. Changing EP invalidates projection currentness and therefore
        # the binding before the resolver needs its deeper candidate-level episode guard.
        m.episodes.change('EP',reason='MS1984-CONSTRUCTOR-EPISODE-DRIFT')
        assert m.projection_conditioned_relation_routing_status(bid)['status']=='STALE_PROJECTION_CONDITIONED_ROUTING'
        out=m.resolve_current_raw_constructor_projection_conditioned_relation(bid,action_id='B',task_id='MS1984',channel_id='opaque-control',horizon=1)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='ROUTING_BINDING_NOT_CURRENT'
        assert out['execution_authority']=='NONE'
    finally:
        _close(m);world.close();td.cleanup()
