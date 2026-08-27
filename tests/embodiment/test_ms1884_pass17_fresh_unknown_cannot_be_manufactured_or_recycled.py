import pytest

from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture,
    _qualify_revised_surface,
)


def _successor_events(m):
    return tuple(
        e for e in m.store.events()
        if e.get('kind') == 'EPISTEMIC_REVISED_SURFACE_SUCCESSOR_DEFICIT_RECORDED'
    )


def test_accepted_revision_does_not_recycle_old_unknown_into_successor_question():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        b = _qualify_revised_surface(m, c)
        accepted = m.accept_revisit_hypothesis_revision('D', b.binding_id)
        assert accepted['status'] == 'OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        old = m.epistemic_deficits.records['D']
        before = _successor_events(m)

        with pytest.raises(ValueError, match='REQUIRES_FRESH_UNKNOWN_EVIDENCE'):
            m.record_revised_surface_action_limited_unknown(
                old_deficit_id='D',
                new_deficit_id='D-RECYCLED-1884',
                unknown_evidence_id=old.unknown_evidence_id,
                missing_discriminator_signature_sha256='a' * 64,
            )

        assert 'D-RECYCLED-1884' not in m.epistemic_deficits.records
        assert _successor_events(m) == before
        assert m.epistemic_development_pressure_ids() == ()
    finally:
        td.cleanup()


def test_non_unknown_evidence_cannot_be_relabelled_as_fresh_successor_unknown():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        b = _qualify_revised_surface(m, c)
        accepted = m.accept_revisit_hypothesis_revision('D', b.binding_id)
        assert accepted['status'] == 'OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        pressure = m.append_evidence(
            'E-NOT-UNKNOWN-1884',
            {'kind': 'MODEL_REVISION_EXISTS_BUT_NO_NEW_UNKNOWN'},
            EpistemicStatus.PRESSURE_SUPPORTED,
            source='RESEARCH',
        )
        before = _successor_events(m)

        with pytest.raises(ValueError, match='REQUIRES_FRESH_UNKNOWN_INCOMPLETE'):
            m.record_revised_surface_action_limited_unknown(
                old_deficit_id='D',
                new_deficit_id='D-NOT-UNKNOWN-1884',
                unknown_evidence_id=pressure.evidence_id,
                missing_discriminator_signature_sha256='b' * 64,
            )

        assert 'D-NOT-UNKNOWN-1884' not in m.epistemic_deficits.records
        assert _successor_events(m) == before
        assert m.epistemic_development_pressure_ids() == ()
    finally:
        td.cleanup()
