# MS1923 Pass 12 Evidence — Program Trace Equivalence Is Not Realization Identity

## Frontier
Long-deferred program-realization equivalence vs ambiguity.

Refined discriminator:
`REPRESENTATION_EQUIVALENCE != PROGRAM_REALIZATION_IDENTITY`.

## Parent authority
- Parent sealed research head: `40b690ecfa66c963119398e1e8029cf9014e2173` — MS1922.
- Canonical Main-Dev remains MS1527; no promotion.

## Classification
**NEGATIVE / NO_PRODUCTION_CHANGE PASS.**

No runtime source changed.

## Recovered historical owners
MS1810 already establishes:
`INFORMATION_PARTITION_IDENTITY != PROGRAM_TRANSFORMATION_IDENTITY`.
Two distinct programs may induce the same partition while producing different represented observable traces.

MS1811 exposes `derive_program_observable_trace_signature(...)` as representation-only and leaves missing transitions unresolved.

MS1746 already preserves multiple current epistemic opportunities when the same program word arrives through different relation provenance; caller order cannot collapse the ambiguity.

MS1819 binds generated candidate identity to action word plus exact source relation content; changing relation content changes candidate identity even when the word is unchanged.

MS1908/MS1910 require exact current source-relation ancestry for discriminator satisfaction. Matching discriminator signature alone cannot launder unowned/subset/superset/drifted source relations.

MS1911 collapses only content-equivalent registered discriminator requirements; genuinely distinct current requirements remain ambiguous.

## Stronger MS1923 hostile
MS1923 constructed two physically/action-wise distinct generated words:
- `A,B,C`
- `X,Y,Z`

Both were represented so that under each live alternative they traversed the exact same observable state trace:
- alternative 0: `S1 -> S2 -> P`
- alternative 1: `S1 -> S2 -> Q`

Therefore both had:
- identical observable trace signatures;
- identical information partition `((0,), (1,))`.

Yet:
- action words remained different;
- candidate IDs remained different;
- candidate digests remained different;
- trial digests remained different;
- relation candidate IDs remained different;
- all program authorities remained NONE.

Equal partitions also fail strict refinement in both directions:
`program_partition_strictly_refines(p,p) == False`.

Thus the production arbitration rule cannot derive a unique winner merely from equal information structure.

## Production consumer audit
`derive_program_observable_trace_signature(...)` has no production identity/selection consumer beyond partition construction.

`derive_program_observable_partition(...)` is used by endogenous trial arbitration only for **strict partition refinement**. Equal partitions produce no dominator; multiple admitted candidates remain multiple opportunities with selection/execution/truth authority NONE.

Therefore no current owner promotes trace/partition equality into physical realization identity.

## MS1923 audit suite
`tests/embodiment/test_ms1923_pass12_program_trace_equivalence_not_realization_identity.py`

4/4 PASS, job `job-9eee082968b3`:
1. different program words may have identical trace signature and partition;
2. equal trace/partition do not collapse candidate/trial identity;
3. equal partitions create no strict-refinement selection authority;
4. representation equivalence grants no program authority.

## Compatibility
Focused identity/ancestry owner chain job `job-4ba01d52371d`:
- MS1746, MS1810, MS1811, MS1817, MS1818, MS1819, MS1908, MS1910, MS1911, MS1923: **32/32 PASS**.

Selective regression job `job-f12574d14a90`:
- modern PASS;
- inherited cleanup-neutral PASS;
- compileall PASS;
- overall PASS / COMPLETE.

No production source changed, so production exact compatibility remains inherited from sealed MS1919 (670/670 over 177 files), with subsequent audit-only seals layered above.

## Earned laws
- `REPRESENTATION_EQUIVALENCE != PROGRAM_REALIZATION_IDENTITY`.
- `TRACE_SIGNATURE_EQUALITY != ACTION_WORD_IDENTITY`.
- `PARTITION_EQUALITY != SELECTION_AUTHORITY`.
- `INFORMATION_EQUIVALENCE != PHYSICAL_GENERATOR_IDENTITY`.
- `DISCRIMINATOR_SATISFACTION != SOURCE_ANCESTRY_SUBSTITUTABILITY`.
- `CONTENT_EQUIVALENT_REQUIREMENT != DISTINCT_PROGRAM_REALIZATION`.

## Disposition
The deferred program-realization seam is CLOSED under current evidence. Existing owners already preserve representation, information, source ancestry, program identity, and execution authority as distinct surfaces.

Reopen only if a later production path uses trace/partition equality to substitute one program for another, restore execution authority, or collapse distinct source ancestry.

## HSP / frontier posture
HSP remains advisory only. Attention Reservoir should select the next sibling after seal; no blind external challenge is currently present.
