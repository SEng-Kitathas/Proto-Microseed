from pathlib import Path
import hashlib, random, tempfile

from microseed import (
    Microseed, Authority, QualificationState, OperationalFrameContract,
    ProjectionSample, ProjectionDiscoveryConfig,
)


def H(x): return hashlib.sha256(str(x).encode()).hexdigest()


def new_ms():
    td=tempfile.TemporaryDirectory(prefix='microseed-ms2059-factorization-')
    m=Microseed(Path(td.name))
    m.register_operational_frame(OperationalFrameContract(
        frame_id='F',purpose='opaque-factorized-request-effect-boundary',signature_sha256=H('ms2059-frame'),
        authority=Authority.DERIVED_READ_ONLY,lineage=('MS2059-RESEARCH',),currentness='CURRENT',
        qualification=QualificationState.SHADOW_QUALIFIED,
        assistance_ancestry=('EXTERNAL_FRAME_QUALIFICATION',),
        invariants=('NO_SEMANTIC_PARENT_CHILD_AUTHORITY','NO_SEMANTIC_COORDINATE_AUTHORITY'),
    ))
    return td,m


def world_rows(seed, *, n=1600, permutation=(0,1,2,3), omit_subordinate=False):
    rng=random.Random(seed); out=[]
    for i in range(n):
        higher=rng.randint(0,1)
        subordinate=rng.randint(0,1)
        nuisance_a=rng.randint(0,7)
        nuisance_b=rng.randint(0,7)
        action='U1' if rng.random()<.5 else 'U2'
        desired_request = higher ^ subordinate
        chosen = 0 if action=='U1' else 1
        effect='POS' if chosen==desired_request else 'NEG'
        logical=[f'H{higher}',f'S{subordinate}',f'N{nuisance_a}',f'M{nuisance_b}']
        if omit_subordinate:
            logical[1]='S-UNOBSERVED'
        raw=tuple(logical[j] for j in permutation)
        out.append(ProjectionSample(
            f'R-{seed}-{i}',raw,action,effect,f'SCOPE-{i%4}','F',0
        ))
    relevant_positions=tuple(sorted((permutation.index(0),permutation.index(1))))
    return out,relevant_positions


def discover(m,rows, *, max_subset=2):
    cut=1100
    cfg=ProjectionDiscoveryConfig(
        max_subset=max_subset,min_train_support=100,min_key_action_support=8,
        min_validation_accuracy=.95,min_lift_over_action_baseline=.35,min_scope_accuracy=.90,
        complexity_penalty=.008,max_candidates=8,
    )
    return m.discover_epistemic_projection_candidates(rows[:cut],rows[cut:],cfg)


def test_factorized_higher_and_subordinate_state_are_discovered_without_semantic_labels():
    td,m=new_ms()
    try:
        rows,relevant=world_rows(2059,permutation=(2,0,3,1))
        found=discover(m,rows)
        assert found
        best=m.epistemic_projection_candidates[found[0]['candidate_id']]
        assert best.input_positions==relevant
        assert best.validation_accuracy>=.99
        assert best.lift>=.45
        assert best.semantic_projection_authority=='NONE' and best.truth_authority=='NONE'
        assert all('PARENT' not in x and 'CHILD' not in x for x in best.assistance_ancestry)
    finally: td.cleanup()


def test_unary_context_cannot_solve_joint_higher_x_subordinate_request_effect():
    td,m=new_ms()
    try:
        rows,_=world_rows(2060,permutation=(1,3,0,2))
        assert discover(m,rows,max_subset=1)==[]
        assert discover(m,rows,max_subset=2)
    finally: td.cleanup()


def test_coordinate_permutation_does_not_change_which_latent_factors_are_selected():
    for seed,perm in enumerate(((0,1,2,3),(3,2,1,0),(1,3,0,2),(2,0,3,1)),start=2100):
        td,m=new_ms()
        try:
            rows,relevant=world_rows(seed,permutation=perm)
            found=discover(m,rows)
            assert found
            best=m.epistemic_projection_candidates[found[0]['candidate_id']]
            assert best.input_positions==relevant
            assert best.validation_accuracy>=.99
        finally: td.cleanup()


def test_nuisance_variation_generalizes_because_nuisance_coordinates_are_not_selected():
    td,m=new_ms()
    try:
        # Training/validation have broad independently varying nuisance values. The selected
        # two-coordinate partition must ignore both nuisance positions.
        rows,relevant=world_rows(2200,permutation=(3,0,1,2),n=2200)
        found=discover(m,rows)
        assert found
        best=m.epistemic_projection_candidates[found[0]['candidate_id']]
        assert best.input_positions==relevant
        nuisance=set(range(4))-set(relevant)
        assert nuisance.isdisjoint(best.input_positions)
        # Two raw observations that differ only in nuisance project to the same bucket.
        a=['H0','S1','N0','M0']; b=['H0','S1','N7','M7']
        pa=tuple(a[j] for j in (3,0,1,2)); pb=tuple(b[j] for j in (3,0,1,2))
        assert best.project(pa)==best.project(pb)
    finally: td.cleanup()


def test_hiding_subordinate_current_state_makes_relation_unidentifiable_and_returns_no_candidate():
    td,m=new_ms()
    try:
        rows,_=world_rows(2300,permutation=(2,0,3,1),omit_subordinate=True)
        assert discover(m,rows,max_subset=2)==[]
    finally: td.cleanup()


def test_projection_is_predictive_factorization_not_role_topology_or_execution_authority():
    td,m=new_ms()
    try:
        rows,_=world_rows(2400,permutation=(2,0,3,1))
        found=discover(m,rows); assert found
        c=m.epistemic_projection_candidates[found[0]['candidate_id']]
        assert c.proposal_authority=='NONE'
        assert c.qualification_authority=='NONE'
        assert c.semantic_projection_authority=='NONE'
        assert c.truth_authority=='NONE'
        assert not hasattr(m,'parent_child_topology')
        assert not hasattr(m,'hierarchy_manager')
        # Projection candidate cannot itself execute or qualify anything.
        assert c.candidate_id not in m.epistemic_projections.records
    finally: td.cleanup()
