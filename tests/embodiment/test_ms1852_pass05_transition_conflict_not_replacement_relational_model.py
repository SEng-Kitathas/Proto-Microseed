from dataclasses import fields

from microseed.development.relational_algebra import OpaqueTransitionConflictCandidate
from microseed.development.rehearsal import RehearsalTransitionRelation


def test_opaque_transition_conflict_lacks_value_and_ancestry_needed_for_decision_model_relation():
    conflict_fields={f.name for f in fields(OpaqueTransitionConflictCandidate)}
    relation_fields={f.name for f in fields(RehearsalTransitionRelation)}
    # The existing conflict owner says only that one opaque slot has recurrent
    # incompatible endpoints.  It deliberately does not own the richer ancestry
    # required by a decision-bearing predictive relation.
    assert 'outcome_supports' in conflict_fields and 'frame_epoch' in conflict_fields
    for missing in (
        'value_effect','value_epoch','episode_schema_epoch','capability_epoch',
        'evidence_premise_epochs','evidence_premise_signatures',
    ):
        assert missing not in conflict_fields
        assert missing in relation_fields
    assert 'state_alias_authority' in conflict_fields
    assert 'generator_authority' in conflict_fields
    assert not hasattr(OpaqueTransitionConflictCandidate,'as_rehearsal_relation')
    assert not hasattr(OpaqueTransitionConflictCandidate,'as_epistemic_alternative_relation')
