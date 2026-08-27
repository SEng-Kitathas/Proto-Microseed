from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_accepted_revision_digest_is_recovered_from_owned_history_and_live_binding_rechecked():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        accepted=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        assert accepted['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        st=m.accepted_revisit_hypothesis_revision_status('D')
        assert st['status']=='CURRENT_ACCEPTED_REVISED_HYPOTHESIS_SURFACE'
        assert st['revised_hypothesis_digest_sha256']==accepted['revised_hypothesis_digest_sha256']
        assert b.binding_id in st['current_binding_ids']
        assert st['new_unknown_authority']==st['execution_authority']=='NONE'
        # Accepted history remains, but a stale live projection blocks current reuse.
        m.epistemic_projections.invalidate(b.projection_id)
        no=m.accepted_revisit_hypothesis_revision_status('D')
        assert no['status']=='ACCEPTED_REVISION_MODEL_NOT_CURRENT'
        assert no['revised_hypothesis_digest_sha256']==accepted['revised_hypothesis_digest_sha256']
    finally: td.cleanup()
