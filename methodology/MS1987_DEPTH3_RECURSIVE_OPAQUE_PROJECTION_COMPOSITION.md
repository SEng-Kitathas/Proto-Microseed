# MS1987 — Depth-3 Recursive Opaque Projection Composition

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent branch HEAD: `e0c948d32c006d21ad4a867d6f5941c75d7208f7`
Latest technical parent: MS1986 `383196060c0bb88980a2e22b972972a4e09f58a5`

## Question
Can a projection learned from other learned opaque projections become a lawful source for one more projection-learning step without adding a new learner or representation manager?

Target structure:

`A + B -> C`

then

`C + D -> E`

with C alone insufficient, D alone insufficient, and C+D predictive.

Prewrites:
- `RECURSIVE_OPAQUE_REPRESENTATION_COMPOSITION != SEMANTIC_RECURSION`;
- `DEPENDENCY_DEPTH != CONCEPT_HIERARCHY`;
- `OPAQUE_BUCKET_OF_BUCKET != SEMANTIC_SYMBOL`;
- `TRANSITIVE_CURRENTNESS_REQUIRED_FOR_RECURSIVE_COMPOSITION`.

## Boundary before mutation
MS1986's owned bucket bridge applied every current admitted source candidate directly to the original raw row.

That was correct for first-stage projections A/B/D, but not for composed projection C. C was learned over a vector of source buckets. Its `project(...)` method therefore expects those opaque bucket values, not the original raw coordinates.

A six-bit process world reproduced the boundary:
- A learns parity over raw positions `(0,1)`;
- B learns parity over `(2,3)`;
- D learns parity over `(4,5)`;
- C learns whether A and B agree;
- E depends on whether C agrees with D.

Before the recursive evaluator:
- C was current;
- bridge sources were A/B/D only;
- C was rejected as `SOURCE_PROJECTION_DOES_NOT_COVER_ALL_BASE_SAMPLES`;
- 128 owned E samples were available;
- max-subset-2 search over A/B/D produced zero depth-3 candidates.

This localized one missing mechanism:
`CURRENT_COMPOSED_PROJECTION_RECURSIVE_EVALUATION_OVER_OWNED_RAW_SAMPLE`.

The projection learner itself was not missing.

## Minimum embodiment
Added a private bounded evaluator:

`_evaluate_current_projection_bucket_from_owned_raw_sample(...)`

The evaluator:
1. starts from a current admitted projection record;
2. requires exact nominated candidate content by record signature;
3. requires current frame ancestry and compatibility with the owned base sample;
4. for a direct projection, applies the candidate to the owned raw row;
5. for a composed projection, follows the record's exact source-projection `(id, epoch, signature)` ancestry;
6. recursively evaluates those sources over the same owned raw row;
7. passes the resulting opaque bucket vector into the composed candidate's existing `project(...)` method;
8. stops at an explicit supplied recursion-depth ceiling;
9. refuses missing candidate content, stale ancestry, cycles, frame mismatch, uncovered raw rows, or uncovered derived bucket vectors;
10. persists nothing and grants no semantic or truth authority.

The existing bridge now accepts:
- `max_source_projections`;
- `max_projection_depth`.

The caller still supplies only ceilings. The caller does not supply source IDs, per-sample bucket values, semantic labels, or a hand-built recursive path.

## Process result
Separate process:
`research/substrate_shadow/recursive_bucket_composition_world_server.py`.

Scratch embodiment:
`scratch/ms1987_depth3_recursive_bucket_composition.py`.

The same experiment checks both sides of the boundary.

### Depth ceiling 0
- available sources: A/B/D;
- C rejected: `SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND`;
- E samples: 128;
- max-subset-2 depth-3 candidates: 0.

### Depth ceiling 1
- available sources: A/B/C/D;
- one-source search: 0 candidates;
- max-subset-2 finds exact positions `(2,3)`, which are C+D in lexicographic source order;
- validation accuracy: 1.0;
- lift: 0.59375;
- external process holdouts: 64/64.

Earned candidate statement:

`CURRENT_COMPOSED_OPAQUE_PROJECTIONS_CAN_BE_RECURSIVELY_EVALUATED_THROUGH_EXACT_SOURCE_LINEAGE_AND_REUSED_AS_INPUTS_TO_EXISTING_PROJECTION_SEARCH_AT_ONE_ADDITIONAL_DEPTH`

## Hostile checks inside the process embodiment
- depth 0 refuses composed C;
- depth 1 evaluates C;
- missing exact C candidate content removes C from the compatible source set rather than guessing;
- C change stales admitted E;
- A change stales the current C generation;
- generated samples remain ephemeral;
- no new projection-search mechanism was added;
- no new representation manager was added.

## Important lineage note
Projection candidates currently carry the exact full source-vector ancestry used to produce their training samples, not a minimized causal dependency subset.

For example, C is trained from a generated vector A/B/D and selects positions A/B, so its stored source-vector ancestry still contains A/B/D. This is conservative: it may stale a projection when an unused source coordinate changes. It does not grant false currentness.

Do not call this minimal dependency lineage.

A later pass may test whether dependency minimization is worth adding, but MS1987 does not need it to establish recursive evaluation.

## Authority ceiling
- recursive evaluation authority: exact current admitted source lineage only;
- source selection authority: automatic compatible current set + supplied count/depth ceilings;
- semantic symbol authority: NONE;
- semantic recursion authority: NONE;
- semantic composition authority: NONE;
- truth authority: NONE;
- language authority: NONE;
- sample persistence: NONE.

## Interpretation
MS1987 would show a real extra step in representation growth: an opaque representation produced from learned representations can itself be evaluated from grounded owned evidence and used as an input to another existing projection search.

That is recursive operational representation composition.

It is not evidence that the buckets are concepts, symbols, words, or semantic categories.

## Focused verification
Direct pytest over the focused set produced 12 failures and 21 passes, but every failure was a Windows cleanup lock on an open `biography.sqlite3`; no mechanism assertion failed. This is the known reason the repository carries the cleanup-neutral runner.

The same exact focused set through `tools/run_pytest_cleanup_neutral.py`:
- job `job-4b9142b4e2a1`;
- **33/33 PASS in 87.52s**;
- stderr empty.

The set covered MS1477 routing, MS1865 current visible-history projection, MS1971 projection admission, and MS1983–MS1987 owned projection/routing/composition surfaces.

## Final verification
- focused cleanup-neutral regression: `job-4b9142b4e2a1` -> **33/33 PASS in 87.52s**;
- whole cleanup-neutral embodiment suite: `job-bae9757b4785` -> **776/776 PASS in 380.52s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall over microseed/research/scratch/tests: PASS;
- `git diff --check`: PASS.

## Seal/publication gate
The technical pass is eligible to seal because the process embodiment, focused regressions, self-test, compile gate, and whole-organism suite all passed.

Publication still requires:
1. local Git seal;
2. push of the exact sealed research ref;
3. independent remote ref readback matching the sealed SHA.
