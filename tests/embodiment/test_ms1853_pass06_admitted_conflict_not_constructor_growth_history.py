from dataclasses import fields

from microseed.development.constructor_growth import ConstructorProjectionSample
from microseed.development.relational_algebra import OpaqueTransitionSample


def test_admitted_opaque_transition_does_not_supply_constructor_growth_history_or_target_partition():
    opaque={f.name for f in fields(OpaqueTransitionSample)}
    constructor={f.name for f in fields(ConstructorProjectionSample)}
    assert opaque=={'sample_id','origin_id','start_token','action_token','end_token','frame_id','frame_epoch'}
    # Constructor growth is a different old lab owner: it expects raw temporal
    # history and supplied target labels/partitions that an admitted transition
    # deliberately does not contain.
    for required in ('raw_history','effect_token','episode_schema_id','episode_schema_epoch'):
        assert required in constructor
        assert required not in opaque
