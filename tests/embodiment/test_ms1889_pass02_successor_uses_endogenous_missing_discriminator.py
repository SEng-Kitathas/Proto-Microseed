from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture, _qualify_revised_surface,
)


def _close(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def test_successor_no_longer_requires_external_missing_discriminator_token():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        binding = _qualify_revised_surface(m, c)
        m.accept_revisit_hypothesis_revision('D', binding.binding_id)
        derived = m.derive_current_revised_surface_missing_discriminator('D')
        fresh = m.append_evidence('E-U-1889', {'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'}, EpistemicStatus.UNKNOWN_INCOMPLETE, source='RESEARCH')
        successor = m.record_revised_surface_action_limited_unknown(
            old_deficit_id='D', new_deficit_id='D-1889', unknown_evidence_id=fresh.evidence_id,
        )
        assert successor.missing_discriminator_signature_sha256 == derived['missing_discriminator_signature_sha256']
        assert 'MISSING_DISCRIMINATOR_DERIVED_FROM_CURRENT_REVISED_SURFACE' in successor.assistance_ancestry
        assert 'CALLER_MISSING_DISCRIMINATOR_TOKEN_IGNORED' not in successor.assistance_ancestry
    finally:
        _close(m, td)


def test_legacy_caller_token_cannot_override_current_derived_discriminator():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        binding = _qualify_revised_surface(m, c)
        m.accept_revisit_hypothesis_revision('D', binding.binding_id)
        derived = m.derive_current_revised_surface_missing_discriminator('D')
        fresh = m.append_evidence('E-U-1889-B', {'kind':'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'}, EpistemicStatus.UNKNOWN_INCOMPLETE, source='RESEARCH')
        successor = m.record_revised_surface_action_limited_unknown(
            old_deficit_id='D', new_deficit_id='D-1889-B', unknown_evidence_id=fresh.evidence_id,
            missing_discriminator_signature_sha256='f' * 64,
        )
        assert successor.missing_discriminator_signature_sha256 == derived['missing_discriminator_signature_sha256']
        assert successor.missing_discriminator_signature_sha256 != 'f' * 64
        assert 'CALLER_MISSING_DISCRIMINATOR_TOKEN_IGNORED' in successor.assistance_ancestry
    finally:
        _close(m, td)
