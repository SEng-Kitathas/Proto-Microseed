from __future__ import annotations

import pytest

from microseed.development.epistemic import EpistemicProjectionRecord, EpistemicProjectionRegistry
from scratch.ms1989_selected_dependency_lineage_boundary import run_ms1989


def _record(pid: str, sig: str, *, source=(), dependency=()) -> EpistemicProjectionRecord:
    return EpistemicProjectionRecord(
        projection_id=pid,
        signature_sha256=sig,
        source_projection_epochs=tuple(source),
        dependency_projection_epochs=tuple(dependency),
    )


def test_ms1989_process_keeps_unused_basis_source_from_controlling_currentness():
    result=run_ms1989()
    assert result['status']=='PASS'
    assert result['candidate_input_positions']==[0,1]
    assert result['full_basis_ids']==['P-MS1989-A','P-MS1989-B','P-MS1989-D','P-MS1989-F']
    assert result['selected_dependency_ids']==['P-MS1989-A','P-MS1989-B']
    assert result['C_current_after_unused_source_change'] is True
    assert result['C_evaluable_after_unused_source_change'] is True
    assert result['C_stale_after_selected_source_change'] is True
    assert result['basis_ancestry_preserved'] is True
    assert result['semantic_feature_authority']==result['truth_authority']==result['language_authority']=='NONE'


def test_selected_dependency_lineage_controls_currentness_but_full_basis_is_preserved():
    reg=EpistemicProjectionRegistry()
    a='a'*64; b='b'*64; c='c'*64
    reg.register(_record('A',a))
    reg.register(_record('B',b))
    rec=_record('C',c,source=(('A',0,a),('B',0,b)),dependency=(('A',0,a),))
    reg.register(rec)
    packet=rec.serializable()
    assert packet['source_projection_epochs']==[('A',0,a),('B',0,b)] or packet['source_projection_epochs']==(('A',0,a),('B',0,b))
    assert packet['dependency_projection_epochs']==[('A',0,a)] or packet['dependency_projection_epochs']==(('A',0,a),)
    restored=EpistemicProjectionRecord.from_serializable(packet)
    assert restored.source_projection_epochs==(('A',0,a),('B',0,b))
    assert restored.dependency_projection_epochs==(('A',0,a),)

    reg.change('B',new_signature_sha256='d'*64)
    assert reg.records['C'].current
    assert reg.is_current('C',0)

    reg.change('A',new_signature_sha256='e'*64)
    assert not reg.records['C'].current
    assert not reg.is_current('C',reg.records['C'].epoch)


def test_legacy_empty_dependency_lineage_keeps_full_basis_currentness_behavior():
    reg=EpistemicProjectionRegistry()
    a='1'*64; b='2'*64; c='3'*64
    reg.register(_record('A',a))
    reg.register(_record('B',b))
    reg.register(_record('C',c,source=(('A',0,a),('B',0,b))))
    reg.change('B',new_signature_sha256='4'*64)
    assert not reg.records['C'].current


def test_full_basis_must_still_be_current_at_registration_even_if_source_is_not_selected():
    reg=EpistemicProjectionRegistry()
    a='5'*64; b='6'*64
    reg.register(_record('A',a))
    reg.register(_record('B',b))
    reg.change('B',new_signature_sha256='7'*64)
    with pytest.raises(ValueError,match='EPISTEMIC_SOURCE_PROJECTION_NOT_CURRENT'):
        reg.register(_record(
            'C','8'*64,
            source=(('A',0,a),('B',0,b)),
            dependency=(('A',0,a),),
        ))


def test_candidate_selected_dependency_is_derived_from_signed_basis_and_positions_on_roundtrip():
    from microseed.development.projection_discovery import EpistemicProjectionCandidate

    basis=(('A',0,'a'*64),('B',0,'b'*64),('D',0,'d'*64),('F',0,'f'*64))
    candidate=EpistemicProjectionCandidate(
        candidate_id='proj-cand-ms1989-roundtrip',
        input_positions=(0,1),
        key_to_bucket=((('0','0'),'bucket-0'),(('0','1'),'bucket-1'),(('1','0'),'bucket-1'),(('1','1'),'bucket-0')),
        bucket_action_prediction=(('bucket-0','C','C0'),('bucket-1','C','C1')),
        train_accuracy=1.0,validation_accuracy=1.0,action_baseline_accuracy=.5,min_scope_accuracy=1.0,
        lift=.5,score=.49,raw_key_count=4,bucket_count=2,
        source_sample_ids=('S0','S1'),frame_epochs=(('F',0),),assistance_ancestry=('TEST',),
        source_projection_epochs=basis,
    )
    assert [x[0] for x in candidate.dependency_projection_epochs]==['A','B']
    packet=candidate.serializable()
    # Selected dependency is a deterministic consequence of already signed basis+positions,
    # not a second caller-controlled identity field.
    assert 'dependency_projection_epochs' not in packet
    restored=EpistemicProjectionCandidate.from_serializable(packet)
    assert restored.dependency_projection_epochs==candidate.dependency_projection_epochs
    assert restored.candidate_id==candidate.candidate_id
    assert restored.digest()==candidate.digest()


def test_candidate_rejects_supplied_dependency_that_disagrees_with_selected_positions():
    from microseed.development.projection_discovery import EpistemicProjectionCandidate

    basis=(('A',0,'a'*64),('B',0,'b'*64),('D',0,'d'*64))
    with pytest.raises(ValueError,match='CANDIDATE_DEPENDENCY_PROJECTIONS_DO_NOT_MATCH_SELECTED_INPUT_POSITIONS'):
        EpistemicProjectionCandidate(
            candidate_id='proj-cand-ms1989-mismatch',input_positions=(0,1),
            key_to_bucket=((('0','0'),'bucket-0'),),
            bucket_action_prediction=(('bucket-0','C','C0'),),
            train_accuracy=1.0,validation_accuracy=1.0,action_baseline_accuracy=.5,min_scope_accuracy=1.0,
            lift=.5,score=.49,raw_key_count=1,bucket_count=1,
            source_sample_ids=('S0',),frame_epochs=(('F',0),),assistance_ancestry=('TEST',),
            source_projection_epochs=basis,
            dependency_projection_epochs=(basis[0],basis[2]),
        )


def test_source_based_candidate_identity_remains_ms1988_compatible_while_dependency_is_derived():
    from microseed.development.projection_discovery import ProjectionDiscoveryConfig, ProjectionSample, discover_epistemic_projection_candidates

    basis=(('A',0,'a'*64),('B',0,'b'*64),('D',0,'d'*64),('F',0,'f'*64))
    rows=[]
    for i in range(48):
        n=i%16
        raw=tuple(str((n>>s)&1) for s in (3,2,1,0))
        effect='C1' if (int(raw[0])^int(raw[1])) else 'C0'
        rows.append(ProjectionSample(f'S{i}',raw,'C',effect,'S','FRAME',0,source_projection_epochs=basis))
    cfg=ProjectionDiscoveryConfig(max_subset=2,min_train_support=24,min_key_action_support=2,min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=16)
    found=discover_epistemic_projection_candidates(tuple(rows[:32]),tuple(rows[32:]),cfg)
    exact=[c for c in found if c.input_positions==(0,1)]
    assert len(exact)==1
    candidate=exact[0]
    # Exact values independently matched sealed MS1988 in a detached-worktree boundary check.
    assert candidate.candidate_id=='proj-cand-659ab3b00df7224f5100'
    assert candidate.digest()=='6c19bb59464942b716d607e65d4c1f838076056519de9407521f756338632d21'
    assert [x[0] for x in candidate.dependency_projection_epochs]==['A','B']
