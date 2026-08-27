from pathlib import Path

from microseed import EpistemicStatus, Microseed
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture,
    _qualify_revised_surface,
)


def test_revised_surface_successor_survives_restart_without_authority_and_projection_drift_stales_it_selectively():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        root = Path(td.name)
        b = _qualify_revised_surface(m, c)
        accepted = m.accept_revisit_hypothesis_revision('D', b.binding_id)
        assert accepted['status'] == 'OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        fresh = m.append_evidence(
            'E-U-1885',
            {'kind': 'FRESH_UNKNOWN_AFTER_REVISED_SURFACE'},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source='RESEARCH',
        )
        new = m.record_revised_surface_action_limited_unknown(
            old_deficit_id='D',
            new_deficit_id='D-1885',
            unknown_evidence_id=fresh.evidence_id,
            missing_discriminator_signature_sha256='5' * 64,
        )
        revised_digest = new.hypothesis_digest_sha256
        projection_anchor = next(a for a in new.premise_anchors if a.kind == 'PROJECTION')
        old_digest = m.epistemic_deficits.records['D'].hypothesis_digest_sha256

        # Reincarnate from owned durable history.
        del m
        m2 = Microseed(root)

        old = m2.epistemic_deficits.records['D']
        successor = m2.epistemic_deficits.records['D-1885']
        assert old.state.value == 'STALE'
        assert old.hypothesis_digest_sha256 == old_digest
        assert successor.state.value == 'ACTION_LIMITED'
        assert successor.hypothesis_digest_sha256 == revised_digest
        assert successor.unknown_evidence_id == 'E-U-1885'
        assert projection_anchor in successor.premise_anchors
        assert m2.epistemic_development_pressure_ids() == ('D-1885',)
        assert m2.epistemic_revisit_required_ids() == ()

        # History may restore nonexecuting structures, never executable handlers/authority.
        assert all(contract.handler is None for contract in m2.capabilities.contracts.values())

        # The refined representation is a real currentness premise of only the successor.
        p = m2.epistemic_projections.records[projection_anchor.object_id]
        assert p.current is True and p.epoch == projection_anchor.epoch
        m2.change_epistemic_projection(
            projection_anchor.object_id,
            new_signature_sha256='6' * 64,
            reason='POST_RESTART_REFINED_REPRESENTATION_DRIFT',
        )
        assert m2.epistemic_deficits.records['D'].state.value == 'STALE'
        assert m2.epistemic_deficits.records['D-1885'].state.value == 'STALE'
        assert m2.epistemic_development_pressure_ids() == ()
    finally:
        td.cleanup()
