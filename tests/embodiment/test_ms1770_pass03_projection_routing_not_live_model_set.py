import inspect

from microseed.development.action_learning import QualifiedProjectionConditionedRelationBinding
from microseed.runtime.entity import Microseed


def test_projection_conditioned_binding_can_map_multiple_qualified_buckets_but_does_not_own_which_are_live_alternatives_now():
    b = QualifiedProjectionConditionedRelationBinding(
        binding_id='B', candidate_id='C', candidate_sha256='a'*64,
        projection_id='P', projection_epoch=0, projection_signature_sha256='b'*64,
        task_id='T', action_ids=('A','B'), channel_ids=('CH',), horizon=2,
        default_action_relations=(('A','RA0'),('B','RB0')),
        bucket_action_overrides=(('x','A','RAX'),('y','A','RAY')),
        source_evidence_ids=('E-SRC',), qualification_evidence_ids=('E-Q',),
        holdout_support=24, holdout_accuracy=1.0, holdout_coverage=1.0,
        qualified_bucket_ids=('x','y'),
    )
    assert b.relation_id_for('x','A') == 'RAX'
    assert b.relation_id_for('y','A') == 'RAY'
    assert b.qualified_bucket_ids == ('x','y')
    assert b.model_switch_authority == b.truth_authority == 'NONE'

    # Runtime resolution still requires the bucket to be supplied explicitly.
    sig = inspect.signature(Microseed.resolve_projection_conditioned_action_outcome_relation)
    assert 'projection_bucket_id' in sig.parameters
    assert sig.parameters['projection_bucket_id'].default is inspect._empty

    # Qualification of a bucket-specific routing rule is not a current-possibility
    # assertion over all qualified buckets; the binding has no live-alternative field.
    payload = b.serializable()
    for forbidden in ('live_bucket_ids','possible_bucket_ids','current_alternative_ids','active_model_set'):
        assert forbidden not in payload
