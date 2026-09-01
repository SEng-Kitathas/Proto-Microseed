# MS2064 — Promotion Review Projection Snapshot Repair

## Trigger
Promotion review of the MS2062+MS2063 production candidate inspected the exact two-file production delta rather than relying on green test counts.

The review found a latent code defect introduced during MS2062: a broad text replacement changed `EpistemicDeficitRegistry.snapshot()` to reference `self.capability_dependents`, which that registry does not own. The intended metadata belonged to `EpistemicProjectionRegistry.snapshot()`, whose own snapshot remained unchanged.

The 970-test MS2063 whole suite did not exercise either snapshot surface strongly enough to expose the error.

## Classification
`WHOLE_SUITE_GREEN != PROMOTION_REVIEW_COMPLETE`.

`WRONG_REGISTRY_SNAPSHOT_PATCH__LATENT_PRODUCTION_DEFECT_FOUND_BY_EXACT_DELTA_REVIEW`.

This blocks promotion until repaired and re-verified.

## Repair
- restore `EpistemicDeficitRegistry.snapshot()` to its pre-MS2062 pure record serialization;
- add `capability_dependents` only to `EpistemicProjectionRegistry.snapshot()`;
- add direct regression tests for both registries.

No hierarchy semantics, authority, currentness rule, or request-specialization behavior changes.

## Pre-whole verification
- focused direct snapshot guards: **3/3 PASS in 0.45s**;
- broader hierarchy/projection/currentness guard: **102/102 PASS in 131.61s**;
- stderr empty;
- production delta is exactly `microseed/development/epistemic.py` relative to the MS2063 evidence head, and the effective production candidate remains the MS2062 two-file carrier plus this one-lineage snapshot correction.

Whole cleanup-neutral regression remains required before promotion review can resume.

## Pre-whole-suite verification
- Directly affected MS2062 + MS2063 + MS2064 surfaces: **16/16 PASS in 46.34s**.
- Broader historical-owner + P1A/N1A + MS2057-MS2064 guard: **102/102 PASS in 131.84s**.
- stderr empty in both runs.

Promotion remains blocked until the repaired committed head passes an authoritative cleanup-neutral whole suite.
