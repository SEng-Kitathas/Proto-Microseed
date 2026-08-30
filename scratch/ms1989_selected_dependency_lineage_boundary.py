from __future__ import annotations

import json, tempfile, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from scratch.ms1988_depth4_recursive_bucket_genericity import (
    World, admit_source_projection, build, learn_composed, qualify_candidate, run_owned_action,
)
from tests.embodiment.test_ms1941_learned_signal_response_reentry import _close


def run_ms1989() -> dict[str, object]:
    td=tempfile.TemporaryDirectory(prefix='ms1989-lineage-'); world=World(); m=build(Path(td.name),world)
    try:
        admit_source_projection(m,'A',(0,1),'P-MS1989-A')
        admit_source_projection(m,'B',(2,3),'P-MS1989-B')
        admit_source_projection(m,'D',(4,5),'P-MS1989-D')
        admit_source_projection(m,'F',(6,7),'P-MS1989-F')
        run_owned_action(m,world,'C',0)
        _,candidate=learn_composed(m,'C','P-MS1989-C',(0,1),4,0)
        record=qualify_candidate(
            m,candidate,'P-MS1989-C','MS1989_SELECTED_DEPENDENCY_LINEAGE',
            [{'candidate_sha256':candidate.digest()}],
        )
        basis_ids=[x[0] for x in record.source_projection_epochs]
        dependency_ids=[x[0] for x in record.dependency_projection_epochs]
        assert basis_ids==['P-MS1989-A','P-MS1989-B','P-MS1989-D','P-MS1989-F']
        assert candidate.input_positions==(0,1)
        assert dependency_ids==['P-MS1989-A','P-MS1989-B']
        assert [x[0] for x in candidate.dependency_projection_epochs]==dependency_ids
        assert m.epistemic_projections.is_current('P-MS1989-C',record.epoch)

        # F was in the search/evaluation basis but was not selected by C.
        m.epistemic_projections.change('P-MS1989-F',new_signature_sha256='9'*64)
        after_unused=m.epistemic_projections.records['P-MS1989-C']
        assert after_unused.current
        assert m.epistemic_projections.is_current('P-MS1989-C',after_unused.epoch)

        # C remains exactly evaluable from selected A+B even though old F basis content is stale.
        composed=m.derive_admitted_projection_samples_from_owned_projection_buckets(
            max_source_projections=4,max_projection_depth=1,
        )
        assert composed['status']=='ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES',composed
        assert 'P-MS1989-C' in composed['source_projection_ids']
        assert ('P-MS1989-F','SOURCE_PROJECTION_CONTENT_NOT_EXACTLY_RECOVERABLE') in composed['source_rejections']

        # An actual selected dependency still fails closed.
        m.epistemic_projections.change('P-MS1989-A',new_signature_sha256='a'*64)
        after_selected=m.epistemic_projections.records['P-MS1989-C']
        assert not after_selected.current
        assert not m.epistemic_projections.is_current('P-MS1989-C',after_selected.epoch)

        return {
            'status':'PASS',
            'candidate_input_positions':list(candidate.input_positions),
            'full_basis_ids':basis_ids,
            'selected_dependency_ids':dependency_ids,
            'unused_source_changed':'P-MS1989-F',
            'C_current_after_unused_source_change':True,
            'C_evaluable_after_unused_source_change':True,
            'selected_source_changed':'P-MS1989-A',
            'C_stale_after_selected_source_change':True,
            'basis_ancestry_preserved':True,
            'legacy_behavior':'EMPTY_DEPENDENCY_LINEAGE_FALLS_BACK_TO_FULL_SOURCE_BASIS',
            'earned':'SELECTED_SOURCE_DEPENDENCY_LINEAGE_CAN_GOVERN_CURRENTNESS_AND_RECURSIVE_EVALUATION_WHILE_FULL_SOURCE_BASIS_REMAINS_SIGNED_PROVENANCE',
            'semantic_feature_authority':'NONE','truth_authority':'NONE','language_authority':'NONE',
        }
    finally:
        _close(m); world.close(); td.cleanup()


def main() -> None:
    print(json.dumps(run_ms1989(),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
