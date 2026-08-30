# MS1914 — External Validation / Scar Re-Earning Evidence

## Discriminator
`STANCE_MATCH != MECHANISM_VERIFIED_FOR_INHERITED_EPISTEMIC_GUARDS`

## Provenance
Challenge family originated from external forensic review, not the immediate Microseed implementation loop. Five named mutants were supplied as external audit signals:
- `IGNORE_ZERO_PRESSURE`
- `IGNORE_CAPABILITY_EPOCH_DRIFT`
- `ACCEPT_NONCURRENT_VALUE`
- `ALLOW_NON_ACTION_LIMITED_DEFICIT`
- `FEASIBILITY_NOT_REQUIRED_CURRENT`

Current-server reproduction used named transformations encoded in `tools/run_ms1914_pass03_external_mutation_reproduction.py`. Unless original external patch bytes are later supplied, this is a current-descendant reproduction of the named mutant semantics, not a claim of byte-identical external patches.

## First current-descendant reproduction
The durable mutation harness isolated each mutant in a copied temporary repository and ran the inherited epistemic suite.
Initial result: four mutants rejected; `FEASIBILITY_NOT_REQUIRED_CURRENT` survived with the inherited suite green.

Interpretation: this exposed a mechanism-blind test surface, not an automatic production defect.

## Mechanism inspection
`derive_grounded_feasibility_option()` explicitly requires the feasibility capability to be qualified and `currentness == CURRENT` before invocation.
`CapabilityRegistry.invoke()` checks qualification, obligation, scope, and handler but does not independently check the `currentness` field.
Therefore the `FEASIBILITY_NOT_REQUIRED_CURRENT` mutation removes a real currentness guard rather than merely removing redundant defense-in-depth.

## Test-only strengthening
No production code was changed.

Strengthened:
- `tests/embodiment/test_ms1709_decision_bearing_priority.py`
  - asserts mechanism-bearing `reason` and minimally sufficient `premise_ids` for zero pressure, capability-epoch drift, value-currentness drift, and non-ACTION_LIMITED deficit state;
- `tests/embodiment/test_ms1706_grounded_feasibility_epistemic_step.py`
  - adds explicit qualified-but-STALE feasibility-capability hostile and requires the currentness owner to produce ABSTAIN / `FEASIBILITY_CAPABILITY_NOT_CURRENT`.

Strengthened-test durable receipt: `reports/ms1914_pass03_strengthened/receipt.json`.
Result: 18/18 PASS, exit 0, COMPLETE, stderr empty.

## Final unchanged five-mutant rerun
Durable job: `job-5bdeeac892d8`.
Receipt: `reports/ms1914_pass03_mutants/receipt.json`.
Completion: COMPLETE.
Survivors: 0.
Rejected: 5.
Unknown: 0.

Mechanism witnesses:
- `IGNORE_ZERO_PRESSURE` rejected because the intended reason changes from `NO_CURRENT_REGULATORY_PRESSURE` to `DISCRIMINATION_CANNOT_CHANGE_CURRENT_EXECUTABLE_ACTION`.
- `IGNORE_CAPABILITY_EPOCH_DRIFT` rejected because intended UNKNOWN becomes YES.
- `ACCEPT_NONCURRENT_VALUE` rejected because intended `VALUE_PREMISE_NOT_CURRENT` is bypassed.
- `ALLOW_NON_ACTION_LIMITED_DEFICIT` rejected because intended UNKNOWN becomes YES.
- `FEASIBILITY_NOT_REQUIRED_CURRENT` rejected because intended ABSTAIN becomes `ACTION_INTENT_NOMINATED` for a qualified-but-STALE feasibility capability.

Clean source hashes recorded by the mutation receipt:
- `microseed/development/epistemic_priority.py`: `71b8fceb852cbaa36c824c4674b76ff1bab92a86cf5fe627ad8cc86c92838440`
- `microseed/development/epistemic_action.py`: `8fd9ec5123817053f1f2d3435697341858fbc2ab0dd525aa1d976d335a8a8dda`

## Integrated clean-tree regression
Server job: `job-4ec35f5183fa`.
Receipt: `reports/ms1913_regression/receipt.json` (reused regression launcher with strengthened tests present).
Overall: PASS / COMPLETE.
- modern: 29/29 PASS in 15.87s, stderr empty;
- inherited cleanup-neutral: 74/74 PASS in 8.21s, stderr empty;
- compileall: PASS, stderr empty.

## Git seal
Commit: `345476a6792ca56804787bc0bec19682f2517ece`
Message: `MS1914 re-earn inherited epistemic guards under external mutants`
Content: strengthened tests + durable mutation/strengthened-test runners only.
Production code mutation: NONE.
Worktree: clean immediately after commit.

## Scar / claim status
The five named external mutant semantics are `CURRENT_REEARNED` against the current descendant under mechanism-bearing tests.

This does NOT establish independent-validation completeness or exhaust unknown blind spots. The external-review ceiling remains OPEN: a new independently authored mutant/counterexample family still has higher epistemic value than simply multiplying same-lineage green tests.

## Literature / novelty state
Primary richer prior-art map: `notes/maintenance/MS1914_EXTERNAL_LITERATURE_MAP.md`.
Discovery supplement: `notes/maintenance/VALIDATION_PASS_V1_PRIOR_ART_STARMAP.md`.
Novelty remains `UNKNOWN / NOT ENTITLED TO CLAIM`; existing literature already establishes autonomous goal/experiment selection, learning-progress curiosity, epistemic value / expected information gain, active learning, and model-discriminating experiment design.

## Apparatus-tax response
Do not create redundant doctrine/evidence artifacts for the same result. `PROJECT_LOCAL_EXTERNAL_VALIDATION_AMENDMENT.md` remains the primary exact audit/mutant record; `EXTERNAL_VALIDATION_AND_SCAR_REEARNING_AMENDMENT.md` is a compatible general supplement. This evidence note is the compact MS1914 seal record.