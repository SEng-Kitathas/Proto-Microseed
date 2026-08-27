from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture, _qualify_revised_surface,
)


def test_current_revised_surface_derives_unique_opaque_missing_discriminator_without_authority():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        binding = _qualify_revised_surface(m, c)
        accepted = m.accept_revisit_hypothesis_revision('D', binding.binding_id)
        assert accepted['status'] == 'OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        result = m.derive_current_revised_surface_missing_discriminator('D')
        assert result['status'] == 'CURRENT_UNIQUE_REVISED_SURFACE_MISSING_DISCRIMINATOR'
        assert len(result['missing_discriminator_signature_sha256']) == 64
        assert result['revised_hypothesis_digest_sha256'] == accepted['revised_hypothesis_digest_sha256']
        assert {w['action_id'] for w in result['witnesses']} == {'B'}
        assert all(len(w['candidate_outcome_digests']) >= 2 for w in result['witnesses'])
        assert result['authority'] == result['truth_authority'] == result['execution_authority'] == 'NONE'
        assert calls == ['A', 'B']
    finally:
        m.biography.close()
        m.evidence.conn.close()
        m.store.conn.close()
        td.cleanup()


def test_projection_drift_invalidates_derived_missing_discriminator_instead_of_reusing_stale_partition():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        binding = _qualify_revised_surface(m, c)
        m.accept_revisit_hypothesis_revision('D', binding.binding_id)
        before = m.derive_current_revised_surface_missing_discriminator('D')
        assert before['status'] == 'CURRENT_UNIQUE_REVISED_SURFACE_MISSING_DISCRIMINATOR'
        m.change_epistemic_projection(binding.projection_id, new_signature_sha256='9' * 64, reason='MS1888_HOSTILE_DRIFT')
        after = m.derive_current_revised_surface_missing_discriminator('D')
        assert after['status'] == 'ABSTAIN'
        assert after['reason'] == 'ACCEPTED_REVISION_MODEL_NOT_CURRENT'
    finally:
        m.biography.close()
        m.evidence.conn.close()
        m.store.conn.close()
        td.cleanup()
