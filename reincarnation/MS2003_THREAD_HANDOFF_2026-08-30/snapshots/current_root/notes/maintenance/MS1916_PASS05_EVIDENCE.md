# MS1916 / Pass 05 — Current-Locus Direct-Probe Authorization

## Discriminator
`EXACT_DIRECT_PROBE_SATISFACTION != CURRENT_DECISION_BEARING_AUTHORIZATION`

## Scientific finding
The direct-probe discriminator was genuinely realizable by capability `B`, but the exact qualified branch relations lived at control-state locus `s1` while the historical production trial fixture was instantiated from current state `s2`.

Exact qualified `B` branch relations:
- `R-B-S2-1868`: `s1 --B--> s2`, value effect -1.0; digest `c1aec24ae7aae27b0ecd2160d0defeb2a8c921ec422f1715ce0a6231de7c5ac4`.
- `R-B-SX-1868`: `s1 --B--> sx`, value effect +1.0; digest `6fd5b6c93b856e2f752161b366f4b1d97195e7ccfdb28d983fdeaefaeb06ce14`.

At `s2`, existing ancestry logic correctly returned `PROGRAM_RELATION_ANCESTRY_INCOMPLETE`; there was no live `s2/B` edge in either decision alternative.

When the successor was rebuilt with the organism already at `s1`, existing mechanisms were sufficient. Composing each exact `B` branch with current stable `s1/D` background produced:
- ancestry CURRENT;
- priority YES / `DISCRIMINATION_CAN_CHANGE_CURRENT_REGULATORY_ACTION`;
- information YES / `PROGRAM_CAN_CHANGE_OBSERVABLE_EVIDENCE`.

Classification: MISSING WIRING / LOCUS AUTHORIZATION BINDING, NOT MISSING COGNITIVE PRIMITIVE.

## Production repair
Only two production owners changed.

### `microseed/runtime/entity.py`
Added `derive_current_revised_surface_direct_probe_decision_surface(...)`:
- ephemeral / zero-authority only;
- exact current revised direct-probe branch relations define one conflict slot;
- requires current action-closure state to equal branch locus;
- wrong locus => `CURRENT_CONTROL_STATE_NOT_DIRECT_PROBE_LOCUS`;
- stable background comes only from existing stricter `_action_outcome_relation_current` relations at the same locus/value coordinate;
- ambiguous current background slot => `DIRECT_PROBE_BACKGROUND_RELATION_AMBIGUOUS`;
- no persistence, planner, registry, scheduler or new semantic model.

Production direct-probe trial instantiation now requires that current decision surface first. Historical branch relevance can no longer masquerade as a current executable program.

### `microseed/development/epistemic_priority.py`
Narrow requalification of the MS1914 state guard:
- `ACTION_LIMITED` remains accepted;
- `PROBE_AVAILABLE` is accepted only when an exact bound probe capability + epoch exist, the epoch is current, and every live alternative contains the bound probe relation at the current start state;
- arbitrary other states, including `REVISIT_REQUIRED`, remain UNKNOWN;
- successful bound-probe priority includes probe capability ID in `premise_ids`.

New/updated reasons:
- `ACTION_LIMITED_OR_EXACT_BOUND_PROBE_AVAILABLE_REQUIRED`;
- `EXACT_BOUND_PROBE_REQUIRED`;
- `BOUND_PROBE_CAPABILITY_EPOCH_NOT_CURRENT`;
- `BOUND_PROBE_RELATION_REQUIRED_AT_CURRENT_STATE`.

This requalifies rather than deletes the earlier scar.

## OARR / hostile surface
Final MS1916 test file contains nine Rangers:
1. wrong live locus refuses surface + production trial;
2. correct locus composes exact branch + stable background with zero authority;
3. exact bound `PROBE_AVAILABLE` re-earns priority + information and exposes probe premise witness;
4. bound probe epoch drift returns UNKNOWN;
5. missing bound probe relation at current locus returns UNKNOWN;
6. `REVISIT_REQUIRED` remains rejected;
7. public grounded nomination works only with the current revised decision context and still grants no execution authority itself;
8. subsequent state drift blocks fresh nomination at an earlier owner;
9. ambiguous current background abstains rather than first-picking.

Affected current-locus downstream MS1908–1913 surface: 29/29 PASS.

## Mutation adequacy
Final frozen source-mutant receipt: `reports/ms1916_pass05_source_mutants/receipt.json`.
Final valid job: `job-d0cd9e1f3b37`.

6/6 REJECTED; 0 SURVIVED; 0 UNKNOWN:
- `DROP_DIRECT_PROBE_LOCUS_GATE`;
- `ALLOW_REVISIT_AS_DECISION_PRESSURE`;
- `DROP_BOUND_PROBE_EPOCH_CURRENTNESS`;
- `DROP_BOUND_PROBE_RELATION_REQUIREMENT`;
- `DROP_BACKGROUND_AMBIGUITY_ABSTENTION`;
- `DROP_BOUND_PROBE_PREMISE_WITNESS`.

An earlier mutation job `job-491085035c1d` is INVALID_RUN for evidence because downstream tests changed during its execution. It is not counted.

Recovery readback after E: remount confirmed current normalized-text hashes exactly match the clean hashes in the final valid mutation receipt:
- `microseed/runtime/entity.py`: `d0cc6eed2d605925873a1b62b21d201b1e957c0ce4f0fd2f093c43ea718a1076`;
- `microseed/development/epistemic_priority.py`: `75ad2bf14a00aeea53b237ab9cc0a27b9dbbc3b912ae01d3633f1b11b3160b34`.

## Selective regression
Final frozen selective regression:
- 30/30 modern PASS;
- 74/74 inherited cleanup-neutral PASS;
- compileall PASS;
- overall PASS.

## Exact full compatibility
Frozen full-suite verifier: `reports/ms1916_pass05_full_suite_final/aggregate_receipt.json`.
It covered all ordinary/fast groups and ended route-incomplete only because six known slow historical singleton files exceeded the 35s leaf ceiling:
- MS1533;
- MS1534;
- MS1535;
- MS1598;
- MS1620;
- MS1643.

No negative groups occurred. Source stable=true. Compileall PASS.

Terminal leaf closure runner: `reports/ms1916_pass05_terminal_leaf_closure/aggregate_receipt.json`.
Job: `job-dca93333c113`.
It decomposed only those six files by test function, recursively splitting on timeout without raising the global ceiling.

Final closure:
- leaf coverage exact;
- 53/53 terminal-leaf tests PASS;
- base selected passes 596;
- aggregate exact compatibility: **649/649 PASS**;
- exact test-file coverage: **174/174**;
- negative groups: 0;
- remaining UNKNOWN: 0;
- source stable=true;
- compileall PASS from frozen base verifier.

Claim boundary: compatibility breadth is not mutation adequacy; the 6/6 source-mutant rejection owns mechanism adequacy.

## Infrastructure interruption and recovery
During the first final full-suite attempt, the ngrok server remained healthy but the configured `E:` volume disappeared. Project and even a separate recovery-inspector initialization failed with WinError 3 on `E:\`.

Classification: `INFRASTRUCTURE_VOLUME_UNAVAILABLE`, not a Microseed result.

No replacement project was initialized and no write/recreation was attempted against the missing project path. An off-server emergency recovery checkpoint was created as non-authoritative continuity insurance only.

After the collaborator restored `E:`, readback verified:
- original project/ledger/manifest returned;
- sealed pre-pass head remained `33e93566bee2bbd04cc17c005609a060fe7dbfad`;
- complete uncommitted MS1916 diff survived;
- final mutation source hashes matched exactly under like-for-like normalized-text hashing;
- exact compatibility was rerun and closed before commit.

New operational scar: `SERVER_HEALTH != PROJECT_VOLUME_AVAILABILITY`.
New recovery law: `OFF_SERVER_RECOVERY_CHECKPOINT != PROJECT_AUTHORITY_UNTIL_ORIGINAL_LINEAGE_AND_SOURCE_HASHES_RECONCILE`.

## Git seal
Experimental research-descendant commit:
`54bde4fd01509642a7c11a5f94645b56f92a8d28`

Commit message:
`MS1916 bind direct probe authorization to current locus`

16 files changed; worktree clean after seal.

Canonical Main-Dev remains MS1527. No promotion.

## Helix successor
The direct-probe chain now earns a decision-bound intent at a genuinely current branch locus, but intent/authorization is still not a physical outcome.

Next discriminator:
`BOUND_CURRENT_PROBE_INTENT != PHYSICAL_EXECUTION_AND_OBSERVATION_CLOSURE`

Plain-language question: can the same current-locus decision context survive execution-time reauthorization, produce one real bounded probe execution, and close through actual observation/evidence without converting predicted branch relevance into observed truth or inheriting authority across the tick?