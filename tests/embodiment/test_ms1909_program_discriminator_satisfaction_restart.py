from pathlib import Path
from microseed import Microseed
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _close_handles(m):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close()


def test_cold_restart_preserves_requirement_history_but_does_not_regrant_program_satisfaction():
    td,m,calls,b,s=_bound()
    root=Path(td.name)
    try:
        formed=m.instantiate_current_revised_surface_direct_probe_trial(
            old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
        assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        trial=formed['trial']
        before=m.derive_current_program_discriminator_satisfaction(trial)
        assert before.licenses_yes(),before.serializable()
        requirement_ids=tuple(sorted(
            x.binding_id for x in m.epistemic_contrasts.bindings.values()
            if x.deficit_id=='D-1904' and x.binding_origin=='DERIVED_CURRENT_REVISED_SURFACE_CONTRAST'))
        assert len(requirement_ids)==1

        # Historical MS1864 fixture relations were injected directly rather than through
        # the durable qualification API. Persist them here only so restart can prove that
        # relation history alone is still insufficient to recreate current authority.
        existing={(e.get('kind'),e.get('payload',{}).get('relation_id')) for e in m.store.events()}
        for r in m.action_outcome_learning.relations.values():
            key=('ACTION_OUTCOME_PREDICTIVE_RELATION_QUALIFIED',r.relation_id)
            if key not in existing:
                m.store.append('ACTION_OUTCOME_PREDICTIVE_RELATION_QUALIFIED',r.serializable())
        _close_handles(m)

        m2=Microseed(root)
        try:
            assert requirement_ids==tuple(sorted(
                x.binding_id for x in m2.epistemic_contrasts.bindings.values()
                if x.deficit_id=='D-1904' and x.binding_origin=='DERIVED_CURRENT_REVISED_SURFACE_CONTRAST'))
            assert len(m2.action_outcome_learning.relations)>=2
            # Constructor replay restores historical structures but intentionally does not
            # restore current frame/episode/value/capability ownership or executable handlers.
            assert not m2.frames.is_current('F',0)
            assert not m2.episodes.is_current('EP',0)
            assert not m2.values.is_current('V',0)
            assert not m2.capabilities.contracts
            cold=m2.derive_current_program_discriminator_satisfaction(trial)
            assert not cold.licenses_yes(),cold.serializable()
            assert cold.reason=='PROGRAM_SOURCE_RELATIONS_DO_NOT_REALIZE_REGISTERED_CONTRAST'
            assert dict(cold.qualifiers)['execution_authority']=='NONE'
        finally:
            _close_handles(m2)
    finally:
        td.cleanup()
