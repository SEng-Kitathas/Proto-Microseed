# MS1996 — Endogenous Program Caller-Choice Elimination

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1995 `a3e82f4f80bbe910234590f2cdf982293ac4fa96`

## Question
Can Microseed construct and arbitrate a useful multi-step epistemic intervention/program from organism-owned opaque action/outcome history and currently qualified primitive capabilities **without the caller naming the preferred action or program sequence**?

And when multiple generated programs are equally informative, can it preserve ambiguity instead of acquiring pick-first authority?

Prewrites:
- `ENDOGENOUS_CANDIDATE_CONSTRUCTION != EXECUTION_AUTHORITY`;
- `OPAQUE_ACTION_HANDLE != SEMANTIC_ACTION_NAME`;
- `PROGRAM_PROPOSAL != POLICY`;
- `INFORMATION_BEARING != PERMISSION_TO_EXECUTE`;
- `TIE_OR_AMBIGUITY != PERMISSION_TO_PICK_FIRST`;
- `SEARCH_BUDGET_EXHAUSTION != NO_DISCRIMINATOR`.

## Audit before embodiment
The current core already contains the needed owners from the MS18xx/MS19xx lineage:

1. `derive_current_epistemic_effect_action_tokens(...)`
   - derives the query-local generator alphabet from current, qualified EFFECT capability contracts;
   - caller does not supply an action-token list.

2. `derive_current_generated_epistemic_program_candidates(...)`
   - searches represented alternatives for discriminating programs;
   - candidates carry exact source-relation/frame ancestry;
   - proposal, truth, execution, qualification, semantic-action and closure authority remain NONE.

3. `derive_three_locus_chain_action_outcome_epistemic_relation_sets()`
   - derives a bounded alternative-model surface from organism-owned admitted action/outcome history;
   - no externally supplied relation-set selection.

4. `discover_and_arbitrate_generated_epistemic_trial_from_three_locus_history(...)`
   - composes the owned alternative surface through generated-program search and the existing trial arbitration lane.

5. `arbitrate_endogenous_epistemic_trial_candidates(...)`
   - grounds feasibility once from current capability-derived routes;
   - does not use candidate order or a scalar score;
   - a unique winner is licensed only by strict observable-partition refinement;
   - unresolved equal/incomparable live opportunities remain explicitly multiple with selection authority NONE.

Therefore MS1996 is a composition/falsification pass, not a license to add a planner, scheduler, curiosity manager, or program executor.

## Boundary
Scratch:
`scratch/ms1996_endogenous_program_caller_choice_elimination.py`.

The world uses opaque primitive handles rather than semantic action names:
- useful chain: `K-17 -> M-23 -> R-41`;
- fallback: `F-83`;
- qualified nuisance/distractor handles include `A`, `B`, `N-61`, `N-67`.

The caller invokes only:
- current deficit ID;
- query obligation/scope;
- finite search-node budget.

It does **not** supply:
- preferred action ID;
- preferred first step;
- candidate sequence;
- semantic feature/action label;
- winner among generated programs.

## Owned-history route
Four recurrent owned histories create two live three-locus alternatives:
- two positive-regulatory trajectories ending in one opaque state;
- two negative-regulatory trajectories ending in another opaque state.

A current qualified shared fallback at the root makes the uncertainty decision-bearing under the current regulatory pressure.

The generated-program route returns:
`K-17 -> M-23 -> R-41`.

The registry-derived generator alphabet also contains qualified distractors, so this is not a one-option fixture disguised as endogenous choice.

Result:
- generated program is information-bearing: YES;
- current regulatory decision-bearing: YES;
- intents added during generation/arbitration: 0;
- executions added during generation/arbitration: 0;
- handler calls during generation/arbitration: 0;
- trial proposal/execution/truth/semantic-action authority: NONE.

## Search-budget hostile
The same owned-history candidate search is run with `max_nodes=1`.

Result:
- `SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED`;
- reason `REPRESENTED_PROGRAM_NODE_BUDGET_EXHAUSTED`;
- no generated candidate is silently interpreted as an exhaustive negative.

Thus:
`SEARCH_BUDGET_EXHAUSTION != NO_DISCRIMINATOR`.

## Tie hostile
A separate arbitration hostile uses the same registry-owned generator mechanism but two genuinely distinct discriminating second steps:
- `K-17 -> R-41`;
- `K-17 -> R-43`.

Both induce the same observable partition across the two live alternatives:
`[[0], [1]]`.

Both share the same decision-bearing first primitive `K-17`.

Result:
- `MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES`;
- reason `NO_UNIQUE_STRICT_PARTITION_REFINEMENT`;
- two candidate IDs retained;
- selection authority NONE;
- execution authority NONE;
- truth authority NONE;
- no caller-order selection.

### Wrong-path probe recorded
An earlier tie attempt used two different middle primitives that converged on the same represented common state. The search emitted only one continuation because represented common states are intentionally visited extensionally once.

That was not a missing candidate-generation mechanism. It was the correct behavior of the existing represented-state alias collapse. The hostile was repaired to use genuinely distinct discriminating actions at the same represented state.

## History insertion-order hostile
The owned recurrent histories are replayed into two fresh organisms in different insertion orders:
- `P1, P2, N1, N2`;
- `N2, P2, N1, P1`.

Both yield the same opaque program `K-17 -> M-23 -> R-41`, with the exact same candidate ID and digest. No intent or execution is created in either run.

Thus:
`HISTORY_INSERTION_ORDER != SELECTION_AUTHORITY`.

## Currentness hostile
After successful generation/arbitration, the required final primitive `R-41` is marked stale. Fresh generation from the current capability surface then yields:
- `REPRESENTED_REACHABILITY_INCOMPLETE`;
- the old `K-17 -> M-23 -> R-41` proposal is absent;
- fresh end-to-end arbitration returns `ABSTAIN`;
- reason `CURRENT_GENERATOR_TRANSITION_UNREPRESENTED`;
- no intent/execution side effect.

Thus:
`STALE_PRIMITIVE -> REGENERATE_FROM_CURRENT_SURFACE`, not cached proposal authority.

## Concurrent-draft reconciliation
During active drafting, a second local executor produced an unsealed MS1996 draft emphasizing history insertion-order invariance and stale-primitive currentness. The primary draft independently emphasized opaque handles, distractors, budget exhaustion, and equal-partition tie refusal.

Because neither draft was sealed, they were reconciled before verification. The final candidate explicitly merges both pressure sets into one scratch/test/methodology line; the redundant unsealed draft files were removed. Whole-suite verification started before this reconciliation is not eligible as a seal witness.

This is a continuity/concurrency scar, not an organism mechanism result.

## Earned
`OWNED_OPAQUE_HISTORY_PLUS_CURRENT_QUALIFIED_EFFECT_CONTRACTS_CAN_GENERATE_AND_ARBITRATE_DECISION_BEARING_PROGRAM_CANDIDATES_WITHOUT_CALLER_NAMED_ACTION_OR_PROGRAM_CHOICE_WHILE_PRESERVING_INSERTION_ORDER_CURRENTNESS_BUDGET_TIE_AND_EXECUTION_AUTHORITY_BOUNDARIES`.

## Mechanism verdict
No new core mechanism is required for this boundary.

The existing substrate already separates:
- generator alphabet ownership;
- represented program construction;
- decision/information bearing;
- feasibility;
- candidate arbitration;
- intent nomination;
- primitive execution.

Program construction does not imply execution. The NAKED unknown-effect first-probe authority block remains unchanged because every primitive used here is already represented/current/qualified under the existing effect lane.

## Remaining boundary
The largest remaining falsifier is now **rich-world lifetime composition**:
- learned representations and recursive composition;
- persistent/re-associated external referents;
- delayed/stochastic consequences;
- drift and relearning;
- restart/currentness changes;
- resource/opportunity pressure;
- nuisance changes;
- endogenous candidate construction;
- ordinary one-step execution and re-deliberation.

Many-referent partial-observability scaling remains a parallel hostile line.

## Final verification
- direct reconciled MS1996 boundary: PASS;
- focused endogenous-program / search / persistence lineage: `job-6028dd3dfbae` -> **41/41 PASS in 12.57s**;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS;
- whole cleanup-neutral embodiment suite: `job-716e9b81ee29` -> **794/794 PASS in 977.39s**;
- whole-suite stderr: empty;
- reconciled scratch/test/methodology hashes were frozen before focused/whole verification and the executable/test hashes matched exactly after the whole-suite pass.

### Rejected verification witness
An earlier whole-suite attempt `job-2b022cc09e38` was terminated externally around 27% with return code `-9` and empty stderr while concurrent draft reconciliation was still active. It is **not** a seal witness and is recorded only as an infrastructure/concurrency scar.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
