from __future__ import annotations

import json, math, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from microseed import Authority, Microseed, OperationalFrameContract, ProjectionDiscoveryConfig, ProjectionSample, QualificationState
from microseed.development.projection_discovery import discover_epistemic_projection_candidates
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def _masks(count:int) -> tuple[int,...]:
    n=int(count)
    if n < 4:
        raise ValueError('COUNT_AT_LEAST_FOUR_REQUIRED')
    # Nuisance sources are even masks.  The final pair 2,3 uniquely XORs to 1,
    # so the useful pair is the final pair in lexicographic size-2 enumeration.
    return tuple(range(4,2*n,2))+(2,3)


def _rows(count:int) -> tuple[ProjectionSample,...]:
    masks=_masks(count)
    states=1 << max(masks).bit_length()
    rows=[]
    for rep in range(2):
        for n in range(states):
            raw=tuple(str((int(n & mask).bit_count()) & 1) for mask in masks)
            effect='H1' if (int(raw[-2]) ^ int(raw[-1])) else 'H0'
            rows.append(ProjectionSample(f'R-{rep}-{n:03d}',raw,'H',effect,'S','F',0))
    return tuple(rows)


def _cfg(states:int) -> ProjectionDiscoveryConfig:
    return ProjectionDiscoveryConfig(
        max_subset=2,min_train_support=states,min_key_action_support=3,
        min_validation_accuracy=.95,min_lift_over_action_baseline=.35,
        min_scope_accuracy=.95,max_candidates=64,
    )


def _subset_count(width:int,max_subset:int) -> int:
    return sum(math.comb(int(width),k) for k in range(1,min(int(width),int(max_subset))+1))


def run_ms1991() -> dict[str,object]:
    width=32
    rows=_rows(width)
    states=len(rows)//2
    train=rows[:states]; validation=rows[states:]
    cfg=_cfg(states)
    required=_subset_count(width,cfg.max_subset)
    assert required==528

    td=tempfile.TemporaryDirectory(prefix='ms1991-search-budget-')
    m=Microseed(Path(td.name))
    try:
        m.register_operational_frame(OperationalFrameContract(
            'F','MS1991 projection search budget frame','f'*64,
            Authority.DERIVED_READ_ONLY,('MS1991',),'CURRENT',
            qualification=QualificationState.SHADOW_QUALIFIED,
        ))

        before=len(m.epistemic_projection_candidates)
        insufficient=m.discover_epistemic_projection_candidates_with_budget(
            train,validation,cfg,max_subset_evaluations=required-1,
        )
        assert insufficient['status']=='DEFER_UNKNOWN',insufficient
        assert insufficient['reason']=='PROJECTION_SEARCH_SUBSET_EVALUATION_BUDGET_INSUFFICIENT'
        assert insufficient['required_subset_evaluations']==required
        assert insufficient['subset_evaluations_performed']==0
        assert insufficient['candidate_count']==0
        assert insufficient['search_complete'] is False
        assert len(m.epistemic_projection_candidates)==before

        # Legacy exhaustive constructor remains the identity reference.
        legacy=discover_epistemic_projection_candidates(train,validation,cfg)
        exact_legacy=[c for c in legacy if c.input_positions==(30,31)]
        assert len(exact_legacy)==1,[(c.input_positions,c.validation_accuracy,c.lift) for c in legacy]
        legacy_candidate=exact_legacy[0]
        assert legacy_candidate.validation_accuracy==1.0 and legacy_candidate.lift==.5

        sufficient=m.discover_epistemic_projection_candidates_with_budget(
            train,validation,cfg,max_subset_evaluations=required,
        )
        assert sufficient['status']=='EXHAUSTIVE_PROJECTION_SEARCH_COMPLETED',sufficient
        assert sufficient['search_complete'] is True
        assert sufficient['required_subset_evaluations']==required
        assert sufficient['subset_evaluations_performed']==required
        exact=[x for x in sufficient['candidates'] if tuple(x['input_positions'])==(30,31)]
        assert len(exact)==1,sufficient['candidates']
        assert exact[0]['candidate_id']==legacy_candidate.candidate_id
        assert exact[0]['candidate_sha256']==legacy_candidate.digest()
        assert exact[0]['validation_accuracy']==1.0 and exact[0]['lift']==.5

        zero_error=None
        try:
            m.discover_epistemic_projection_candidates_with_budget(
                train,validation,cfg,max_subset_evaluations=0,
            )
        except ValueError as exc:
            zero_error=str(exc)
        assert zero_error=='BOUNDED_PROJECTION_SEARCH_EVALUATION_BUDGET_REQUIRED'

        return {
            'status':'PASS',
            'width':width,
            'max_subset':cfg.max_subset,
            'required_subset_evaluations':required,
            'insufficient_budget':required-1,
            'insufficient_status':insufficient['status'],
            'insufficient_reason':insufficient['reason'],
            'insufficient_subset_evaluations_performed':insufficient['subset_evaluations_performed'],
            'sufficient_budget':required,
            'sufficient_status':sufficient['status'],
            'late_exact_positions':[30,31],
            'legacy_candidate_id':legacy_candidate.candidate_id,
            'bounded_candidate_id':exact[0]['candidate_id'],
            'candidate_identity_preserved':exact[0]['candidate_id']==legacy_candidate.candidate_id and exact[0]['candidate_sha256']==legacy_candidate.digest(),
            'validation_accuracy':exact[0]['validation_accuracy'],'lift':exact[0]['lift'],
            'cost_examples':{
                'N32_K2':_subset_count(32,2),
                'N64_K3':_subset_count(64,3),
                'N128_K4':_subset_count(128,4),
            },
            'partial_search_used':'NO',
            'source_ids_nominated':'NO',
            'semantic_attention_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
            'earned':'EXPLICIT_SUBSET_EVALUATION_BUDGET_CAN_FAIL_CLOSED_BEFORE_PARTIAL_PROJECTION_SEARCH_AND_PRESERVE_EXHAUSTIVE_CANDIDATE_IDENTITY_WHEN_SUFFICIENT',
        }
    finally:
        _close(m);td.cleanup()


def main() -> None:
    print(json.dumps(run_ms1991(),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
