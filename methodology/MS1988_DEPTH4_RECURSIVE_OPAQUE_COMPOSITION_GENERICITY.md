# MS1988 — Depth-4 Recursive Opaque Composition Genericity

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: MS1987 `d34a3491d412c154f525eedebafe624a18537b3f`
Core mechanism change in this pass: NONE

## Question
Was the MS1987 recursive evaluator a one-off depth-3 patch, or can the same mechanism support one more learned-representation generation without core changes?

Target chain:

`A+B -> C`

`C+D -> E`

`E+F -> G`

Prewrites:
- `GENERIC_RECURSIVE_EVALUATION != SEMANTIC_RECURSION`;
- `DEPTH_GENERALITY != OPEN_ENDED_REPRESENTATION_GRAMMAR`;
- `OPAQUE_BUCKET_CHAIN != CONCEPT_HIERARCHY`.

## Process world
Separate eight-bit process:
`research/substrate_shadow/depth4_recursive_bucket_world_server.py`.

Independent raw projections:
- A = parity `(0,1)`;
- B = parity `(2,3)`;
- D = parity `(4,5)`;
- F = parity `(6,7)`.

Composed process targets:
- C = A xor B;
- E = C xor D;
- G = whether E agrees with F.

The raw set contains 64 opaque octets covering every A/B/D/F parity combination with nuisance-bit variation so the pair parities remain learned two-coordinate structures.

## Method
No core file was changed.

The pass uses the MS1987 mechanisms exactly as sealed:
- owned raw/action/outcome sample derivation;
- current admitted projection discovery;
- exact source-projection lineage;
- bounded recursive source evaluation;
- existing projection search;
- external qualification.

### Stage C
Admit A/B/D/F, record 128 owned C histories, derive the four-source bucket vector with recursion depth 0, and learn C from A+B.

### Stage E
Record 128 owned E histories, derive A/B/C/D/F with recursion depth 1, and learn E from C+D.

### Stage G — falsifier
Record 128 owned G histories.

With recursion depth 1:
- E must be rejected because evaluating E requires reaching through C;
- available sources must be A/B/C/D/F;
- max-subset-2 search must produce no G candidate.

With recursion depth 2:
- E must become available;
- available sources must be A/B/C/D/E/F;
- one-source search must fail;
- max-subset-2 must find exact E+F positions `(4,5)` in lexicographic source order.

## Process result
The scratch campaign:
`scratch/ms1988_depth4_recursive_bucket_genericity.py`

returned PASS.

### Depth 1
- source set: A/B/C/D/F;
- E rejection: `SOURCE_PROJECTION_RECURSIVE_DEPTH_EXCEEDS_BOUND`;
- G max-subset-2 candidates: 0.

### Depth 2
- source set: A/B/C/D/E/F;
- one-source G candidates: 0;
- exact G positions: `(4,5)` = E+F;
- validation accuracy: 1.0;
- lift: 0.53125;
- external process holdouts: 64/64.

Currentness pressure:
- changing E stales G;
- changing C stales the current E generation.

Earned candidate statement:

`THE_SAME_BOUNDED_SOURCE_LINEAGE_EVALUATOR_SUPPORTS_ONE_MORE_LEVEL_OF_OPAQUE_REPRESENTATION_COMPOSITION_WITHOUT_CORE_MECHANISM_CHANGE`

## What this does not earn
MS1988 does not establish:
- semantic recursion;
- concepts or symbols;
- a concept hierarchy;
- language;
- open-ended recursion;
- autonomous source-family selection;
- removal of supplied recursion/source-count ceilings.

It establishes one additional tested depth for the same bounded evaluator.

## Lineage caution remains
Generated projections still store full source-vector basis ancestry rather than minimized causal dependency ancestry.

At deeper levels this causes ancestry width to grow:
- C record: 4 source projections;
- E record: 5 source projections;
- G record: 6 source projections.

That growth is now a clearer scaling seam. It is safe but may be wasteful and may cause avoidable staleness.

Do not fix it inside MS1988. The current pass is a genericity test, not a lineage redesign.

## Authority ceiling
- source evaluation: exact current lineage only;
- recursion: supplied bounded depth only;
- source count: supplied bounded ceiling only;
- semantic recursion authority: NONE;
- semantic symbol authority: NONE;
- truth authority: NONE;
- language authority: NONE.

## Focused verification
Cleanup-neutral focused test:
- `job-6c498585129d` -> **1/1 PASS in 80.22s**;
- stderr empty.

The pass also verified before testing that `git diff -- microseed` was empty. No core file changed relative to sealed MS1987.

## Final verification
- focused cleanup-neutral: `job-6c498585129d` -> **1/1 PASS in 80.22s**;
- whole cleanup-neutral: `job-d0fc85134a95` -> **777/777 PASS in 457.06s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS;
- `git diff -- microseed`: empty.

## Seal/publication gate
The evidence-only pass is eligible to seal. Publication still requires local Git seal, research-branch push, and independent remote ref readback matching the sealed SHA.
