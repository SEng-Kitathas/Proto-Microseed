from pathlib import Path
import tempfile

from microseed import Authority, EpistemicStatus, FeasibilityState, Microseed, QualificationState, ValueVariableContract
from microseed.development.action_learning import (
    ActionOutcomeExperience, QualifiedActionOutcomePredictiveRelation,
    assemble_single_conflict_epistemic_relation_sets, discover_action_outcome_alternative_hypotheses,
)
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.recruitment import RecruitmentOption


def row(i,end,effect):
    return ActionOutcomeExperience(
        evidence_id=f'E{i}',execution_id=f'X{i}',start_state_id='s0',capability_id='A',
        actual_next_state_id=end,actual_value_effect=effect,capability_epoch=0,
        frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
        evidence_premise_epochs=(('BASIS',0),),evidence_premise_signatures=(('BASIS','b'*64),),
    )


def fixture():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms1784-')
    m=Microseed(Path(td.name))
    m.register_value_variable(ValueVariableContract('V','reg',0,10,'v'*64,Authority.REFERENCE_ONLY,('MS1784',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
    m.observe_value_state('V',-1.0)
    m.append_evidence('E-U',{'u':1},EpistemicStatus.UNKNOWN_INCOMPLETE)
    m.record_action_limited_unknown(deficit_id='D',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id='E-U',missing_discriminator_signature_sha256='d'*64,premise_anchors=(EpistemicCurrentnessAnchor('VALUE','V',0),))
    return td,m


def test_single_conflict_plus_shared_qualified_background_can_be_decision_bearing_without_promoting_conflict_modes():
    hs=discover_action_outcome_alternative_hypotheses((row(0,'x',2),row(1,'x',2),row(2,'y',-1),row(3,'y',-1)))
    q=QualifiedActionOutcomePredictiveRelation(
        relation_id='R-B',candidate_id='C-B',candidate_sha256='a'*64,start_state_id='s0',capability_id='B',
        next_state_id='b',value_effect=.5,support=12,consistency=1.0,source_evidence_ids=('EB',),qualification_evidence_ids=('QB',),
        holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),
        value_epoch=('V',0),evidence_premise_epochs=(('BASIS',0),),evidence_premise_signatures=(('BASIS','b'*64),),
    )
    bg=q.as_epistemic_alternative_relation()
    assert bg is not None
    sets=assemble_single_conflict_epistemic_relation_sets(hs,background_relations=(bg,))
    assert len(sets)==2
    assert all(sum(r.capability_id=='B' for r in s)==1 for s in sets)
    assert all(next(r for r in s if r.capability_id=='A').authority=='PROPOSAL_ONLY_RELATIONAL_ALTERNATIVE' for s in sets)
    td,m=fixture()
    try:
        out=derive_regulatory_decision_bearing_commitment(
            deficit=m.epistemic_deficits.records['D'],values=m.values,
            relation_sets=tuple({(r.state_id,r.capability_id):r for r in s} for s in sets),
            options=(RecruitmentOption('A',FeasibilityState.FEASIBLE),RecruitmentOption('B',FeasibilityState.FEASIBLE)),
            start_state_id='s0',current_capability_epochs={'A':0,'B':0,'BASIS':0},
            current_capability_signatures={'BASIS':'b'*64},current_frame_epochs={'F':0},current_episode_epochs={'EP':0},
        )
        assert out.licenses_yes(), out.reason
    finally:
        td.cleanup()


def test_background_collision_with_conflict_slot_is_rejected_instead_of_overwriting_it():
    hs=discover_action_outcome_alternative_hypotheses((row(0,'x',2),row(1,'x',2),row(2,'y',-1),row(3,'y',-1)))
    q=QualifiedActionOutcomePredictiveRelation(
        relation_id='R-A',candidate_id='C-A',candidate_sha256='a'*64,start_state_id='s0',capability_id='A',next_state_id='z',value_effect=0,
        support=12,consistency=1.0,source_evidence_ids=('E',),qualification_evidence_ids=('Q',),holdout_support=12,holdout_accuracy=1.0,
        capability_epoch=0,frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    )
    assert assemble_single_conflict_epistemic_relation_sets(hs,background_relations=(q.as_epistemic_alternative_relation(),))==()
