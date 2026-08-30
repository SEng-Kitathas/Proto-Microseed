# MS1991 — Explicit Projection-Search Budget Completeness

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1990 `3dc6fb7655d0be3633df917a962126f69054144d`

## Question
Once wider learned-source vectors are lawful, how should projection discovery behave when exhaustive subset enumeration is too expensive for a supplied compute budget?

The failure to prevent is simple:

`SEARCH_BUDGET_EXHAUSTED != NO_PREDICTIVE_PARTITION`.

A partial search must never be returned as if it proved exhaustive absence.

Prewrites:
- `PARTIAL_ENUMERATION != EXHAUSTIVE_SEARCH`;
- `COMPUTATIONAL_BUDGET != SEMANTIC_ATTENTION`;
- `SEARCH_ORDER != FEATURE_IMPORTANCE`;
- `BUDGET_EXHAUSTION != PERMISSION_TO_TRUNCATE`.

## Existing search behavior
`discover_epistemic_projection_candidates(...)` enumerates coordinate subsets deterministically:
1. ascending subset size;
2. lexicographic position order within each size.

For dimension N and supplied max subset arity K, the exact number of subset fits is known before search:

`sum(C(N,k), k=1..min(N,K))`.

Examples:
- N=32, K=2 -> 528;
- N=64, K=3 -> 43,744;
- N=128, K=4 -> 11,017,632.

The legacy API is exhaustive and returns a bare list. It has no partial-search mode and therefore no completeness metadata.

## Minimum embodiment
Added a new Microseed method:

`discover_epistemic_projection_candidates_with_budget(...)`.

The legacy `discover_epistemic_projection_candidates(...)` list API is unchanged.

The new bounded method:
1. validates a positive explicit `max_subset_evaluations` budget;
2. checks sample frame currentness under the same operational boundary;
3. computes the exact deterministic subset count before fitting any subset;
4. if required count exceeds budget, returns `DEFER_UNKNOWN` with reason `PROJECTION_SEARCH_SUBSET_EVALUATION_BUDGET_INSUFFICIENT`;
5. performs **zero** subset fits in that case;
6. nominates/persists no partial candidates;
7. if budget covers the full search, calls the unchanged exhaustive learner;
8. reports exact required/performed subset counts and `search_complete=True`.

This is preflight refusal, not partial truncation.

No source IDs are supplied. No feature importance ranking is inferred from search order. No semantic attention policy is added.

## Late-candidate boundary
Scratch:
`scratch/ms1991_projection_search_budget_boundary.py`.

A 32-coordinate opaque world is constructed so:
- no one coordinate predicts the target;
- the unique useful pair is positions `(30,31)`;
- `(30,31)` is the final pair in deterministic size-2 lexicographic enumeration;
- exhaustive max-subset-2 search therefore requires 528 subset fits.

### Budget 527
Result:
- status `DEFER_UNKNOWN`;
- reason `PROJECTION_SEARCH_SUBSET_EVALUATION_BUDGET_INSUFFICIENT`;
- required subset evaluations 528;
- performed subset evaluations 0;
- candidate count 0;
- no candidate persistence;
- search complete false.

The system does not search the first 527 subsets and pretend the late candidate does not exist.

### Budget 528
Result:
- status `EXHAUSTIVE_PROJECTION_SEARCH_COMPLETED`;
- required/performed evaluations 528/528;
- exact late pair `(30,31)` found;
- validation 1.0;
- lift 0.5.

Candidate ID and digest exactly match the unchanged legacy exhaustive constructor.

Earned candidate statement:

`EXPLICIT_SUBSET_EVALUATION_BUDGET_CAN_FAIL_CLOSED_BEFORE_PARTIAL_PROJECTION_SEARCH_AND_PRESERVE_EXHAUSTIVE_CANDIDATE_IDENTITY_WHEN_SUFFICIENT`.

## Large-space preflight hostile
A 128-coordinate, max-subset-4 request has an exact search requirement of 11,017,632 subset fits.

A budget of 1,000,000 must:
- return `DEFER_UNKNOWN`;
- report required count 11,017,632;
- perform zero subset fits;
- persist no candidates.

This verifies that the cost wall can be detected cheaply before expensive search begins.

## Why this is not attention
The mechanism answers only:

> Can the supplied compute budget cover the exact search grammar the caller already authorized?

It does not answer:
- which sources are important;
- which concepts matter;
- what the organism should attend to;
- which source family should be preferred.

Those remain separate developmental questions.

## Authority ceiling
- compute-budget authority: supplied positive subset-evaluation ceiling only;
- search grammar: existing bounded max subset arity;
- search order: deterministic implementation order, not semantic importance;
- source nomination: NONE;
- semantic attention/feature authority: NONE;
- truth authority: NONE;
- language authority: NONE.

## Final verification
- focused cleanup-neutral MS1986–MS1991: `job-722229643c67` -> **21/21 PASS in 159.61s**;
- whole cleanup-neutral embodiment suite: `job-6c15c895fe2e` -> **789/789 PASS in 514.77s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
