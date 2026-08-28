from __future__ import annotations

from pathlib import Path

from microseed import Microseed
from microseed.development.epistemic_action import EpistemicDecisionBearingContext
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob, fob
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus


def _close(m):
    m.biography.close();m.evidence.conn.close();m.store.conn.close()


def test_ranger1_replayed_control_state_does_not_reauthorize_caller_retained_direct_probe_trial():
    td,m,calls,b,s=_bound_at_probe_locus(); root=Path(td.name)
    try:
        surface=m.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
        dc=EpistemicDecisionBearingContext(tuple(surface['relation_sets']),())
        formed=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
        assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        trial=formed['trial']
        before=m.nominate_grounded_epistemic_program_step_intent(trial,'FEAS-B',fob('B'),act_ob(),decision_context=dc)
        assert before['status']=='ACTION_INTENT_NOMINATED'
        assert m.action_closure.current_state.state_id=='s1'
        _close(m); del m

        m2=Microseed(root)
        try:
            # Historical/current-state observation is reconstructed, but operational
            # contracts/handlers are not automatically restored as current authority.
            assert m2.action_closure.current_state.state_id=='s1'
            assert m2.action_closure.current_state.evidence_id=='E-MS1904-PROBE-LOCUS-S1'
            assert not m2.capabilities.contracts
            satisfaction=m2.derive_current_program_discriminator_satisfaction(trial)
            assert satisfaction.commitment.value=='UNKNOWN'
            assert satisfaction.reason=='PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST'
            restart_counts=(len(m2.action_closure.intents),len(m2.action_closure.executions))
            after=m2.nominate_grounded_epistemic_program_step_intent(trial,'FEAS-B',fob('B'),act_ob(),decision_context=dc)
            assert after['status']=='ABSTAIN'
            assert after['reason']=='EPISTEMIC_PROGRAM_STEP_LOCAL_PRECHECK_UNRESOLVED'
            assert (len(m2.action_closure.intents),len(m2.action_closure.executions))==restart_counts
        finally:_close(m2)
    finally:td.cleanup()


def test_ranger2_restart_history_cannot_rematerialize_current_direct_probe_surface_or_trial():
    td,m,calls,b,s=_bound_at_probe_locus(); root=Path(td.name)
    try:
        before=m.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
        assert before['status']=='CURRENT_REVISED_DIRECT_PROBE_DECISION_SURFACE'
        _close(m); del m
        m2=Microseed(root)
        try:
            assert m2.action_closure.current_state.state_id=='s1'
            candidate=m2.derive_current_revised_surface_direct_probe_program_candidate(old_deficit_id='D',successor_deficit_id='D-1904')
            surface=m2.derive_current_revised_surface_direct_probe_decision_surface(old_deficit_id='D',successor_deficit_id='D-1904')
            assert candidate['status']=='ABSTAIN'
            assert candidate['execution_authority']=='NONE'
            assert surface['status']=='ABSTAIN'
            assert surface['execution_authority']=='NONE'
            assert not hasattr(m2,'trial_registry')
            assert not hasattr(m2,'epistemic_program_trials')
        finally:_close(m2)
    finally:td.cleanup()
