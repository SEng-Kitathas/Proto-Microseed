from __future__ import annotations

from dataclasses import replace

from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus, _close
from tests.embodiment.test_ms1918_pass07_authenticated_probe_observation_closure import (
    _install_observation, _execute_probe, _assured_observe, _advance,
)


def _challenge(next_state: str = 'ms1920-surprise'):
    td,m,calls,b,s=_bound_at_probe_locus()
    _install_observation(m,{'next_state_id':next_state},bind_frame=True)
    prior,dc,n,e=_execute_probe(m)
    eid=e['execution']['execution_id']
    observed=_assured_observe(m,eid,evidence_id=f'E-MS1920-{next_state}',capture_id=f'C-MS1920-{next_state}')
    assert observed['status']=='ACTION_OUTCOME_OBSERVED',observed
    advanced=_advance(m,prior,n,e)
    bearing=m.assess_epistemic_program_step_outcome_bearing(prior,advanced,dc)
    assert bearing['status']=='MODEL_SPACE_CHALLENGE' and bearing['revisit_status']=='REVISIT_REQUIRED',bearing
    return td,m,calls,prior,dc,n,e,advanced,eid


def test_ranger1_live_direct_probe_challenge_has_no_owned_predecessor_outcome_pair():
    td,m,calls,prior,dc,n,e,advanced,eid=_challenge('no-predecessor')
    try:
        ex=m.action_closure.executions[eid]
        intent=m.action_closure.intents[ex.intent_id]
        outcome_evidence_ids={o.evidence_id for o in m.action_closure.outcomes.values()}
        assert intent.control_state_evidence_id=='E-MS1904-PROBE-LOCUS-S1'
        assert intent.control_state_evidence_id not in outcome_evidence_ids
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        assert admitted['status']=='ADMITTED_OPAQUE_TRANSITION_SAMPLE'
        history=m.derive_admitted_one_step_visible_history_refinements()
        assert history['status']=='ONE_STEP_VISIBLE_HISTORY_REFINEMENTS_FOUND'
        # Existing fixture history may contain other lawful pairs/refinements, but the
        # current challenge itself cannot form a predecessor/current pair.
        challenge_id=admitted['sample'].sample_id
        assert all(challenge_id not in c.source_sample_ids for c in history['refinements'])
        revisit=m.derive_revisit_one_step_visible_history_refinement('D-1904')
        assert revisit['status']=='NO_BOUNDED_REFINEMENT_FOR_REVISIT',revisit
        assert revisit['challenge_sample_ids']==(challenge_id,)
    finally:_close(m,td)


def test_ranger2_existing_refinement_surface_cannot_absorb_novel_challenge_endpoint_retroactively():
    td,m,calls,prior,dc,n,e,advanced,eid=_challenge('outside-existing-refinement')
    try:
        admitted=m.derive_admitted_opaque_transition_sample(eid)
        challenge=admitted['sample']
        history=m.derive_admitted_one_step_visible_history_refinements()
        target=[c for c in history['refinements'] if (c.start_token,c.action_token)==('s1','B')]
        assert len(target)==1,target
        existing=target[0]
        assert challenge.sample_id not in existing.source_sample_ids
        assert challenge.end_token not in {end for _,end,_ in existing.context_outcomes}
        revisit=m.derive_revisit_one_step_visible_history_refinement('D-1904')
        assert revisit['status']=='NO_BOUNDED_REFINEMENT_FOR_REVISIT'
    finally:_close(m,td)


def test_ranger3_grafting_one_real_predecessor_does_not_turn_single_surprise_into_refinement():
    td,m,calls,prior,dc,n,e,advanced,eid=_challenge('single-grafted-surprise')
    try:
        ex=m.action_closure.executions[eid]
        intent=m.action_closure.intents[ex.intent_id]
        # Hostile counterfactual: point the challenge at a real authenticated s0->s1
        # predecessor outcome already present in the fixture.  This grants pairing only;
        # it does not grant recurrence or endpoint unanimity.
        assert any(o.evidence_id=='E1858-LIVE-A' and o.actual_next_state_id=='s1' for o in m.action_closure.outcomes.values())
        m.action_closure.intents[ex.intent_id]=replace(intent,control_state_evidence_id='E1858-LIVE-A')
        history=m.derive_admitted_one_step_visible_history_refinements()
        assert history['successor_pair_count']>=1
        # The new s0-context endpoint conflicts with the recurrent s0->sx history, so
        # the coarse slot is unresolved rather than silently rewritten around one surprise.
        assert history['status']=='NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT',history
        revisit=m.derive_revisit_one_step_visible_history_refinement('D-1904')
        assert revisit['status']=='NO_BOUNDED_REFINEMENT_FOR_REVISIT'
    finally:_close(m,td)


def test_ranger4_no_refinement_means_no_revision_acceptance_or_successor_creation():
    td,m,calls,prior,dc,n,e,advanced,eid=_challenge('no-auto-rebind')
    try:
        refinement=m.derive_revisit_one_step_visible_history_refinement('D-1904')
        assert refinement['status']=='NO_BOUNDED_REFINEMENT_FOR_REVISIT'
        surface=m.derive_current_revisit_hypothesis_revision_surface('D-1904')
        assert surface['status']=='NO_CURRENT_REVISED_HYPOTHESIS_SURFACE'
        binding_id=next(iter(sorted(m.action_outcome_learning.projection_conditioned_bindings)))
        accepted=m.accept_revisit_hypothesis_revision('D-1904',binding_id)
        assert accepted=={'status':'REVISION_NOT_ACCEPTED','reason':'NO_CURRENT_REVISED_HYPOTHESIS_SURFACE','authority':'NONE'}
        try:
            m.record_revised_surface_action_limited_unknown(
                old_deficit_id='D-1904',new_deficit_id='D-1920',unknown_evidence_id='E-U-1904-LOCUS')
        except ValueError as exc:
            assert str(exc)=='REVISED_SURFACE_SUCCESSOR_REQUIRES_STALE_OLD_DEFICIT'
        else:
            raise AssertionError('successor created without lawful accepted revision')
    finally:_close(m,td)
