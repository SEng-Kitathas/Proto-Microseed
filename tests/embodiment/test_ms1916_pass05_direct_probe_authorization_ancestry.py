from __future__ import annotations

from dataclasses import replace

from microseed import Authority, EpistemicStatus, Observation
from microseed.development.epistemic import EpistemicDeficitState
from microseed.development.epistemic_priority import derive_regulatory_decision_bearing_commitment
from microseed.development.epistemic_action import (
    EpistemicDecisionBearingContext,
    derive_current_decision_bearing_commitment_from_grounded_surface,
    derive_current_grounded_feasibility_surface,
    derive_current_program_discrimination_commitment,
)
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture,
    _qualify_revised_surface,
)
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound, _close


def _successor_at_state(state_id: str, *, deficit_id: str = 'D-1916'):
    td, m, calls, c = _qualified_refinement_fixture()
    b = _qualify_revised_surface(m, c)
    m.accept_revisit_hypothesis_revision('D', b.binding_id)
    m.observe_opaque_control_state(
        Observation(f'MS1916-{state_id}', 'EXT', 'opaque-control', state_id, authority=Authority.OBSERVATION_ONLY),
        evidence_id=f'E-MS1916-{state_id}',
    )
    fresh = m.append_evidence(
        f'E-U-{deficit_id}', {'kind': 'FRESH_UNKNOWN_AT_' + state_id},
        EpistemicStatus.UNKNOWN_INCOMPLETE, source='RESEARCH',
    )
    s = m.record_revised_surface_action_limited_unknown(
        old_deficit_id='D', new_deficit_id=deficit_id, unknown_evidence_id=fresh.evidence_id,
    )
    bound = m.bind_current_revised_surface_direct_probe(old_deficit_id='D', successor_deficit_id=deficit_id)
    assert bound['status'] == 'PROBE_AVAILABLE', bound
    return td, m, calls, b, s


def _close_fixture(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def _surface_and_trial(m, deficit_id: str):
    surface = m.derive_current_revised_surface_direct_probe_decision_surface(
        old_deficit_id='D', successor_deficit_id=deficit_id,
    )
    trial_out = m.instantiate_current_revised_surface_direct_probe_trial(
        old_deficit_id='D', successor_deficit_id=deficit_id, obligation=act_ob(),
    )
    return surface, trial_out


def _priority_information(m, deficit_id: str, trial, surface):
    dc = EpistemicDecisionBearingContext(tuple(surface['relation_sets']), ())
    opts, _ = derive_current_grounded_feasibility_surface(
        capabilities=m.capabilities, operational_scope_id=act_ob().operational_scope_id,
    )
    priority = derive_current_decision_bearing_commitment_from_grounded_surface(
        trial=trial,
        deficit=m.epistemic_deficits.records[deficit_id],
        decision_context=dc,
        feasibility_options=opts,
        capabilities=m.capabilities,
        values=m.values,
        current_frame_epochs=dict(m.frames.epochs),
        current_episode_epochs=dict(m.episodes.epochs),
        current_topology_epochs=dict(m.topologies.epochs),
        current_coordination_epochs=dict(m.coordinations.epochs),
    )
    info = derive_current_program_discrimination_commitment(
        trial=trial, decision_context=dc, decision_bearing_commitment=priority,
    )
    return dc, priority, info


def test_ranger1_wrong_live_locus_refuses_direct_probe_decision_surface_and_trial_instantiation():
    td, m, calls, b, s = _bound()
    try:
        assert m.action_closure.current_state.state_id == 's2'
        formed = m.derive_current_revised_surface_direct_probe_program_candidate(
            old_deficit_id='D', successor_deficit_id='D-1904',
        )
        assert formed['status'] == 'CURRENT_DIRECT_PROBE_PROGRAM_CANDIDATE'
        branch_states = {
            m.action_outcome_learning.relations[rid].start_state_id
            for rid in formed['source_relation_ids']
        }
        assert branch_states == {'s1'}

        surface = m.derive_current_revised_surface_direct_probe_decision_surface(
            old_deficit_id='D', successor_deficit_id='D-1904',
        )
        assert surface['status'] == 'ABSTAIN'
        assert surface['reason'] == 'CURRENT_CONTROL_STATE_NOT_DIRECT_PROBE_LOCUS'

        trial = m.instantiate_current_revised_surface_direct_probe_trial(
            old_deficit_id='D', successor_deficit_id='D-1904', obligation=act_ob(),
        )
        assert trial['status'] == 'ABSTAIN'
        assert trial['reason'] == 'CURRENT_CONTROL_STATE_NOT_DIRECT_PROBE_LOCUS'
    finally:
        _close(m, td)


def test_ranger2_current_locus_composes_existing_branch_and_background_into_zero_authority_surface():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        assert surface['status'] == 'CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE', surface
        assert surface['conflict_slot'] == ('s1', 'B')
        assert surface['current_control_state_id'] == 's1'
        assert len(surface['relation_sets']) == 2
        assert surface['model_set_authority'] == 'PROPOSAL_ONLY_EPHEMERAL'
        assert surface['truth_authority'] == surface['execution_authority'] == 'NONE'
        for rows in surface['relation_sets']:
            slots = {(r.state_id, r.capability_id) for r in rows}
            assert ('s1', 'B') in slots
            assert ('s1', 'D') in slots
        assert trial_out['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', trial_out
        assert trial_out['trial'].start_state_id == 's1'
    finally:
        _close_fixture(m, td)


def test_ranger3_exact_bound_probe_available_can_reearn_priority_and_information_at_current_locus():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        assert trial_out['status'] == 'EPISTEMIC_TRIAL_INSTANTIATED', trial_out
        trial = trial_out['trial']
        dc, priority, info = _priority_information(m, 'D-1916', trial, surface)
        assert priority.licenses_yes(), priority.serializable()
        assert priority.reason == 'DISCRIMINATION_CAN_CHANGE_CURRENT_REGULATORY_ACTION'
        assert set(priority.qualifier('first_actions').split('|')) == {'B','D'}
        assert 'B' in priority.premise_ids
        assert info.licenses_yes(), info.serializable()
        assert info.reason == 'PROGRAM_CAN_CHANGE_OBSERVABLE_EVIDENCE'
    finally:
        _close_fixture(m, td)


def test_ranger4_probe_available_without_exact_bound_capability_epoch_remains_unknown():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        trial = trial_out['trial']
        rec = m.epistemic_deficits.records['D-1916']
        rec.probe_capability_epoch = rec.probe_capability_epoch + 1
        _, priority, info = _priority_information(m, 'D-1916', trial, surface)
        assert priority.commitment.value == 'UNKNOWN'
        assert priority.reason == 'BOUND_PROBE_CAPABILITY_EPOCH_NOT_CURRENT'
        assert not info.licenses_yes()
    finally:
        _close_fixture(m, td)


def test_ranger5_probe_available_relation_surface_must_contain_bound_probe_at_current_locus():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        trial = trial_out['trial']
        # Remove the B conflict edge from every live alternative but keep stable background.
        forged = {
            **surface,
            'relation_sets': tuple(tuple(r for r in rows if r.capability_id != 'B') for rows in surface['relation_sets']),
        }
        rows = tuple({(r.state_id, r.capability_id): r for r in rels} for rels in forged['relation_sets'])
        opts, _ = derive_current_grounded_feasibility_surface(
            capabilities=m.capabilities, operational_scope_id=act_ob().operational_scope_id,
        )
        priority = derive_regulatory_decision_bearing_commitment(
            deficit=m.epistemic_deficits.records['D-1916'], values=m.values, relation_sets=rows,
            options=opts, start_state_id=trial.start_state_id,
            current_capability_epochs=dict(m.capabilities.epochs),
            current_frame_epochs=dict(m.frames.epochs), current_episode_epochs=dict(m.episodes.epochs),
            current_topology_epochs=dict(m.topologies.epochs), current_coordination_epochs=dict(m.coordinations.epochs),
            current_capability_signatures={cid: cap.computed_signature_sha256() for cid, cap in m.capabilities.contracts.items()},
        )
        assert priority.commitment.value == 'UNKNOWN'
        assert priority.reason == 'BOUND_PROBE_RELATION_REQUIRED_AT_CURRENT_STATE'
    finally:
        _close_fixture(m, td)


def test_ranger6_revisit_required_is_still_rejected_by_priority_state_owner():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        trial = trial_out['trial']
        rec = m.epistemic_deficits.records['D-1916']
        rec.state = EpistemicDeficitState.REVISIT_REQUIRED
        _, priority, info = _priority_information(m, 'D-1916', trial, surface)
        assert priority.commitment.value == 'UNKNOWN'
        assert priority.reason == 'ACTION_LIMITED_OR_EXACT_BOUND_PROBE_AVAILABLE_REQUIRED'
        assert not info.licenses_yes()
    finally:
        _close_fixture(m, td)


def test_ranger7_end_to_end_public_grounded_nomination_requires_current_revised_surface_context():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        trial = trial_out['trial']
        dc = EpistemicDecisionBearingContext(tuple(surface['relation_sets']), ())
        n = m.nominate_grounded_epistemic_program_step_intent(
            trial, 'FEAS-B', fob('B'), act_ob(), decision_context=dc,
        )
        assert n['status'] == 'ACTION_INTENT_NOMINATED', n
        assert n['priority']['commitment'] == 'YES'
        assert n['information']['commitment'] == 'YES'
        assert n['execution_authority'] == 'NONE'
    finally:
        _close_fixture(m, td)


def test_ranger8_state_drift_after_decision_context_prevents_fresh_nomination():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        surface, trial_out = _surface_and_trial(m, 'D-1916')
        trial = trial_out['trial']
        dc = EpistemicDecisionBearingContext(tuple(surface['relation_sets']), ())
        m.observe_opaque_control_state(
            Observation('MS1916-DRIFT-S2','EXT','opaque-control','s2',authority=Authority.OBSERVATION_ONLY),
            evidence_id='E-MS1916-DRIFT-S2',
        )
        n = m.nominate_grounded_epistemic_program_step_intent(
            trial, 'FEAS-B', fob('B'), act_ob(), decision_context=dc,
        )
        assert n['status'] == 'ABSTAIN'
        assert n['reason'] == 'EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
        assert n['local_precheck']['commitment'] == 'UNKNOWN'
    finally:
        _close_fixture(m, td)


def test_ranger9_ambiguous_current_background_slot_abstains_instead_of_choosing_one_relation():
    td, m, calls, b, s = _successor_at_state('s1')
    try:
        # Find the stable current s1/D background relation and add a conflicting current peer.
        original = next(
            r for r in m.action_outcome_learning.relations.values()
            if r.start_state_id == 's1' and r.capability_id == 'D' and m._action_outcome_relation_current(r)
        )
        duplicate = replace(
            original,
            relation_id='MS1916-AMBIGUOUS-BACKGROUND-D',
            next_state_id='ms1916-other-d',
            value_effect=float(original.value_effect) + 0.5,
        )
        m.action_outcome_learning.add_relation(duplicate)
        surface = m.derive_current_revised_surface_direct_probe_decision_surface(
            old_deficit_id='D', successor_deficit_id='D-1916',
        )
        assert surface['status'] == 'ABSTAIN'
        assert surface['reason'] == 'DIRECT_PROBE_BACKGROUND_RELATION_AMBIGUOUS'
        assert surface['ambiguous_slots'] == (('s1','D'),)
    finally:
        _close_fixture(m, td)
