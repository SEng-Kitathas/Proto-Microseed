# MS1914 / Validation Pass V1 — Mechanism-Verification Hardening

## Discriminator
`STANCE_MATCH != MECHANISM_VERIFIED_FOR_INHERITED_EPISTEMIC_GUARDS`

Plain-language alias: a test that gets the same YES/NO/UNKNOWN result is not necessarily testing the mechanism that produced it.

## Provenance
External evaluator supplied five independent mutant concepts/results, not exact harness bytes. Their challenge origin is externally independent; the current-server mutation patches are `SELF_AUTHORED_REPRODUCTION_OF_EXTERNAL_CHALLENGE`, not a byte-identical blind rerun.

Mutant concepts:
- `IGNORE_ZERO_PRESSURE`
- `IGNORE_CAPABILITY_EPOCH_DRIFT`
- `ACCEPT_NONCURRENT_VALUE`
- `ALLOW_NON_ACTION_LIMITED_DEFICIT`
- `FEASIBILITY_NOT_REQUIRED_CURRENT`

## Pre-hardening reproduction
Durable job: `job-19a8ea4199cb`.
Wrapper status: COMPLETED, return code 0, duration 42.395s.
Preserved stdout journal confirms all five mutants SURVIVED the unchanged inherited pressure set; none rejected; no UNKNOWN.

This independently reproduced the evaluator's mechanism-blindness signal on the current descendant using locally reconstructed mutant patches.

## Validation-only repair
No Microseed production semantics changed.

Strengthened `test_ms1709_decision_bearing_priority.py` to assert minimum mechanism witnesses already exposed by `RelationalCommitment`:
- zero current regulatory pressure -> `NO_CURRENT_REGULATORY_PRESSURE`, premise IDs `('D','V')`;
- capability epoch drift -> `RELATIONAL_ALTERNATIVE_CAPABILITY_EPOCH_DRIFT:A`;
- noncurrent value -> `VALUE_PREMISE_NOT_CURRENT`, premise IDs `('D','V')`;
- non-ACTION_LIMITED deficit -> `ACTION_LIMITED_DEFICIT_REQUIRED`;
- positive/same-action paths also assert their intended reason/premise ancestry where load-bearing.

Strengthened `test_ms1706_grounded_feasibility_epistemic_step.py`:
- normal invalidation test initially left `FEASIBILITY_NOT_REQUIRED_CURRENT` observationally equivalent because invalidation stales both qualification and currentness;
- source/type inspection showed `CapabilityContract` permits qualified-but-`currentness='STALE'` contracts;
- added exact hostile for that independently load-bearing state, requiring `FEASIBILITY_CAPABILITY_NOT_CURRENT` before nomination.

## Post-hardening mutant result
Final durable mutation job: `job-303ee66b5882`.
Wrapper status: COMPLETED, return code 0, duration 45.442s.
Final mutation receipt: `reports/ms1914_pass03_mutants/receipt.json`.

All five mutants REJECTED:
- zero-pressure deletion fails the zero-pressure reason witness;
- capability-epoch drift deletion changes UNKNOWN -> YES;
- value-currentness deletion changes intended reason to a downstream substitute;
- non-ACTION_LIMITED deletion changes UNKNOWN -> YES;
- feasibility-currentness deletion changes ABSTAIN -> ACTION_INTENT_NOMINATED in the qualified-but-stale case.

Classification: VERIFIED that these five previously surviving mutant classes were test-adequacy blind spots, not production holes, in the tested current mechanism surface.

## Clean strengthened tests
Durable job `job-8b86c2247f08`: strengthened mechanism tests PASS, exit 0.
Receipt: `reports/ms1914_pass03_strengthened/receipt.json`.

## Selective regression
Durable job `job-4ec35f5183fa`, exit 0.
Receipt: `reports/ms1913_regression/receipt.json`.
- modern: 29/29 PASS;
- inherited cleanup-neutral: 74/74 PASS;
- compileall: PASS;
- stderr empty.

## Full compatibility breadth
A monolithic cleanup-neutral full-suite route was attempted first and timed out after 120s at ~34% progress. Receipt classified `UNKNOWN_INCOMPLETE_TIMEOUT`; this is a route nonresult, not a suite failure.

Per collaborator execution preference, the route was decomposed rather than timeout-raised.

Bounded compatibility execution:
- first-level top shards 0 and 5 completed PASS;
- heavy parent shards 1–4 were recursively split into 3 smaller children each;
- selected aggregate therefore uses 14 completed receipts total.

Aggregate receipt: `reports/ms1914_pass03_full_suite_shards/aggregate_receipt.json`.
Exact coverage:
- 172/172 test files covered exactly once;
- missing files: 0;
- extra files: 0;
- duplicate files: 0;
- aggregate tests: 629/629 PASS;
- all selected receipts COMPLETE/PASS with exit 0.

Claim boundary: this establishes broad compatibility after validation hardening. It is NOT mutation-adequacy evidence; the five-mutant rejection matrix is the mechanism evidence.

## Git / embodiment
Validation-hardening commit: `345476a` — `MS1914 re-earn inherited epistemic guards under external mutants`.
Bounded sharded compatibility tooling commit: `83d516691e13cb2639aae993cfedc7c831686b8e` — `MS1914 add bounded sharded compatibility runner`.
Worktree clean at seal.
No Microseed production file changed in MS1914.

## Scar authority after this pass
CURRENT_REEARNED for the tested current owners:
- `EPISTEMIC_UNCERTAINTY != NORMATIVE_PRIORITY` via zero-pressure deletion mutant;
- capability epoch currentness for decision-bearing relation alternatives;
- constitutional value currentness for decision-bearing priority;
- ACTION_LIMITED need-state requirement for regulatory decision bearing;
- feasibility capability currentness before grounded nomination;
- new scar: `STANCE_MATCH != MECHANISM_VERIFIED`.

Other inherited scars are not automatically reauthorized by this pass. They remain `INHERITED_UNVERIFIED` unless current campaign evidence independently re-earns them.

## External-contact result
Prior-art pressure is now explicit. Existing server notes map SAGG-RIAC/competence progress, curiosity/learning progress, active inference/expected free energy, Bayesian optimal experimental design, discriminating experimental design, developmental robotics, active learning, and mutation testing.

Novelty status remains `UNKNOWN / NOT ENTITLED TO CLAIM` pending deeper mechanism comparison. Planner-free information-seeking or experiment selection alone is established prior art; any defensible Microseed distinction must be narrower and earned.

## Open API-boundary discriminator discovered during Pass 3
Production source audit found that legacy/public `nominate_epistemic_program_step_intent()` and grounded variant may create an `EPISTEMIC_PROGRAM_STEP` intent without priority/information commitments. Execution-time reauthorization also leaves priority/information `None` when `EpistemicStepExecutionContext.decision_context is None`.

Newer endogenous nomination/execution paths do supply both priority and information. Legacy/local fixture paths are actively used by MS1703 and by later lifecycle tests.

Current status: OPEN, not yet classified as defect. The next question is whether this is a lawful explicitly bounded legacy/local primitive path or an ambiguous public API that can be mistaken for decision-bearing epistemic autonomy.

## Apparatus-tax action
No third validation-doctrine artifact is added. Treat `EXTERNAL_VALIDATION_AND_SCAR_REEARNING_AMENDMENT.md` as the governing merged amendment; `PROJECT_LOCAL_EXTERNAL_VALIDATION_AMENDMENT.md` remains overlapping historical lineage. Future validation should prefer one durable receipt/evidence index over repeated long dispositions where possible.