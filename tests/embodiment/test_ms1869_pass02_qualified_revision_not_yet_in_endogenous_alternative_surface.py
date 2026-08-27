from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def _surface_signature(surface):
    return tuple(tuple(r.digest() for r in rows) for rows in surface.get('relation_sets',()))


def test_current_projection_conditioned_revision_does_not_silently_rewrite_endogenous_three_locus_model_surface():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        before=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        assert before['status']=='THREE_LOCUS_CHAIN_MODEL_SURFACE'
        sig_before=_surface_signature(before)
        binding=_qualify_revised_surface(m,c)
        assert m._projection_conditioned_binding_current(binding)
        after=m.derive_three_locus_chain_action_outcome_epistemic_relation_sets()
        assert after['status']=='THREE_LOCUS_CHAIN_MODEL_SURFACE'
        assert _surface_signature(after)==sig_before
        # The newly qualified refined B->sx branch is real/current but is not yet
        # represented in the endogenous alternative surface constructor.
        assert 'R-B-SX-1868' in binding.relation_ids()
        assert all(r.next_state_id!='sx' for rows in after['relation_sets'] for r in rows if r.state_id=='s1' and r.capability_id=='B')
        assert m.epistemic_deficits.records['D'].state.value=='REVISIT_REQUIRED'
    finally:
        td.cleanup()
