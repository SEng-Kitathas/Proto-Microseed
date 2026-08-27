from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture, _qualify_revised_surface,
)


def _close(m, td):
    m.biography.close(); m.evidence.conn.close(); m.store.conn.close(); td.cleanup()


def _successor_with_hash(token):
    td, m, calls, c = _qualified_refinement_fixture()
    binding = _qualify_revised_surface(m, c)
    accepted = m.accept_revisit_hypothesis_revision('D', binding.binding_id)
    fresh = m.append_evidence('E-U-MS1888', {'kind':'SAME_FRESH_UNKNOWN'}, EpistemicStatus.UNKNOWN_INCOMPLETE, source='RESEARCH')
    rec = m.record_revised_surface_action_limited_unknown(
        old_deficit_id='D', new_deficit_id='D-MS1888', unknown_evidence_id=fresh.evidence_id,
        missing_discriminator_signature_sha256=token,
    )
    return td, m, accepted, rec


def test_same_revised_model_and_same_fresh_unknown_accept_arbitrary_caller_discriminator_hashes():
    td1,m1,a1,r1=_successor_with_hash('1'*64)
    td2,m2,a2,r2=_successor_with_hash('2'*64)
    try:
        assert a1['revised_hypothesis_digest_sha256']==a2['revised_hypothesis_digest_sha256']
        assert r1.hypothesis_digest_sha256==r2.hypothesis_digest_sha256
        assert r1.unknown_evidence_id==r2.unknown_evidence_id=='E-U-MS1888'
        assert r1.missing_discriminator_signature_sha256=='1'*64
        assert r2.missing_discriminator_signature_sha256=='2'*64
        assert r1.missing_discriminator_signature_sha256!=r2.missing_discriminator_signature_sha256
    finally:
        _close(m1,td1); _close(m2,td2)
