# MS1987 Recursive Opaque Composition Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1987**.
- Commit: `d34a3491d412c154f525eedebafe624a18537b3f`.
- Tree: `2c65c607b1c33a36e45d86ad246042e2fe31dd4f`.
- Source/test snapshot: `32699ce3ff93cca2f711f14179de35255ffdbb206eb90d3efc05ac9c316760d6` / 312 Python files.
- Worktree clean.
- GitHub `refs/heads/research/ms1888-replay`: remote readback exactly matched the seal.
- `origin/main`: unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
MS1986 could apply direct learned projections to owned raw rows, but a composed projection C expects a vector of learned buckets rather than original raw tokens.

Six-bit process pressure:
- A = parity raw `(0,1)`;
- B = parity raw `(2,3)`;
- D = parity raw `(4,5)`;
- C = whether A and B agree;
- E = whether C and D agree.

Before recursive evaluation, C was current but rejected by the owned bucket bridge and A/B/D produced zero max-subset-2 E candidates.

Missing mechanism localized to:
`CURRENT_COMPOSED_PROJECTION_RECURSIVE_EVALUATION_OVER_OWNED_RAW_SAMPLE`.

## Embodiment
Added bounded private evaluator:
`_evaluate_current_projection_bucket_from_owned_raw_sample(...)`.

It follows exact current source-projection `(id, epoch, signature)` ancestry, recurses only under a supplied depth ceiling, requires exact candidate content and current frame ancestry, and returns only an opaque bucket.

The existing bridge now accepts `max_projection_depth` in addition to `max_source_projections`.

Caller supplies ceilings only; no source IDs, bucket values, semantic labels, or hand-built path.

## Result
Depth 0:
- source set A/B/D;
- C refused with `SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND`;
- depth-3 candidate count 0.

Depth 1:
- source set A/B/C/D;
- one-source candidates 0;
- exact C+D positions `(2,3)` found;
- validation 1.0;
- lift 0.59375;
- external holdouts 64/64.

Earned:
`CURRENT_COMPOSED_OPAQUE_PROJECTIONS_CAN_BE_RECURSIVELY_EVALUATED_THROUGH_EXACT_SOURCE_LINEAGE_AND_REUSED_AS_INPUTS_TO_EXISTING_PROJECTION_SEARCH_AT_ONE_ADDITIONAL_DEPTH`.

No new projection learner or representation manager was added.

## Hostiles
- explicit depth 0 blocks C;
- missing C candidate content refuses C rather than guessing;
- C change stales E;
- A change stales the current C generation;
- sample persistence NONE;
- semantic recursion/symbol/truth/language authority NONE.

## Verification
Direct focused pytest: 21 pass + 12 cleanup-only Windows file-lock failures on `biography.sqlite3`; no mechanism assertion failed.

Cleanup-neutral focused:
- `job-4b9142b4e2a1` -> **33/33 PASS in 87.52s**.

Whole cleanup-neutral:
- `job-bae9757b4785` -> **776/776 PASS in 380.52s**;
- stderr empty.

Self-test: 81/81 PASS.
compileall: PASS.
`git diff --check`: PASS.

## Lineage precision note
Current projection candidates carry the full ordered source-vector ancestry used to form generated samples, even when their selected `input_positions` use only part of that vector. This is safe but conservative: it can over-stale a dependent if an unused source coordinate changes.

Do not describe current lineage as minimal causal dependency lineage.

## Next pressure
P0: depth-4 genericity with one more chain level under the same evaluator, ideally with no core change:
`A+B -> C`, `C+D -> E`, `E+F -> G`.

Depth 1 should not expose E; depth 2 should expose E and allow E+F to predict G.

P1: test whether conservative full-vector lineage creates enough false staleness to justify a separate minimal dependency/basis distinction.