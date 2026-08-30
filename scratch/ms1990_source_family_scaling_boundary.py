from __future__ import annotations

import json, tempfile, types, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from microseed import Authority, Microseed, OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample, QualificationState
from microseed.development.epistemic import EpistemicProjectionRecord
from microseed.development.projection_discovery import EpistemicProjectionCandidate
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _masks(count:int) -> tuple[int,...]:
    n=int(count)
    if n < 2:
        raise ValueError('COUNT_AT_LEAST_TWO_REQUIRED')
    # First source mask 2 and final source mask 3 have XOR 1.  All nuisance
    # masks are even, so no other source pair has XOR 1.
    return (2,)+tuple(range(4,2*n,2))+(3,)


def _raw_row(n:int,masks:tuple[int,...]) -> tuple[str,...]:
    return tuple(str((int(n & mask).bit_count()) & 1) for mask in masks)


def _direct_candidate(index:int) -> EpistemicProjectionCandidate:
    return EpistemicProjectionCandidate(
        candidate_id=f'proj-cand-ms1990-source-{index:02d}',
        input_positions=(index,),
        key_to_bucket=((('0',),'bucket-0'),(('1',),'bucket-1')),
        bucket_action_prediction=(('bucket-0','SRC','E0'),('bucket-1','SRC','E1')),
        train_accuracy=1.0,validation_accuracy=1.0,action_baseline_accuracy=.5,min_scope_accuracy=1.0,
        lift=.5,score=.49,raw_key_count=2,bucket_count=2,
        source_sample_ids=(f'SRC-{index:02d}',),frame_epochs=(('F',0),),assistance_ancestry=('MS1990_SYNTHETIC_DIRECT_SOURCE',),
    )


def _target_config(max_subset:int,min_support:int) -> ProjectionDiscoveryConfig:
    return ProjectionDiscoveryConfig(
        max_subset=max_subset,min_train_support=min_support,min_key_action_support=3,
        min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.95,max_candidates=128,
    )


def _run_case(count:int) -> dict[str,object]:
    masks=_masks(count)
    states=1 << max(masks).bit_length()
    td=tempfile.TemporaryDirectory(prefix=f'ms1990-source-family-{count}-')
    m=Microseed(Path(td.name))
    try:
        m.register_operational_frame(OperationalFrameContract(
            'F','MS1990 source-family frame','f'*64,Authority.DERIVED_READ_ONLY,('MS1990',),'CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
        ))
        ordered=[]
        for i in range(count):
            pid=f'P-MS1990-{i:02d}'
            candidate=_direct_candidate(i)
            m.epistemic_projection_candidates[candidate.candidate_id]=candidate
            m.epistemic_projections.register(EpistemicProjectionRecord(
                projection_id=pid,signature_sha256=candidate.digest(),frame_epochs=(('F',0),),
            ))
            ordered.append((pid,candidate))

        base=[]
        for rep in range(2):
            for n in range(states):
                raw=_raw_row(n,masks)
                effect='H1' if (int(raw[0]) ^ int(raw[-1])) else 'H0'
                base.append(ProjectionSample(f'BASE-{rep}-{n:03d}',raw,'H',effect,'S','F',0))
        base=tuple(base)

        def _owned_raw(_self):
            return {'status':'ADMITTED_OWNED_RAW_PROJECTION_SAMPLES','samples':base}
        m.derive_admitted_projection_samples_from_owned_raw_observations=types.MethodType(_owned_raw,m)

        bounded=m.derive_admitted_projection_samples_from_owned_projection_buckets(
            max_source_projections=count-1,max_projection_depth=0,
        )
        assert bounded['status']=='DEFER_UNKNOWN',bounded
        assert bounded['reason']=='COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND'
        assert bounded['compatible_source_projection_count']==count
        assert tuple(bounded['source_projection_ids'])==tuple(pid for pid,_ in ordered)

        admitted=m.derive_admitted_projection_samples_from_owned_projection_buckets(
            max_source_projections=count,max_projection_depth=0,
        )
        assert admitted['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',admitted
        assert admitted['source_projection_count']==count
        assert tuple(admitted['source_projection_ids'])==tuple(pid for pid,_ in ordered)
        rows=tuple(admitted['samples'])
        assert len(rows)==len(base)
        assert len(rows[0].raw_tokens)==count

        split=states
        one=m.discover_epistemic_projection_candidates(rows[:split],rows[split:],_target_config(1,states))
        assert one==[]
        found=m.discover_epistemic_projection_candidates(rows[:split],rows[split:],_target_config(2,states))
        candidates=[m.epistemic_projection_candidates[x['candidate_id']] for x in found]
        expected=(0,count-1)
        exact=[c for c in candidates if c.input_positions==expected]
        assert len(exact)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in candidates]
        target=exact[0]
        assert target.validation_accuracy==1.0 and target.lift==.5
        assert [x[0] for x in target.dependency_projection_epochs]==[ordered[0][0],ordered[-1][0]]

        return {
            'source_count':count,
            'lower_bound_status':bounded['status'],
            'lower_bound_reason':bounded['reason'],
            'exact_bound_status':admitted['status'],
            'vector_width':len(rows[0].raw_tokens),
            'single_source_candidates':0,
            'existing_learner_exact_positions':list(target.input_positions),
            'validation_accuracy':target.validation_accuracy,
            'lift':target.lift,
            'selected_dependency_ids':[x[0] for x in target.dependency_projection_epochs],
        }
    finally:
        _close(m); td.cleanup()


def run_ms1990() -> dict[str,object]:
    invalid_zero=None
    td=tempfile.TemporaryDirectory(prefix='ms1990-invalid-bound-')
    m=Microseed(Path(td.name))
    try:
        try:
            m.derive_admitted_projection_samples_from_owned_projection_buckets(max_source_projections=0)
        except ValueError as exc:
            invalid_zero=str(exc)
    finally:
        _close(m); td.cleanup()
    assert invalid_zero=='BOUNDED_SOURCE_PROJECTION_COUNT_REQUIRED'

    cases=[_run_case(17),_run_case(32)]
    return {
        'status':'PASS',
        'invalid_zero_rejection':invalid_zero,
        'cases':cases,
        'caller_source_ids_supplied':'NO',
        'lexicographic_truncation_used':'NO',
        'new_source_selection_mechanism_added':'NO',
        'earned':'EXPLICIT_POSITIVE_SOURCE_COUNT_CEILINGS_CAN_SCALE_BEYOND_16_WHILE_PRESERVING_NO_TRUNCATION_AND_EXISTING_PROJECTION_SEARCH',
        'semantic_feature_selection_authority':'NONE',
        'truth_authority':'NONE','language_authority':'NONE',
    }


def main() -> None:
    print(json.dumps(run_ms1990(),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
