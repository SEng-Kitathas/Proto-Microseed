# MS1990 Source-Count Scaling Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1990**.
- Commit: `3dc6fb7655d0be3633df917a962126f69054144d`.
- Tree: `4ff5bfa26e2a9a24d850be559acde363651a1a4a`.
- Source/test snapshot: `17599a8441a596f9873f4ce697ee688763d4e142f07b42e5af2a85d4790d686b` / 315 Python files.
- Worktree clean at seal.
- GitHub `refs/heads/research/ms1888-replay`: remote readback exactly matched the seal.
- `origin/main`: unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
The owned projection-bucket bridge had a hard API validation: `1 <= max_source_projections <= 16`.

MS1990 built 17 exact current/evaluable opaque sources. Under published MS1989:
- ceiling 16 -> `DEFER_UNKNOWN`, compatible count 17;
- ceiling 17 -> rejected by local validation before the bridge could emit the lawful vector.

The same 17-column opaque vector fed to the unchanged projection learner produced:
- one-source candidates 0;
- exact useful pair `(0,16)`;
- validation 1.0;
- lift 0.5.

Therefore 17 sources did not prove a missing learner or source-selection mechanism. The immediate blocker was an arbitrary local cap.

## Embodiment
Changed only `microseed/runtime/entity.py` source-count validation:
- old: positive and <=16;
- new: positive explicit source-count ceiling.

Unchanged:
- default 8;
- compatible count above supplied ceiling -> `DEFER_UNKNOWN`;
- never truncate;
- caller never supplies source IDs;
- exact/current/evaluable source requirements;
- separate recursive depth bound 0..8;
- ephemeral samples;
- semantic/truth/language authority NONE.

## Positive pressure
17 sources:
- ceiling 16 -> defer;
- ceiling 17 -> vector width 17;
- one-source 0;
- exact pair `(0,16)`;
- validation 1.0; lift 0.5.

32 sources:
- ceiling 31 -> defer;
- ceiling 32 -> vector width 32;
- one-source 0;
- exact pair `(0,31)`;
- validation 1.0; lift 0.5.

No new learner or source-selection policy.

Earned:
`EXPLICIT_POSITIVE_SOURCE_COUNT_CEILINGS_CAN_SCALE_BEYOND_16_WHILE_PRESERVING_NO_TRUNCATION_AND_EXISTING_PROJECTION_SEARCH`.

## Verification
- focused cleanup-neutral `job-6dd082eed6e3`: **18/18 PASS in 158.59s**;
- whole cleanup-neutral `job-f8ebbe85d740`: **786/786 PASS in 490.79s**;
- whole stderr empty;
- self-test 81/81 PASS;
- compileall PASS;
- `git diff --check` PASS.

## Interpretation
MS1990 is a scaling correction, not a new cognitive faculty. The evidence rejects the claim that crossing 16 compatible sources alone earns semantic attention or a family-selection manager.

## Next pressure
Measure combinatorial subset-search cost as source count and subset arity grow. Determine whether the next missing mechanism is merely an explicit computational budget with exact refusal, or whether a lawful source-family nomination mechanism is eventually required.

Prewrites:
- `SEARCH_COST != SEMANTIC_ATTENTION`;
- `BUDGET_EXHAUSTION != PERMISSION_TO_TRUNCATE`;
- `COMBINATORIAL_PRESSURE != MISSING_REPRESENTATION_LEARNER`.