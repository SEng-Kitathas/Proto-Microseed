from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.predictive_adaptation import (
    ActionOutcomePredictiveCurrentnessWitness, ActionOutcomeReplacementLink, PredictiveCurrentnessConfig,
)
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture


def learned_relation() -> QualifiedActionOutcomePredictiveRelation:
    return QualifiedActionOutcomePredictiveRelation(
        relation_id='R-OLD', candidate_id='C-OLD', candidate_sha256='a'*64,
        start_state_id='s0', capability_id='A', next_state_id='s1', value_effect=1.0,
        support=16, consistency=1.0, source_evidence_ids=('E-SRC',),
        qualification_evidence_ids=('E-Q',), holdout_support=12, holdout_accuracy=1.0,
        capability_epoch=0, frame_epochs=(('F',0),), episode_schema_epochs=(('EP',0),),
        value_epoch=('V',0),
    )


def test_drift_lineage_stales_old_empirical_relation_and_replacement_link_has_no_model_switch_authority():
    td,m,_,_,_,_=fixture()
    try:
        r=learned_relation(); m.action_outcome_learning.add_relation(r)
        assert m._action_outcome_relation_current(r)
        w=ActionOutcomePredictiveCurrentnessWitness(
            witness_id='W', relation_id=r.relation_id, relation_candidate_sha256=r.candidate_sha256,
            status='DRIFT_WITNESS', window_accuracies=(0.0,0.0), assessed_evidence_ids=('E1','E2'),
            drift_evidence_ids=('E1','E2'), drift_window=1,
            config=PredictiveCurrentnessConfig(window_size=2,min_accuracy=.75,consecutive_failure_windows=1),
        )
        m.action_outcome_learning.currentness_witnesses[r.relation_id]=w
        assert not m._action_outcome_relation_current(r)
        link=ActionOutcomeReplacementLink('C-NEW',r.relation_id,w.witness_id,w.drift_evidence_ids)
        assert link.model_switch_authority == link.qualification_authority == 'NONE'
        assert link.authority == 'MODEL_OUTPUT_ONLY'
    finally: td.cleanup()
