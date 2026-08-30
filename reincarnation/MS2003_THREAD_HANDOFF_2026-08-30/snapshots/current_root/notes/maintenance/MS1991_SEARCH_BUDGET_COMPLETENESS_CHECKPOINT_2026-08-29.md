# MS1991 Search-Budget Completeness Checkpoint — 2026-08-29

## Seal / publication
- Technical milestone: **MS1991**.
- Commit: `75b794011514c2d686f1d92e840b5c5d62a8c9f7`.
- Tree: `572a9a1e7e8cde557ecc74305847b7c8e6cbce3a`.
- Source/test snapshot: `827ca64f816d38d97b542474b402487697a63bf8d5d954f7a2f9fb0cadf47347` / 316 Python files.
- Worktree clean at seal.
- GitHub research ref remote readback exactly matched the seal.
- `origin/main` unchanged at `3473834da0ce1bbc0db16a35f4b9b8e2fa551ee2`.
- Canonical Main-Dev remains MS1527.

## Boundary
Projection search enumerates subsets in deterministic order: ascending size, then lexicographic positions. Before MS1991 it had only an exhaustive list-returning API.

At wider source counts, finite compute creates a dangerous ambiguity if partial search is ever introduced:
`SEARCH_BUDGET_EXHAUSTED != NO_PREDICTIVE_PARTITION`.

Exact subset counts are known before fitting:
- N32 K2 -> 528;
- N64 K3 -> 43,744;
- N128 K4 -> 11,017,632.

## Embodiment
Added `Microseed.discover_epistemic_projection_candidates_with_budget(...)`.

The legacy exhaustive list API is unchanged.

The bounded API:
- requires positive explicit subset-evaluation budget;
- computes exact exhaustive subset count before fitting;
- if budget is insufficient, returns `DEFER_UNKNOWN` with `PROJECTION_SEARCH_SUBSET_EVALUATION_BUDGET_INSUFFICIENT`;
- performs zero subset fits and persists no candidates on that path;
- if budget is sufficient, runs the unchanged exhaustive learner;
- reports required/performed counts and `search_complete=True`.

No partial truncation, source-ID nomination, or semantic attention.

## Late-candidate pressure
32 opaque coordinates, max subset 2. Unique useful pair is `(30,31)`, the final size-2 pair in deterministic enumeration.

Budget 527:
- DEFER_UNKNOWN;
- required 528;
- performed 0;
- no candidates persisted.

Budget 528:
- exhaustive completed;
- exact `(30,31)` found;
- validation 1.0;
- lift 0.5;
- candidate ID/digest exactly matches legacy exhaustive constructor.

Large-space hostile:
- N128 K4 requires 11,017,632 fits;
- budget 1,000,000 defers before any fit.

Earned:
`EXPLICIT_SUBSET_EVALUATION_BUDGET_CAN_FAIL_CLOSED_BEFORE_PARTIAL_PROJECTION_SEARCH_AND_PRESERVE_EXHAUSTIVE_CANDIDATE_IDENTITY_WHEN_SUFFICIENT`.

## Verification
- focused cleanup-neutral `job-722229643c67`: **21/21 PASS in 159.61s**;
- whole cleanup-neutral `job-6c15c895fe2e`: **789/789 PASS in 514.77s**;
- whole stderr empty;
- self-test 81/81 PASS;
- compileall PASS;
- diff-check PASS.

## Interpretation
MS1991 adds explicit epistemic honesty about finite compute. It does not add attention, source importance, or semantic selection.

## Next pressure
With source-count and search-completeness scaling now explicit, return to a larger prelingual seam: first-probe information buying under genuine uncertainty. Audit existing equipped intervention/warrant machinery before adding any NAKED exploratory faculty.