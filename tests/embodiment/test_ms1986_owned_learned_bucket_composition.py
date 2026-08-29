from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from microseed import Authority, EpistemicStatus, ExternalProjectionQualifier, OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample, QualificationState
from microseed.development.epistemic import EpistemicProjectionRecord
from scratch.ms1985_two_learned_bucket_composition_boundary import QUADS, admit_source_projection, run_ms1985
from scratch.ms1986_owned_learned_bucket_composition import (
    World, build, execute_z, external_holdout, prepare_z_proposals, run_ms1986,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _prepare_owned_sources(prefix: str):
    td=tempfile.TemporaryDirectory(prefix=prefix); world=World(); m=build(Path(td.name),world)
    pa,_=admit_source_projection(m,'A',(0,1),'P-MS1986-A')
    pb,_=admit_source_projection(m,'B',(2,3),'P-MS1986-B')
    ps=prepare_z_proposals(m)
    for i in range(64):
        raw=QUADS[i%16]
        execute_z(m,world,raw,ps[raw],i)
    return td,world,m,pa,pb


def _admit_second_stage(m,pa,pb):
    composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=2)
    assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES'
    assert composed['source_projection_ids']==('P-MS1986-A','P-MS1986-B')
    samples=tuple(composed['samples'])
    cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=32,min_key_action_support=3,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=8)
    found=m.discover_epistemic_projection_candidates(samples[:48],samples[48:],cfg)
    assert found
    candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
    exact=[c for c in candidates if c.input_positions==(0,1) and c.digest() not in {pa.digest(),pb.digest()}]
    assert exact
    c=exact[-1]
    holdout=external_holdout(c,pa,pb)
    qe=m.append_evidence('Q-MS1986-SECOND-TEST',{'kind':'OWNED_BUCKET_COMPOSITION_HOLDOUT','candidate_sha256':c.digest(),'rows':holdout},EpistemicStatus.PRESSURE_SUPPORTED,source='EXTERNAL-MS1986-SECOND-TEST')
    ticket=ExternalProjectionQualifier(m.evidence,qualifier_id='EXTERNAL-MS1986-SECOND-TEST').qualify(c,qualification_evidence=(qe,))
    rec=m.admit_epistemic_projection_candidate(ticket,projection_id='P-MS1986-SECOND')
    return composed,c,rec


def test_owned_learned_bucket_composition_positive_path_and_exact_lineage():
    result=run_ms1986()
    assert result['status']=='PASS'
    assert result['source_projection_ids']==['P-MS1986-A','P-MS1986-B']
    assert result['source_projection_count']==2
    assert result['owned_second_stage_sample_count']==64
    assert result['single_source_candidates']==0
    assert result['second_stage_positions']==[0,1]
    assert result['validation_accuracy']==1.0
    assert result['external_holdout_count']==16
    assert [x[0] for x in result['source_projection_epochs']]==['P-MS1986-A','P-MS1986-B']
    assert result['new_projection_search_mechanism_added']=='NO'
    assert result['sample_persistence']=='NONE'
    assert result['semantic_symbol_authority']==result['semantic_composition_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_second_stage_projection_stales_transitively_when_source_projection_changes_and_cannot_reactivate_against_stale_source_epoch():
    td,world,m,pa,pb=_prepare_owned_sources('ms1986-lineage-hostile-')
    try:
        composed,c,rec=_admit_second_stage(m,pa,pb)
        expected=(
            ('P-MS1986-A',m.epistemic_projections.records['P-MS1986-A'].epoch,m.epistemic_projections.records['P-MS1986-A'].signature_sha256),
            ('P-MS1986-B',m.epistemic_projections.records['P-MS1986-B'].epoch,m.epistemic_projections.records['P-MS1986-B'].signature_sha256),
        )
        assert c.source_projection_epochs==expected
        assert rec.source_projection_epochs==expected
        assert m.epistemic_projections.is_current('P-MS1986-SECOND',rec.epoch)

        m.epistemic_projections.change('P-MS1986-A',new_signature_sha256='a'*64)
        stale=m.epistemic_projections.records['P-MS1986-SECOND']
        assert stale.current is False
        assert stale.epoch==rec.epoch+1
        assert not m.epistemic_projections.is_current('P-MS1986-SECOND',stale.epoch)
        with pytest.raises(ValueError,match='EPISTEMIC_SOURCE_PROJECTION_NOT_CURRENT'):
            m.epistemic_projections.reactivate('P-MS1986-SECOND',qualification_evidence_ids=('Q-REACTIVATE',))
    finally:
        _close(m);world.close();td.cleanup()


def test_owned_bucket_bridge_refuses_to_arbitrarily_truncate_compatible_source_projection_set():
    td,world,m,pa,pb=_prepare_owned_sources('ms1986-count-hostile-')
    try:
        original=m.epistemic_projections.records['P-MS1986-A']
        duplicate=EpistemicProjectionRecord(
            projection_id='P-MS1986-A-DUP',signature_sha256=original.signature_sha256,epoch=0,
            assistance_ancestry=original.assistance_ancestry,projection_origin=original.projection_origin,
            proposal_candidate_sha256=original.proposal_candidate_sha256,
            qualification_evidence_ids=original.qualification_evidence_ids,frame_epochs=original.frame_epochs,
            episode_schema_epochs=original.episode_schema_epochs,current=True,
        )
        m.epistemic_projections.register(duplicate)
        out=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=2)
        assert out['status']=='DEFER_UNKNOWN'
        assert out['reason']=='COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND'
        assert out['compatible_source_projection_count']==3
        assert out['max_source_projections']==2
        assert out['samples']==()
        assert out['semantic_symbol_authority']==out['semantic_composition_authority']==out['truth_authority']=='NONE'
    finally:
        _close(m);world.close();td.cleanup()


def test_owned_bucket_bridge_requires_exact_recoverable_source_projection_content():
    td,world,m,pa,pb=_prepare_owned_sources('ms1986-content-hostile-')
    try:
        m.epistemic_projection_candidates.clear()
        out=m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=2)
        assert out['status']=='NO_ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLE'
        assert out['reason']=='NO_COMPATIBLE_CURRENT_SOURCE_PROJECTION'
        assert {reason for _,reason in out['source_rejections']}=={'SOURCE_PROJECTION_CONTENT_NOT_EXACTLY_RECOVERABLE'}
        assert out['samples']==()
    finally:
        _close(m);world.close();td.cleanup()


def test_projection_search_rejects_mixed_source_projection_lineage_rows():
    td=tempfile.TemporaryDirectory(prefix='ms1986-mixed-lineage-')
    from microseed import Microseed
    m=Microseed(Path(td.name))
    try:
        m.register_operational_frame(OperationalFrameContract('F','mixed lineage test frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1986',),'CURRENT',qualification=QualificationState.SHADOW_QUALIFIED))
        a=('P-A',0,'a'*64); b=('P-B',0,'b'*64)
        rows=[]
        for i in range(40):
            lineage=(a,) if i<20 else (b,)
            raw=('0','0') if i%2==0 else ('1','1')
            end='E0' if i%2==0 else 'E1'
            rows.append(ProjectionSample(f'MIX-{i}',raw,'Z',end,'S','F',0,source_projection_epochs=lineage))
        cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=20,min_key_action_support=2,min_validation_accuracy=.9,min_lift_over_action_baseline=.2,min_scope_accuracy=.9,max_candidates=4)
        assert m.discover_epistemic_projection_candidates(tuple(rows[:30]),tuple(rows[30:]),cfg)==[]
    finally:
        _close(m);td.cleanup()


def test_legacy_empty_source_lineage_keeps_ms1985_projection_digests_unchanged():
    result=run_ms1985()
    assert result['source_projection_A_sha256']=='4bde8127577b857952341dcd4da4c7ef18df9a9c46eefeebf777b520aca55d25'
    assert result['source_projection_B_sha256']=='88e4d5d1b31d751c2deb379d9e1663318eb347df7104777100b81b546a37aa2e'
