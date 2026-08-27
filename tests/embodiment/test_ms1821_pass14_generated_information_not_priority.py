from microseed import Authority, Observation
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext, derive_current_grounded_feasibility_surface,
    derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_program_discrimination_commitment,
)
from microseed.development.epistemic_program import begin_generated_epistemic_program_trial
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob
from tests.embodiment.test_ms1820_pass13_owned_three_locus_surface_generates_program import fixture,_add_effect_c,_add_recurrent_chain


def test_generated_three_step_information_does_not_manufacture_normative_priority():
    td,m,calls,_,_,_=fixture()
    try:
        _add_effect_c(m,calls)
        for prefix,effect,end in (('P1',1.0,'u'),('P2',1.0,'u'),('N1',-1.0,'v'),('N2',-1.0,'v')):
            _add_recurrent_chain(m,prefix,effect,end)
        m.observe_opaque_control_state(Observation('CS-1821','EXT','opaque-control','s0',authority=Authority.OBSERVATION_ONLY),evidence_id='E-CS-1821')
        surface=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
        generated=m.derive_current_generated_epistemic_program_candidates_from_three_locus_history(obligation=act_ob())
        candidate=[c for c in generated['candidates'] if c.steps==('A','B','C')][0]
        deficit=m.epistemic_deficits.records['D']
        trial=begin_generated_epistemic_program_trial(
            candidate,deficit_id='D',discrimination_signature_sha256=deficit.missing_discriminator_signature_sha256,
            capabilities=m.capabilities,obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),
            start_state_id='s0',start_state_evidence_id=m.action_closure.current_state.evidence_id,
        )
        options,_=derive_current_grounded_feasibility_surface(capabilities=m.capabilities,operational_scope_id='S')
        priority=derive_current_decision_bearing_commitment_from_grounded_surface(
            trial=trial,deficit=deficit,decision_context=dc,feasibility_options=options,
            capabilities=m.capabilities,values=m.values,current_frame_epochs=dict(m.frames.epochs),
            current_episode_epochs=dict(m.episodes.epochs),current_topology_epochs=dict(m.topologies.epochs),
            current_coordination_epochs=dict(m.coordinations.epochs),
        )
        assert priority.commitment.value=='NO'
        assert priority.reason=='DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION'
        information=derive_current_program_discrimination_commitment(trial=trial,decision_context=dc,decision_bearing_commitment=priority)
        assert information.commitment.value=='UNKNOWN'
        assert information.reason=='CURRENT_DECISION_BEARING_PREMISE_REQUIRED'
        assert calls==[]
    finally:
        td.cleanup()
