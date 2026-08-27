from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_fresh_unknown_rebinds_to_internally_recovered_revised_surface_digest_and_projection_currentness():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        accepted=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        assert accepted['status']=='OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        fresh=m.append_evidence('E-U-1883',{'kind':'FRESH_UNKNOWN_AFTER_MODEL_REVISION'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        new=m.record_revised_surface_action_limited_unknown(
            old_deficit_id='D',new_deficit_id='D-1883',unknown_evidence_id=fresh.evidence_id,missing_discriminator_signature_sha256='f'*64)
        assert new.state.value=='ACTION_LIMITED'
        assert new.hypothesis_digest_sha256==accepted['revised_hypothesis_digest_sha256']
        assert new.hypothesis_digest_sha256!=m.epistemic_deficits.records['D'].hypothesis_digest_sha256
        assert new.unknown_evidence_id=='E-U-1883'
        pa=[a for a in new.premise_anchors if a.kind=='PROJECTION']
        assert len(pa)==1 and pa[0].object_id==b.projection_id
        assert 'SUCCESSOR_OF:D' in new.assistance_ancestry
        assert m.epistemic_deficits.records['D'].state.value=='STALE'
        assert m.epistemic_development_pressure_ids()==('D-1883',)
        # Projection change stales the successor through the newly earned anchor.
        m.change_epistemic_projection(b.projection_id,new_signature_sha256='7'*64,reason='POST_SUCCESSOR_REFINEMENT_DRIFT')
        assert m.epistemic_deficits.records['D-1883'].state.value=='STALE'
    finally: td.cleanup()
