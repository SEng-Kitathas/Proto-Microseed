from microseed import EpistemicStatus
from tests.embodiment.test_ms1868_pass01_revised_model_deficit_succession_owner_audit import (
    _qualified_refinement_fixture,
    _qualify_revised_surface,
)


def test_projection_currentness_exists_but_only_explicitly_anchored_successors_depend_on_it():
    td, m, calls, c = _qualified_refinement_fixture()
    try:
        b = _qualify_revised_surface(m, c)
        accepted = m.accept_revisit_hypothesis_revision('D', b.binding_id)
        assert accepted['status'] == 'OLD_REVISIT_DEFICIT_STALED_FOR_HYPOTHESIS_REVISION'
        st = m.accepted_revisit_hypothesis_revision_status('D')
        assert st['status'] == 'CURRENT_ACCEPTED_REVISED_HYPOTHESIS_SURFACE'
        u = m.append_evidence(
            'E-U-1881',
            {'kind': 'FRESH_REVISED_UNKNOWN'},
            EpistemicStatus.UNKNOWN_INCOMPLETE,
            source='RESEARCH',
        )
        # Historical/legacy-style manual successor deliberately omits the projection anchor.
        new = m.record_action_limited_unknown(
            deficit_id='D-1881',
            question_key='Q-REVISED',
            hypothesis_digest_sha256=st['revised_hypothesis_digest_sha256'],
            unknown_evidence_id=u.evidence_id,
            missing_discriminator_signature_sha256='e' * 64,
            premise_anchors=m.epistemic_deficits.records['D'].premise_anchors,
            assistance_ancestry=('MS1881_MANUAL_SUCCESSOR_WITHOUT_PROJECTION_ANCHOR',),
        )
        assert new.state.value == 'ACTION_LIMITED'
        assert 'PROJECTION' in m._EPISTEMIC_PREMISE_KINDS
        assert all(a.kind != 'PROJECTION' for a in new.premise_anchors)

        # Pass 15 repaired the vocabulary, but dependency remains explicit rather than global:
        # a successor that does not carry the projection anchor is not retroactively coupled to it.
        m.epistemic_projections.invalidate(b.projection_id)
        assert not m.epistemic_projections.records[b.projection_id].current
        assert m.epistemic_deficits.records['D-1881'].state.value == 'ACTION_LIMITED'
    finally:
        td.cleanup()
