from dataclasses import replace
from microseed.development.epistemic_action import derive_epistemic_program_step_commitment
from microseed.development.recruitment import RecruitmentOption
from microseed.runtime.types import FeasibilityState
from tests.embodiment.test_ms1904_1905_endogenous_direct_probe_program import _bound_at_probe_locus as _bound,_close
from tests.embodiment.test_ms1710_endogenous_epistemic_initiation import act_ob


def test_copied_matching_discriminator_must_not_license_trial_with_unowned_relation_ancestry():
    td,m,calls,b,s=_bound()
    try:
        formed=m.instantiate_current_revised_surface_direct_probe_trial(old_deficit_id='D',successor_deficit_id='D-1904',obligation=act_ob())
        assert formed['status']=='EPISTEMIC_TRIAL_INSTANTIATED'
        genuine=formed['trial']
        forged=replace(genuine,source_relation_digests=('f'*64,))
        assert forged.discrimination_signature_sha256==s.missing_discriminator_signature_sha256
        genuine_sat=m.derive_current_program_discriminator_satisfaction(genuine)
        assert genuine_sat.licenses_yes(), genuine_sat.serializable()
        forged_sat=m.derive_current_program_discriminator_satisfaction(forged)
        assert not forged_sat.licenses_yes(), forged_sat.serializable()
        cmt=derive_epistemic_program_step_commitment(
            trial=forged,deficit=m.epistemic_deficits.records['D-1904'],
            feasibility=RecruitmentOption('B',FeasibilityState.FEASIBLE),capabilities=m.capabilities,
            obligation=act_ob(),current_frame_epochs=dict(m.frames.epochs),current_state=m.action_closure.current_state,
            program_discriminator_satisfaction=forged_sat,
        )
        assert not cmt.licenses_yes(), cmt.serializable()
    finally:_close(m,td)
