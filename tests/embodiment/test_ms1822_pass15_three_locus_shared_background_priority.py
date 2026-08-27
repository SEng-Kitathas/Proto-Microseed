from microseed import Authority, CapabilityContract, Observation, QualificationState, QueryObligation
from microseed.development.action_learning import QualifiedActionOutcomePredictiveRelation
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, derive_current_grounded_feasibility_surface,
    derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_program_discrimination_commitment,
)
from microseed.development.epistemic_program import begin_generated_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture,act_ob
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import _add_effect_c,_add_recurrent_chain


def _fob_d():
    return QueryObligation('QF-D','feas:D',required_authority=Authority.DERIVED_READ_ONLY,operational_scope_id='S')


def _add_shared_fallback(m,calls):
    m.register_capability(CapabilityContract(
        'D','opaque',{}, {},(),(),Authority.EFFECT,('T',),'CURRENT',{},query_obligation_id='Q',
        qualification=QualificationState.SHADOW_QUALIFIED,handler=lambda **_:calls.append('D') or {'receipt':'D'},operational_scope_id='S'))
    m.register_capability(CapabilityContract(
        'FEAS-D','feas',{'target_capability_id':'D'},{},(),(),Authority.DERIVED_READ_ONLY,('T',),'CURRENT',{},dependencies=('D',),
        query_obligation_id='QF-D',qualification=QualificationState.SHADOW_QUALIFIED,
        handler=lambda **_:{'feasibility':'FEASIBLE','reason':'FRESH_WORLD'},operational_scope_id='S'))
    m.action_outcome_learning.add_relation(QualifiedActionOutcomePredictiveRelation(
        relation_id='R-D0',candidate_id='C-R-D0',candidate_sha256='d'*64,start_state_id='s0',capability_id='D',
        next_state_id='sd',value_effect=0.0,support=12,consistency=1.0,source_evidence_ids=('E-R-D0',),
        qualification_evidence_ids=('Q-R-D0',),holdout_support=12,holdout_accuracy=1.0,capability_epoch=0,
        frame_epochs=(('F',0),),episode_schema_epochs=(('EP',0),),value_epoch=('V',0),
    ))


def test_existing_shared_background_owner_makes_three_locus_uncertainty_decision_bearing_without_model_authority_gain():
    td,m,calls,_,_,_=fixture()
    try:
        _add_effect_c(m,calls); _add_shared_fallback(m,calls)
        for prefix,effect,end in (('P1',1.0,'u'),('P2',1.0,'u'),('N1',-1.0,'v'),('N2',-1.0,'v')):
            _add_recurrent_chain(m,prefix,effect,end)
        m.observe_opaque_control_state(Observation('CS-1822','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1822')
        surface=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        assert surface['status']=='THREE_LOCUS_CHAIN_MODEL_SURFACE', surface
        assert surface['background_relation_count']==1
        assert all(len(model)==4 for model in surface['relation_sets'])
        assert all(any(r.capability_id=='D' and r.state_id=='s0' for r in model) for model in surface['relation_sets'])
        dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
        generated=m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=act_ob())
        candidate=[c for c in generated['candidates'] if c.steps==('A','B','C')][0]
        deficit=m.epistemic_deficits.records['D']
        trial=begin_generated_epistemic_program_trial(candidate,deficit_id='D',discrimination_signature_sha256=deficit.missing_discriminator_signature_sha256,
            capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),start_state_id='s0',start_state_evidence_id=m.action_closure.current_state.evidence_id)
        options,_=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        priority=derive_current_decision_bearing_commitment_from_grounded_surface(
            trial=trial,deficit=deficit,decision_context=dc,feasibility_options=options,capabilities=m.capabilities,values=m.values,
            current_frame_epochs=dict(m.frames.epochs),current_episode_epochs=dict(m.episodes.epochs),current_topology_epochs=dict(m.topologies.epochs),current_coordination_epochs=dict(m.coordinations.epochs))
        assert priority.commitment.value=='YES', priority.serializable()
        information=derive_current_program_discrimination_commitment(trial=trial,decision_context=dc,decision_bearing_commitment=priority)
        assert information.commitment.value=='YES', information.serializable()
        assert calls==[]
    finally:
        td.cleanup()
