# Substrate Hardening V1 — B/C Bucket-Scoped Currentness V2

Status: VERIFIED DEFECT V2 / REPAIR V1 DEMOTED / NO PROMOTION

## Why V1 was not accepted
Repair V1 passed 4/4 routing hostiles, 2/2 nested hostiles, 69/69 focused lineage, and a 983/983 whole suite. Exact-delta hostile review nevertheless found that its reconstructed descendant evidence was binding+relation-specific, not selected-bucket-specific.

## V2 hostile
The same qualified predictive relation is routed through two qualified projection buckets. Bucket A receives 16 consistently wrong post-binding outcomes. Bucket B receives 48 correct outcomes, interleaved 3:1.

Observed:
- bad bucket alone: `[0.0, 0.0] -> DRIFT_WITNESS`;
- repair-V1 pooled view: eight `[0.75]` windows -> `CURRENT_WITHIN_BOUNDS`;
- routing remains `CURRENT_PROJECTION_CONDITIONED_ROUTING`.

Therefore another bucket can mask a genuinely stale scoped law.

## Root cause
`CounterfactualRehearsalProposal` persists relation digests and evidence ancestry but not `projection_routing_id` or selected `projection_bucket_id`. Routing qualification evidence makes a relation digest binding-specific but not bucket-specific.

## Required repair property
Persist exact routed-selection ancestry on the existing proposal lineage and assess each qualified bucket/action relation independently. Failing the entire binding closed when one bucket drifts is acceptable. Pooling other buckets to keep it current is not.

## Process scar
`WHOLE_SUITE_GREEN != HARDENING_COMPLETE`. Repair V1 remains preserved as a failed repair candidate rather than overwritten.
