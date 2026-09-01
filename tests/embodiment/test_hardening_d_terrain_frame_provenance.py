
from __future__ import annotations

import tempfile
from pathlib import Path

from microseed import EpistemicStatus, ExternalProjectionQualifier
from tests.embodiment.test_frontier_d_cfe_relational_visibility_terrain import (
    _underlying_rows,_terrain_samples,_new_ms,_discover,
)


def _admit_good_projection(ms, *, projection_id='HARD-D-P'):
    rows=_terrain_samples(_underlying_rows(),'GOOD_XY')
    candidates=_discover(ms,rows)
    candidate=next(c for c in candidates if c.input_positions==(0,1))
    q=ms.append_evidence(
        'HARD-D-PROJECTION-QUAL',
        {'candidate_sha256':candidate.digest(),'independent':True,'terrain_contract':'GOOD_XY_DECLARED_AS_FRAME_F'},
        EpistemicStatus.PRESSURE_SUPPORTED,
        source='EXTERNAL-HARDENING-D',
    )
    ticket=ExternalProjectionQualifier(ms.evidence,qualifier_id='EXTERNAL-HARDENING-D').qualify(
        candidate,qualification_evidence=(q,)
    )
    rec=ms.admit_epistemic_projection_candidate(ticket,projection_id=projection_id)
    return candidate,rec


def _close(ms,td):
    try:ms.biography.close();ms.evidence.conn.close();ms.store.conn.close()
    finally:td.cleanup()


def test_undeclared_material_terrain_change_is_not_magically_observable_to_substrate():
    td=tempfile.TemporaryDirectory(prefix='hardening-d-undeclared-');ms=_new_ms(td)
    try:
        candidate,rec=_admit_good_projection(ms)
        assert rec.frame_epochs==(('F',0),)
        assert ms.epistemic_projections.is_current(rec.projection_id,rec.epoch)
        # External adapter can now present BAD_XZ instead of GOOD_XY while lying by
        # omission and continuing to call the operational frame F@0. Nothing inside
        # Microseed changed, so no lawful currentness owner can infer that hidden fact.
        bad=_terrain_samples(_underlying_rows(),'BAD_XZ')
        assert len(bad)>0
        assert all(row.frame_id=='F' and row.frame_epoch==0 for row in bad)
        assert ms.epistemic_projections.is_current(rec.projection_id,rec.epoch)
        assert ms.frames.is_current('F',0)
        # This is an environment-contract attribution boundary, not a license to
        # invent a hidden terrain detector or semantic CFE field.
        for forbidden in ('terrain_detector','cfe_field','developmental_geometry_manager'):
            assert not hasattr(ms,forbidden)
    finally:_close(ms,td)


def test_declared_material_terrain_change_uses_existing_operational_frame_currentness_to_stale_projection():
    td=tempfile.TemporaryDirectory(prefix='hardening-d-declared-');ms=_new_ms(td)
    try:
        candidate,rec=_admit_good_projection(ms)
        old_epoch=rec.epoch
        assert ms.epistemic_projections.is_current(rec.projection_id,old_epoch)
        stale_caps=ms.change_operational_frame('F',reason='DECLARED_MATERIAL_RELATIONAL_VISIBILITY_TERRAIN_CHANGE')
        assert stale_caps==set()
        now=ms.epistemic_projections.records[rec.projection_id]
        assert now.current is False
        assert now.epoch==old_epoch+1
        assert not ms.epistemic_projections.is_current(rec.projection_id,old_epoch)
        assert ms.frames.is_current('F',0) is False
        # Historical candidate/evidence bytes remain; current-use authority does not.
        assert candidate.candidate_id in ms.epistemic_projection_candidates
        assert rec.projection_id in ms.epistemic_projections.records
    finally:_close(ms,td)


def test_operationally_equivalent_coordinate_permutation_does_not_require_semantic_terrain_identity():
    rows=_underlying_rows()
    td1=tempfile.TemporaryDirectory(prefix='hardening-d-perm-a-');ms1=_new_ms(td1)
    td2=tempfile.TemporaryDirectory(prefix='hardening-d-perm-b-');ms2=_new_ms(td2)
    try:
        a=_discover(ms1,_terrain_samples(rows,'GOOD_XY'))
        b=_discover(ms2,_terrain_samples(rows,'GOOD_YX'))
        aa=next(c for c in a if c.input_positions==(0,1));bb=next(c for c in b if c.input_positions==(0,1))
        assert aa.validation_accuracy==bb.validation_accuracy==1.0
        assert round(aa.lift,12)==round(bb.lift,12)
        # The control establishes equivalence at the tested operational relation,
        # not sameness of a semantic 'terrain identity'. No change call is warranted
        # merely because coordinate order changed.
        assert ms1.frames.is_current('F',0) and ms2.frames.is_current('F',0)
        for ms in (ms1,ms2):
            assert not hasattr(ms,'terrain_identity_registry')
    finally:
        _close(ms1,td1);_close(ms2,td2)
