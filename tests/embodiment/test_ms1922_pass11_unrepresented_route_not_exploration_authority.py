from __future__ import annotations

from dataclasses import replace

from microseed import Authority, Observation
from microseed.development.epistemic_action import (
    derive_current_decision_bearing_commitment,
    derive_current_program_discrimination_commitment,
    derive_epistemic_program_step_local_precheck,
    derive_grounded_feasibility_option,
)
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1828_pass01_generated_program_tick1_reauthorization import _generated_fixture


def _at_unrepresented_r():
    td,m,calls,trial,dc=_generated_fixture()
    m.observe_opaque_control_state(
        Observation('MS1922-R','EXT','opaque-control','r',authority=Authority.OBSERVATION_ONLY),
        evidence_id='E-MS1922-R',
    )
    trial_r=replace(trial,start_state_id='r',start_state_evidence_id='E-MS1922-R')
    return td,m,calls,trial_r,dc


def _close(m,td):
    m.biography.close();m.evidence.conn.close();m.store.conn.close();td.cleanup()


def test_ranger1_current_feasible_effect_route_can_pass_local_precheck_without_execution_authority():
    td,m,calls,trial,dc=_at_unrepresented_r()
    try:
        option,basis=derive_grounded_feasibility_option(
            target_capability_id='A',feasibility_capability_id='FEAS-A',
            feasibility_obligation=fob('A'),capabilities=m.capabilities,
        )
        assert option.feasibility==FeasibilityState.FEASIBLE
        assert basis['status']=='CURRENT_BOUNDED_FEASIBILITY'
        local=derive_epistemic_program_step_local_precheck(
            trial=trial,deficit=m.epistemic_deficits.records['D'],feasibility=option,
            capabilities=m.capabilities,obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),current_state=m.action_closure.current_state,
        )
        assert local.commitment.value=='YES',local.serializable()
        assert local.reason=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_ALL_LICENSED'
        assert local.qualifier('decision_premises')=='LOCAL_PRECHECK_ONLY__NOT_EXECUTABLE'
        assert local.qualifier('execution_authority')=='NONE'
        assert calls==[]
    finally:_close(m,td)


def test_ranger2_unrepresented_relation_ancestry_withholds_priority_information_and_nomination():
    td,m,calls,trial,dc=_at_unrepresented_r()
    try:
        priority=derive_current_decision_bearing_commitment(
            trial=trial,deficit=m.epistemic_deficits.records['D'],decision_context=dc,
            capabilities=m.capabilities,values=m.values,
            current_frame_epochs=dict(m.frames.epochs),current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs),current_coordination_epochs=dict(m.coordinations.epochs),
        )
        information=derive_current_program_discrimination_commitment(
            trial=trial,decision_context=dc,decision_bearing_commitment=priority,
        )
        assert priority.commitment.value=='UNKNOWN'
        assert priority.reason=='PROGRAM_RELATION_ANCESTRY_INCOMPLETE'
        assert information.commitment.value=='UNKNOWN'
        assert information.reason=='PROGRAM_RELATION_ANCESTRY_INCOMPLETE'
        nomination=m.nominate_endogenous_epistemic_program_step_intent(trial,dc,'FEAS-A',fob('A'),act_ob())
        assert nomination['status']=='ABSTAIN'
        assert nomination['reason']=='PROGRAM_RELATION_ANCESTRY_INCOMPLETE'
        assert calls==[]
    finally:_close(m,td)


def test_ranger3_generator_does_not_invent_transition_from_unrepresented_current_context():
    td,m,calls,trial,dc=_at_unrepresented_r()
    try:
        result=m.discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(deficit_id='D',obligation=act_ob())
        assert result['status']=='ABSTAIN'
        assert result['reason']=='CURRENT_GENERATOR_TRANSITION_UNREPRESENTED'
        assert calls==[]
    finally:_close(m,td)


def test_ranger4_regulatory_license_unavailable_here_cannot_be_relabelled_as_exploration():
    td,m,calls,trial,dc=_at_unrepresented_r()
    try:
        result=m.derive_multi_value_action_licenses(('V',))
        assert result['status']=='UNKNOWN_ACTION_SELECTION'
        assert result['licensed_action_ids']==[]
        assert result['overall_commitment']['reason']=='NO_FULLY_LICENSED_ACTION'
        nomination=m.nominate_multi_value_action_intent(('V',),act_ob())
        assert nomination['status']=='ABSTAIN'
        assert nomination['reason']=='NO_FULLY_LICENSED_ACTION'
        assert calls==[]
    finally:_close(m,td)
