from microseed.development.epistemic import (
    EpistemicBearingKind, EpistemicContrastBinding, EpistemicContrastRegistry,
    EpistemicContrastRow, EpistemicProjectionRecord, EpistemicProjectionRegistry,
)


def test_existing_epistemic_bearing_can_detect_outside_model_outcome_without_identifying_or_generating_replacement_model():
    projections=EpistemicProjectionRegistry()
    projections.register(EpistemicProjectionRecord('P','a'*64))
    reg=EpistemicContrastRegistry(projections)
    binding=EpistemicContrastBinding('B','D','d'*64,(
        EpistemicContrastRow('P',0,(('H0','0'*64),('H1','1'*64))),
    ))
    reg.register(binding)
    kind,witness,duplicate=reg.assess(
        binding_id='B', current_hypothesis_digest_sha256='d'*64,
        evidence_id='E', evidence_sha256='e'*64, projection_id='P', projection_epoch=0,
        outcome_digest_sha256='f'*64,
    )
    assert kind is EpistemicBearingKind.MODEL_SPACE_CHALLENGE
    assert witness is not None and not duplicate
    assert witness.truth_authority == witness.answer_authority == 'NONE'
    assert witness.kind is EpistemicBearingKind.MODEL_SPACE_CHALLENGE
    # The witness says the observed outcome lies outside the bounded supplied
    # predictions; it deliberately carries no replacement-model content.
    p=witness.serializable()
    for forbidden in ('replacement_hypothesis','replacement_model','new_relation_set','model_generator'):
        assert forbidden not in p
