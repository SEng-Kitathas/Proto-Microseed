# MS1990 — Explicit Source-Count Scaling Beyond 16

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1989 `c6563464e92a266aaafb734520d75a590d8cadd9`

## Question
After MS1989 narrowed operational dependency lineage, the next apparent scaling seam was the owned projection-bucket bridge's hard `max_source_projections <= 16` rule.

Does source count 17 demonstrate a missing source-selection mechanism, or is the existing bridge/learner already adequate once the artificial local cap is removed?

Prewrites:
- `TOO_MANY_COMPATIBLE_SOURCES != PERMISSION_TO_TRUNCATE`;
- `SOURCE_FAMILY_SEARCH != SEMANTIC_FEATURE_SELECTION`;
- `MISSING_SCALING_PATH != MISSING_PROJECTION_LEARNER`;
- `ARBITRARY_LOCAL_CAP != MISSING_COGNITIVE_MECHANISM`.

## Boundary before mutation
Scratch boundary:
`scratch/ms1990_source_family_scaling_boundary.py`.

Constructed 17 exact current/evaluable direct opaque projections with deterministic lexicographic IDs. No source IDs were supplied to the bridge.

Target outcome was designed so:
- no one source predicts it;
- the unique useful pair is source positions `(0,16)`;
- nuisance source pairs cannot reproduce the target relation.

Observed under published-MS1989 behavior:
- `max_source_projections=16` -> `DEFER_UNKNOWN`;
- reason -> `COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND`;
- compatible count -> 17;
- `max_source_projections=17` -> `ValueError: BOUNDED_SOURCE_PROJECTION_COUNT_REQUIRED` because of the local hard `>16` validation.

Separately, the exact same lawful 17-column opaque bucket vector was passed to the unchanged projection learner:
- one-source candidates: 0;
- exact useful pair: `(0,16)`;
- validation accuracy: 1.0;
- lift: 0.5.

Therefore the projection learner was not missing. The immediate blocker was the fixed 16 limit in the bridge API.

## Audit of the old fixed cap
The bridge already evaluates all current projection records and their buckets before it compares compatible count to the caller's supplied ceiling.

Therefore the fixed `<=16` validation was not the primary gate on source-evaluation work. It only prevented a caller from explicitly permitting a wider finite output vector.

The caller-supplied `max_source_projections` itself is already an explicit finite count ceiling.

## Minimum embodiment
Changed only the local source-count validation in:
`microseed/runtime/entity.py`.

Old:
`1 <= max_source_projections <= 16`.

New:
`max_source_projections >= 1`.

The API still requires a positive explicit finite integer ceiling.

Unchanged safety behavior:
- default remains 8;
- if actual compatible source count exceeds the supplied ceiling, return `DEFER_UNKNOWN`;
- never truncate lexicographically;
- never let caller supply source IDs;
- source projections still must be exact/current/evaluable;
- recursive depth remains separately bounded 0..8;
- samples remain ephemeral;
- no semantic/truth/language authority is added.

## Positive pressure after repair
The scratch campaign now runs exact bridge-to-learner cases at 17 and 32 compatible current projections.

### 17-source case
With ceiling 16:
- `DEFER_UNKNOWN`;
- reason `COMPATIBLE_SOURCE_PROJECTION_COUNT_EXCEEDS_BOUND`.

With ceiling 17:
- bridge emits `ADMITTED_OWNED_PROJECTION_BUCKET_SAMPLES`;
- vector width 17;
- one-source candidates 0;
- exact pair `(0,16)`;
- validation 1.0;
- lift 0.5;
- selected dependency IDs are first + last source.

### 32-source case
With ceiling 31:
- `DEFER_UNKNOWN`.

With ceiling 32:
- bridge emits vector width 32;
- one-source candidates 0;
- exact pair `(0,31)`;
- validation 1.0;
- lift 0.5.

The existing projection learner is unchanged in both cases.

## What MS1990 earns
`EXPLICIT_POSITIVE_SOURCE_COUNT_CEILINGS_CAN_SCALE_BEYOND_16_WHILE_PRESERVING_NO_TRUNCATION_AND_EXISTING_PROJECTION_SEARCH`

This is a scaling correction, not a new cognitive faculty.

The evidence specifically rejects the claim that 17 sources alone earns a source-family selection mechanism.

## What remains open
Removing the arbitrary hard cap does not solve all future source-family scaling.

At sufficiently large source counts, exhaustive downstream subset search can become expensive. That future boundary should be pressure-tested by measured combinatorial cost before adding family-selection policy.

Possible later seam:
- bounded computational budget over source-subset search;
- exact refusal if exhaustive search would exceed budget;
- no semantic attention/feature policy unless separately earned.

MS1990 does **not** implement that mechanism because current 17/32 evidence does not require it.

## Authority ceiling
- caller supplies count ceiling only, not source identities;
- source order remains deterministic opaque projection-ID order;
- no lexicographic truncation;
- no semantic feature selection;
- no concept/attention manager;
- truth authority NONE;
- language authority NONE.

## Verification so far
- focused cleanup-neutral MS1986–MS1990: `job-6dd082eed6e3` -> **18/18 PASS in 158.59s**;
- focused stderr empty;
- compileall: PASS;
- self-test: **81/81 PASS**.

## Final verification
- focused cleanup-neutral MS1986–MS1990: `job-6dd082eed6e3` -> **18/18 PASS in 158.59s**;
- whole cleanup-neutral embodiment suite: `job-f8ebbe85d740` -> **786/786 PASS in 490.79s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
