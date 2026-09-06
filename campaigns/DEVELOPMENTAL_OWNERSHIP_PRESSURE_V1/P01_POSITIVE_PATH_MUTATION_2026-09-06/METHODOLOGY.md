# P01 — Developmental Positive-Path Mutation Pressure

Status: `BOUNDED_DIAGNOSTIC_COMPLETE`

## Question
Can the current regression surface detect loss of already-earned positive behavior, rather than only detect authority loosening / over-granting?

## Why this exists
Historical source-mutant campaigns primarily loosened guards. External review correctly identified that this does not directly measure the mirror failure: a progressively safer organism that silently loses lawful action, endogenous experiment initiation, grounded program generation, or fresh currentness recovery.

This first discriminator deliberately disables four already-earned positive paths. It adds no organism mechanism and grants no authority.

## Baseline
The exact unmutated C08A-derived branch ran:
- `test_ms1402_integration.py`
- `test_ms1710_endogenous_epistemic_initiation.py`
- `test_ms1820_pass13_owned_three_locus_surface_generates_program.py`
- `test_lang_c08_native_evidence_association_currentness.py`

Baseline: `22/22 PASS`.

## Mutants
1. suppress an earned bounded-action YES;
2. suppress an earned endogenous epistemic intent;
3. suppress owned three-locus program generation;
4. suppress C08A fresh post-restart revalidation to CURRENT.

A mutant is **KILLED** only when its existing targeted test fails. A surviving mutant would be a concrete under-action blind spot for that path.

## Result
All four mutants were killed. No timeout/unknown occurred.

This does **not** establish symmetry of the whole suite and does not invalidate the broader assertion-shape asymmetry. It establishes only that these four selected positive surfaces are explicitly defended.

## Interpretation
`SELECTED_POSITIVE_PATHS_DEFENDED != POSITIVE_COVERAGE_COMPLETE`

Candidate pressure law, not canon:
`CORRECT_ABSTENTION != DEMONSTRATED_COMPETENCE`

## Next
Use the positive-path mutation axis as a standing discriminator on new developmental/language work. Broaden it by sampling additional earned positive surfaces rather than assuming the four selected paths represent the full system.
