from __future__ import annotations

from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    EpistemicStepExecutionContext,
    derive_current_decision_bearing_commitment,
    derive_current_program_discrimination_commitment,
    derive_epistemic_program_step_commitment,
)
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from microseed.runtime.commitment import RelationalCommitment, TernaryCommitment
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import fixture, fob, act_ob
from tests.embodiment.test_ms1715_program_information_value import r as rel, context as info_context


def typed_feasible():
    return RecruitmentOption('A', FeasibilityState.FEASIBLE)


def legacy_execute(m, trial):
    n = m.nominate_epistemic_program_step_intent(trial, typed_feasible(), act_ob())
    if n['status'] != 'ACTION_INTENT_NOMINATED':
        return n, None
    out = m.execute_bounded_action(
        n['intent']['intent_id'],
        act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(trial, feasibility=typed_feasible()),
    )
    return n, out


def grounded_legacy_execute(m, trial):
    n = m.nominate_grounded_epistemic_program_step_intent(
        trial, 'FEAS-A', fob('A'), act_ob()
    )
    if n['status'] != 'ACTION_INTENT_NOMINATED':
        return n, None
    out = m.execute_bounded_action(
        n['intent']['intent_id'],
        act_ob(),
        epistemic_step_context=EpistemicStepExecutionContext(
            trial,
            feasibility_capability_id='FEAS-A',
            feasibility_obligation=fob('A'),
        ),
    )
    return n, out


def test_ranger1_public_typed_path_must_not_nominate_when_zero_pressure_removes_priority():
    td, m, calls, world, trial, dc = fixture()
    try:
        m.observe_value_state('V', 5.0)
        endogenous = m.nominate_endogenous_epistemic_program_step_intent(
            trial, dc, 'FEAS-A', fob('A'), act_ob()
        )
        assert endogenous['status'] == 'ABSTAIN'
        assert endogenous['priority']['commitment'] == 'NO'
        assert endogenous['priority']['reason'] == 'NO_CURRENT_REGULATORY_PRESSURE'

        legacy = m.nominate_epistemic_program_step_intent(trial, typed_feasible(), act_ob())
        assert legacy['status'] == 'ABSTAIN', (
            'public typed path omitted the already-earned priority premise and still nominated'
        )
        assert calls == []
    finally:
        td.cleanup()


def test_ranger2_public_grounded_path_must_not_execute_when_zero_pressure_removes_priority():
    td, m, calls, world, trial, dc = fixture()
    try:
        m.observe_value_state('V', 5.0)
        endogenous = m.nominate_endogenous_epistemic_program_step_intent(
            trial, dc, 'FEAS-A', fob('A'), act_ob()
        )
        assert endogenous['status'] == 'ABSTAIN'
        assert endogenous['priority']['reason'] == 'NO_CURRENT_REGULATORY_PRESSURE'

        nominated, executed = grounded_legacy_execute(m, trial)
        assert nominated['status'] == 'ABSTAIN', (
            'grounded public path omitted priority and created an executable intent'
        )
        assert executed is None
        assert calls == []
    finally:
        td.cleanup()


def test_ranger3_omitting_priority_cannot_turn_explicit_no_into_yes_at_lower_owner():
    td, m, calls, world, trial, dc = fixture()
    try:
        m.observe_value_state('V', 5.0)
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        priority = derive_current_decision_bearing_commitment(
            trial=trial,
            deficit=deficit,
            decision_context=dc,
            capabilities=m.capabilities,
            values=m.values,
            current_frame_epochs=dict(m.frames.epochs),
            current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs),
            current_coordination_epochs=dict(m.coordinations.epochs),
        )
        assert priority.commitment.value == 'NO'
        with_priority = derive_epistemic_program_step_commitment(
            trial=trial,
            deficit=deficit,
            feasibility=typed_feasible(),
            capabilities=m.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state,
            priority_commitment=priority,
        )
        assert not with_priority.licenses_yes()

        omitted = derive_epistemic_program_step_commitment(
            trial=trial,
            deficit=deficit,
            feasibility=typed_feasible(),
            capabilities=m.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state,
        )
        assert not omitted.licenses_yes(), (
            'omitting a known required priority premise changed NO into YES'
        )
    finally:
        td.cleanup()


def nondiscriminating_context():
    h1 = (
        rel('s0', 'A', 's1', 2),
        rel('s0', 'B', 'bx', 0),
        rel('s1', 'B', 'same', 0),
    )
    h2 = (
        rel('s0', 'A', 's1', 0),
        rel('s0', 'B', 'bx', 2),
        rel('s1', 'B', 'same', 0),
    )
    return info_context(h1, h2)


def test_ranger4_public_path_must_not_nominate_when_program_has_no_information_value():
    td, m, calls, world, trial, _ = fixture()
    try:
        dc = nondiscriminating_context()
        endogenous = m.nominate_endogenous_epistemic_program_step_intent(
            trial, dc, 'FEAS-A', fob('A'), act_ob()
        )
        assert endogenous['status'] == 'ABSTAIN'
        assert endogenous['priority']['commitment'] == 'YES'
        assert endogenous['information']['commitment'] == 'NO'
        assert endogenous['reason'] == 'PROGRAM_CANNOT_CHANGE_OBSERVABLE_EVIDENCE'

        legacy = m.nominate_grounded_epistemic_program_step_intent(
            trial, 'FEAS-A', fob('A'), act_ob()
        )
        assert legacy['status'] == 'ABSTAIN', (
            'public path omitted the already-earned information-value premise and still nominated'
        )
        assert calls == []
    finally:
        td.cleanup()


def test_ranger5_omitting_information_cannot_turn_explicit_no_into_yes_at_lower_owner():
    td, m, calls, world, trial, _ = fixture()
    try:
        dc = nondiscriminating_context()
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        priority = derive_current_decision_bearing_commitment(
            trial=trial,
            deficit=deficit,
            decision_context=dc,
            capabilities=m.capabilities,
            values=m.values,
            current_frame_epochs=dict(m.frames.epochs),
            current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs),
            current_coordination_epochs=dict(m.coordinations.epochs),
        )
        information = derive_current_program_discrimination_commitment(
            trial=trial,
            decision_context=dc,
            decision_bearing_commitment=priority,
        )
        assert priority.commitment.value == 'YES'
        assert information.commitment.value == 'NO'

        complete = derive_epistemic_program_step_commitment(
            trial=trial,
            deficit=deficit,
            feasibility=typed_feasible(),
            capabilities=m.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state,
            priority_commitment=priority,
            information_commitment=information,
        )
        assert not complete.licenses_yes()

        omitted = derive_epistemic_program_step_commitment(
            trial=trial,
            deficit=deficit,
            feasibility=typed_feasible(),
            capabilities=m.capabilities,
            obligation=act_ob(),
            current_frame_epochs=dict(m.frames.epochs),
            current_state=m.action_closure.current_state,
            priority_commitment=priority,
        )
        assert not omitted.licenses_yes(), (
            'omitting a known required information premise changed NO into YES'
        )
    finally:
        td.cleanup()


def test_ranger6_unrelated_yes_commitments_cannot_impersonate_priority_and_information():
    td, m, calls, world, trial, dc = fixture()
    try:
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        forged_priority = RelationalCommitment(
            'P-FORGED-MS1915', 'unrelated-priority-target', TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=('UNRELATED',),
        )
        forged_information = RelationalCommitment(
            'I-FORGED-MS1915', 'unrelated-information-target', TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=('UNRELATED',),
        )
        c = derive_epistemic_program_step_commitment(
            trial=trial, deficit=deficit, feasibility=typed_feasible(), capabilities=m.capabilities,
            obligation=act_ob(), current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
            priority_commitment=forged_priority, information_commitment=forged_information,
        )
        assert not c.licenses_yes(), 'unrelated YES commitments impersonated decision-bearing premises'
    finally:
        td.cleanup()


def test_ranger7_wrong_information_target_cannot_ride_on_genuine_priority():
    td, m, calls, world, trial, dc = fixture()
    try:
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        priority = derive_current_decision_bearing_commitment(
            trial=trial, deficit=deficit, decision_context=dc, capabilities=m.capabilities, values=m.values,
            current_frame_epochs=dict(m.frames.epochs), current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs), current_coordination_epochs=dict(m.coordinations.epochs),
        )
        assert priority.licenses_yes()
        forged_information = RelationalCommitment(
            'I-WRONG-TARGET-MS1915', 'wrong-information-target', TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=(trial.trial_id, priority.commitment_id),
        )
        c = derive_epistemic_program_step_commitment(
            trial=trial, deficit=deficit, feasibility=typed_feasible(), capabilities=m.capabilities,
            obligation=act_ob(), current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
            priority_commitment=priority, information_commitment=forged_information,
        )
        assert not c.licenses_yes(), 'wrong-target information commitment was accepted'
    finally:
        td.cleanup()


def test_ranger8_information_target_without_exact_trial_priority_ancestry_cannot_license():
    td, m, calls, world, trial, dc = fixture()
    try:
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        priority = derive_current_decision_bearing_commitment(
            trial=trial, deficit=deficit, decision_context=dc, capabilities=m.capabilities, values=m.values,
            current_frame_epochs=dict(m.frames.epochs), current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs), current_coordination_epochs=dict(m.coordinations.epochs),
        )
        assert priority.licenses_yes()
        target = f'epistemic-program-information:{trial.trial_id}:step:{len(trial.step_records)}'
        forged_information = RelationalCommitment(
            'I-MISSING-ANCESTRY-MS1915', target, TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=('UNRELATED',),
        )
        c = derive_epistemic_program_step_commitment(
            trial=trial, deficit=deficit, feasibility=typed_feasible(), capabilities=m.capabilities,
            obligation=act_ob(), current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
            priority_commitment=priority, information_commitment=forged_information,
        )
        assert not c.licenses_yes(), 'information commitment without trial/priority ancestry was accepted'
    finally:
        td.cleanup()


def test_ranger9_wrong_priority_target_cannot_hide_behind_correctly_bound_information():
    td, m, calls, world, trial, dc = fixture()
    try:
        deficit = m.epistemic_deficits.records[trial.deficit_id]
        forged_priority = RelationalCommitment(
            'P-WRONG-TARGET-MS1915', 'wrong-priority-target', TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=(trial.deficit_id,),
        )
        information_target = f'epistemic-program-information:{trial.trial_id}:step:{len(trial.step_records)}'
        bound_to_forged = RelationalCommitment(
            'I-BOUND-TO-FORGED-P-MS1915', information_target, TernaryCommitment.YES,
            reason='FORGED_YES', premise_ids=(trial.trial_id, forged_priority.commitment_id),
        )
        c = derive_epistemic_program_step_commitment(
            trial=trial, deficit=deficit, feasibility=typed_feasible(), capabilities=m.capabilities,
            obligation=act_ob(), current_frame_epochs=dict(m.frames.epochs), current_state=m.action_closure.current_state,
            priority_commitment=forged_priority, information_commitment=bound_to_forged,
        )
        assert not c.licenses_yes(), 'wrong-target priority commitment was accepted'
        assert c.reason == 'EPISTEMIC_DECISION_BEARING_PRIORITY_BINDING_REQUIRED'
    finally:
        td.cleanup()


def test_positive_control_public_grounded_adapter_nominates_when_decision_context_earns_both_premises():
    td, m, calls, world, trial, dc = fixture()
    try:
        n = m.nominate_grounded_epistemic_program_step_intent(
            trial, 'FEAS-A', fob('A'), act_ob(), decision_context=dc,
        )
        assert n['status'] == 'ACTION_INTENT_NOMINATED', n
        assert n['priority']['commitment'] == 'YES'
        assert n['information']['commitment'] == 'YES'
        assert n['commitment']['commitment'] == 'YES'
        qualifiers = dict(n['commitment']['qualifiers'])
        assert qualifiers['decision_premises'] == 'PRIORITY_AND_INFORMATION_EXACTLY_BOUND'
        assert n['execution_authority'] == 'NONE'
        assert calls == []
    finally:
        td.cleanup()
