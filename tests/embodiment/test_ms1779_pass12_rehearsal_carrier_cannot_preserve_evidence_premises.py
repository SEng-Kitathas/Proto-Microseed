from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.rehearsal import RehearsalTransitionRelation


def test_repaired_epistemic_carrier_and_ms1941_durable_rehearsal_both_preserve_premises():
    assert 'evidence_premise_epochs' in RehearsalTransitionRelation.__dataclass_fields__
    assert 'evidence_premise_signatures' in RehearsalTransitionRelation.__dataclass_fields__

    r=QualifiedActionOutcomePredictiveRelation(
        relation_id='R',candidate_id='C',candidate_sha256='a'*64,
        start_state_id='s0',capability_id='A',next_state_id='s1',value_effect=1.0,
        support=12,consistency=1.0,source_evidence_ids=('E',),qualification_evidence_ids=('Q',),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,
        frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
        evidence_premise_epochs=(('OBS-BASIS',0),),evidence_premise_signatures=(('OBS-BASIS','b'*64),),
    )
    # Historical MS1779 correctly refused ordinary durable conversion because
    # the proposal carrier could not preserve premise ancestry. MS1941 later
    # completed that carrier/currentness path; the scar survives as history,
    # while both bridges must now preserve the same exact ancestry.
    ordinary=r.as_rehearsal_relation()
    assert ordinary is not None
    assert ordinary.evidence_premise_epochs==r.evidence_premise_epochs
    assert ordinary.evidence_premise_signatures==r.evidence_premise_signatures
    assert ordinary.value_epoch==('V',0)
    rr=r.as_epistemic_alternative_relation()
    assert rr is not None
    assert rr.evidence_premise_epochs==r.evidence_premise_epochs
    assert rr.evidence_premise_signatures==r.evidence_premise_signatures
    assert rr.value_epoch==('V',0)
