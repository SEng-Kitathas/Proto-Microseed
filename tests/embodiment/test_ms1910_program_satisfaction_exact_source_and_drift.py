from dataclasses import replace
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound,_close
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def _trial(m):
    formed=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
    assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
    return formed['trial']


def test_program_satisfaction_requires_exact_source_relation_set_not_subset_or_superset():
    td,m,calls,b,s=_bound()
    try:
        genuine=_trial(m)
        yes=m.derive_current_program_discriminator_satisfaction(genuine)
        assert yes.licenses_yes(),yes.serializable()
        assert len(genuine.source_relation_digests)>=2
        subset=replace(genuine,source_relation_digests=genuine.source_relation_digests[:-1])
        no_subset=m.derive_current_program_discriminator_satisfaction(subset)
        assert not no_subset.licenses_yes(),no_subset.serializable()
        superset=replace(genuine,source_relation_digests=tuple(sorted(genuine.source_relation_digests+('f'*64,))))
        no_super=m.derive_current_program_discriminator_satisfaction(superset)
        assert not no_super.licenses_yes(),no_super.serializable()
        assert no_super.reason=='PROGRAM_SOURCE_RELATION_ANCESTRY_NOT_EXACT'
    finally:_close(m,td)


def test_projection_drift_invalidates_program_satisfaction_through_existing_currentness_owner():
    td,m,calls,b,s=_bound()
    try:
        trial=_trial(m)
        assert m.derive_current_program_discriminator_satisfaction(trial).licenses_yes()
        m.change_epistemic_projection(b.projection_id,new_signature_sha256='9'*64,reason='MS1910_PROJECTION_DRIFT')
        after=m.derive_current_program_discriminator_satisfaction(trial)
        assert not after.licenses_yes(),after.serializable()
    finally:_close(m,td)


def test_episode_drift_invalidates_program_satisfaction_and_stales_deficit():
    td,m,calls,b,s=_bound()
    try:
        trial=_trial(m)
        assert m.derive_current_program_discriminator_satisfaction(trial).licenses_yes()
        m.change_episode_schema('EP',reason='MS1910_EPISODE_DRIFT')
        assert m.epistemic_deficits.records['D-1904'].state.value=='STALE'
        after=m.derive_current_program_discriminator_satisfaction(trial)
        assert not after.licenses_yes(),after.serializable()
        assert after.reason=='CURRENT_EPISTEMIC_DEFICIT_REQUIRED'
    finally:_close(m,td)
