from microseed import EpistemicStatus
from microseed.development.epistemic import EpistemicCurrentnessAnchor
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import _qualified_refinement_fixture,_qualify_revised_surface


def test_projection_anchor_stales_only_successor_deficit_when_refinement_projection_changes():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c)
        accepted=m.accept_revisit_hypothesis_revision('D',b.binding_id)
        st=m.accepted_revisit_hypothesis_revision_status('D')
        rec=m.epistemic_projections.records[b.projection_id]
        u=m.append_evidence('E-U-1882',{'kind':'FRESH_REVISED_UNKNOWN'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        new=m.record_action_limited_unknown(
            deficit_id='D-1882',question_key='Q-REVISED',hypothesis_digest_sha256=st['revised_hypothesis_digest_sha256'],
            unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256='e'*64,
            premise_anchors=tuple(m.epistemic_deficits.records['D'].premise_anchors)+(EpistemicCurrentnessAnchor('PROJECTION',rec.projection_id,rec.epoch),),
        )
        assert new.state.value=='ACTION_LIMITED'
        out=m.change_epistemic_projection(rec.projection_id,new_signature_sha256='9'*64,reason='REFINEMENT_MODEL_DRIFT')
        assert 'D-1882' in out['stale_deficit_ids']
        assert m.epistemic_deficits.records['D-1882'].state.value=='STALE'
        assert m.epistemic_deficits.records['D'].state.value=='STALE'
        assert m.epistemic_development_pressure_ids()==()
    finally: td.cleanup()


def test_projection_anchor_must_be_current_at_successor_creation():
    td,m,calls,c=_qualified_refinement_fixture()
    try:
        b=_qualify_revised_surface(m,c); m.accept_revisit_hypothesis_revision('D',b.binding_id)
        rec=m.epistemic_projections.records[b.projection_id]
        m.change_epistemic_projection(rec.projection_id,new_signature_sha256='8'*64,reason='DRIFT')
        u=m.append_evidence('E-U-1882-B',{'kind':'FRESH_REVISED_UNKNOWN'},EpistemicStatus.UNKNOWN_INCOMPLETE,source='RESEARCH')
        try:
            m.record_action_limited_unknown(deficit_id='D-1882-B',question_key='Q',hypothesis_digest_sha256='a'*64,unknown_evidence_id=u.evidence_id,missing_discriminator_signature_sha256='b'*64,premise_anchors=(EpistemicCurrentnessAnchor('PROJECTION',rec.projection_id,rec.epoch),))
        except ValueError as e:
            assert 'EPISTEMIC_PREMISE_NOT_CURRENT:PROJECTION' in str(e)
        else: raise AssertionError('stale projection anchor must be rejected')
    finally: td.cleanup()
