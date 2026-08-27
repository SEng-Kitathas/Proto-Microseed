from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_qualified_revised_model_retains_exact_revisit_deficit_ancestry_without_staling_it():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        binding=_qualify_revised_surface(m,c)
        rec=m.epistemic_projections.records[binding.projection_id]
        assert m._projection_conditioned_binding_current(binding)
        assert 'DEFICIT:D' in rec.assistance_ancestry
        assert rec.proposal_candidate_sha256==c.digest()
        assert binding.projection_id==rec.projection_id
        assert binding.projection_epoch==rec.epoch
        assert binding.projection_signature_sha256==rec.signature_sha256
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
        assert binding.model_switch_authority==binding.truth_authority=='NONE'
    finally:
        td.cleanup()
