# MS1989 Selected Dependency Lineage Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1989**.
- Commit: `c6563464e92a266aaafb734520d75a590d8cadd9`.
- Tree: `5a9279f41964c1ded654c3401163c3aa728ffa21`.
- Source/test snapshot: `cd1d4e7c421c2af6ba6b1ea3541895c386229f21026105a624ce83c681724148` / 314 Python files.
- Worktree clean at seal.
- GitHub `refs/heads/research/ms1888-replay`: remote readback exactly matched the seal.
- `origin/main`: unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
Sealed MS1988 used full source-vector ancestry for currentness. A C projection discovered from A/B/D/F but selecting only A+B became stale when unused F changed.

Detached exact-MS1988 registry witness:
- C current before F change: true;
- C current after unused F change: false.

This proved real false staleness.

## Embodiment
MS1989 separates:
- `source_projection_epochs` = full evaluation/search basis provenance;
- `dependency_projection_epochs` = operational dependencies derived from source basis positions selected by `candidate.input_positions`.

The caller does not independently nominate the dependency set.

Full basis is still required to be exact/current at admission. After admission, currentness/invalidation/recursive evaluation follow selected dependencies for new records. Legacy records with empty selected dependency lineage retain conservative full-basis behavior.

Candidate identity remains compatible because selected dependencies are already determined by signed source basis + input positions.

Exact compatibility witness against sealed MS1988:
- candidate ID `proj-cand-659ab3b00df7224f5100`;
- digest `6c19bb59464942b716d607e65d4c1f838076056519de9407521f756338632d21`;
- identical before/after MS1989.

## Process pressure
C learned from A+B inside A/B/D/F basis.
- change unused F: C remains current and evaluable;
- change selected A: C stales;
- full basis provenance remains stored;
- stale full-basis source content is not recursively evaluated when unselected.

Earned:
`SELECTED_SOURCE_DEPENDENCY_LINEAGE_CAN_GOVERN_CURRENTNESS_AND_RECURSIVE_EVALUATION_WHILE_FULL_SOURCE_BASIS_REMAINS_EXACT_PROVENANCE`.

## Verification
- focused cleanup-neutral MS1986–MS1989: `job-65a991fc8b11` -> **16/16 PASS in 188.78s**;
- whole cleanup-neutral: `job-e0d362e00fab` -> **784/784 PASS in 501.40s**;
- stderr empty;
- self-test **81/81 PASS**;
- compileall PASS;
- `git diff --check` PASS.

## Authority ceiling
- selected dependency != semantic cause;
- selected coordinate != semantic feature;
- truth/language/semantic authority NONE;
- no source-selection policy added;
- no manager added.

## Next pressure
MS1990: reproduce the source-family scaling boundary. The owned projection-bucket bridge admits at most 16 compatible current projections. With 17 compatible sources it must fail safely today. Determine whether the next missing owner is truly bounded source-family search, or whether a smaller existing-surface composition solves it.