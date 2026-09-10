# Start Here — What Proto-Microseed Is

## One-sentence orientation

**Proto-Microseed is an experimental AGI substrate / developmental cognitive organism research codebase, not a governance product.** Its research question is how far cognition can grow from a small set of grounded, current, qualified mechanisms and lawful composition without installing the answer as a predeclared semantic faculty, generic planner, or language model wrapper.

The governance and continuity machinery is deliberately prominent because the project treats authority, evidence, currentness, lineage, and failure preservation as part of doing the research correctly. That machinery constrains the work; it is not what the organism *is*.

## Project intent

**Grow cognition rather than install intelligence.**

A useful compact description is:

> Microseed is a minimal prelingual developmental cognitive organism whose capabilities must be earned from grounded experience and lawful composition, while truth, currentness, scope, qualification, and execution authority remain explicitly bounded.

The central research question is:

> What is the smallest set of mechanisms that can recursively generate more capable cognition without also generating unearned authority?

## Do not mistake the scaffolding for the substrate

- `microseed/` is the organism/runtime implementation.
- `tests/embodiment/` is where mechanisms are attacked, not merely demonstrated.
- `methodology/` records bounded experiments, laws, failures, promotions, and scope ceilings.
- `campaigns/` contains governed multi-pass research campaigns and their receipts.
- `evidence/` contains compact verification/publication receipts.
- governance/authority/continuity surfaces constrain the research process and preserve exact lineage. They do **not** redefine Microseed as a governance system.

## Current public research frontier

The conservative default `main` branch is intentionally not identical to the newest research head. For the current organism frontier, checkout:

```text
research/rehearsal-currentness-rebase-on-substrate-v1
```

Exact anchors:

```text
science seal:     1d6d384fd97dc7e84b7c2e88114d76e965e886fa
campaign receipt: c33104c8b1e3e24147f99e9a147a3673976e45a4
```

That branch preserves this earned chain:

```text
C08I native pair harvest
  70bc659d26dd668cbda2ecb62b7914856c25a9b0
→ active acquisition revalidation
  dfeaff9cd797be8a26d6082eef8f09101043c100
→ bounded held-out B2 recombination
  80fb18a6922abf663928ab2638a23ca65f702529
→ fixed-depth recursive B2-child reuse
  9c633d096a1f60f4263c10895ed44edd1a6d07bf
→ direct distinct-leaf B3
  39bd68e5484e2229b6a4349248025aebb3428835
→ bounded direct arity 2–4
  d961ce17180fe365f7c185779742b913d908d37a
→ authenticated action-execution window-boundary recognition
  c87a6dfff3c0b6d2236ac89c52f0988c8e4caf0c
→ bounded retrospective structural boundary-occasion ownership
  d87a45a5886f5b5b4de26315e468be39a0717370
→ bounded append-only structural segment-state consumption
  7ba1010be8201e71fbad922b7b1068491f996886
→ bounded B2-compatible structural segment state as reusable recursive composition operand
  500ac5de919f770f79e675002a87a366213836c7
→ bounded grouped segment operands with child leaf arity 2–4
  38bf32af09962f7d4718ed0d1dbb0fbf6fc2905a
→ history-stable timed-action substrate + authenticated grouping boundaries
  75ac873d5fe3330c31ff0321078930320fa59045
→ indexed canonical stale-learned-relation rehearsal currentness restored
  1d6d384fd97dc7e84b7c2e88114d76e965e886fa
```

## Read order for Claude or another external reviewer

If you want an AI reviewer to understand the project rather than mistake the process scaffolding for the object of research, use this order:

1. **This file — `START_HERE.md`.** Establish project identity, intent, and the main-vs-research distinction.
2. **`README.md`.** Use it for the broader public/canonical history and repository map, but do not stop at the governance section.
3. **Checkout `research/rehearsal-currentness-rebase-on-substrate-v1`.** The latest research is not all on default `main`.
4. **`campaigns/REHEARSAL_CURRENTNESS_REBASE_2026-09-10/FINAL_SUMMARY.json`.** This is the compact current campaign result and exact authority ceiling.
5. **`campaigns/MS_SUBSTRATE_INDEXING_2026-09-10/FINAL_SUMMARY.json`.** This is the immediately prior substrate-hardening campaign and soak-performance gate.
6. **`campaigns/SEGMENT_OPERAND_ARITY_GENERALIZATION_2026-09-09/FINAL_SUMMARY.json`.** This is the prior grouped-segment arity campaign.
7. **`campaigns/SEGMENT_STATE_OPERAND_2026-09-09/FINAL_SUMMARY.json`.** This is the immediately prior 2+2 segment-operand campaign.
8. **`campaigns/BOUNDARY_CONSUMPTION_2026-09-08/FINAL_SUMMARY.json`.** This is the prior segment-consumption campaign.
9. **`campaigns/BOUNDARY_OCCASION_2026-09-08/FINAL_SUMMARY.json`.** This is the prior structural boundary-occasion campaign.
10. **`campaigns/OPERAND_WINDOW_BOUNDARY_2026-09-07/FINAL_SUMMARY.json`.** This is the prior action-execution boundary-recognition campaign.
11. **`campaigns/ARITY_GENERALIZATION_2026-09-07/FINAL_SUMMARY.json`.** This shows the direct bounded arity-generalization campaign, including inherited negative-token evidence defects that were found and repaired rather than hidden.
12. **`microseed/runtime/entity.py`.** Read the production organism implementation, especially the native grounded association/composition/currentness/action-closure paths. Do not infer a faculty from a method name; trace the evidence and authority gates.
13. **Relevant embodiment tests:**
   - `tests/embodiment/test_lang_action_execution_boundary_production.py`
   - `tests/embodiment/test_lang_action_execution_boundary_replay_and_history.py`
   - `tests/embodiment/test_lang_action_execution_boundary_restart_production.py`
   - `tests/embodiment/test_lang_bounded_arity_generalization_production.py`
   - `tests/embodiment/test_lang_systematic_heldout_native_b2_recombination.py`
   - `tests/embodiment/test_lang_recursive_b2_composition_as_operand.py`
   - `tests/embodiment/test_lang_c08i_native_pair_harvest.py`
   - `tests/embodiment/test_lang_boundary_occasion_production.py`
   - `tests/embodiment/test_lang_boundary_occasion_production_hostiles.py`
   - `tests/embodiment/test_lang_boundary_occasion_ceiling_audit.py`
   - `tests/embodiment/test_lang_boundary_consumption_production.py`
   - `tests/embodiment/test_lang_boundary_consumption_ceiling_audit.py`
   - `tests/embodiment/test_lang_boundary_consumption_invocation_budget_smuggling.py`
   - `tests/embodiment/test_lang_segment_state_b2_recursive_production.py`
   - `tests/embodiment/test_lang_segment_state_b2_recursive_hostiles.py`
   - `tests/embodiment/test_lang_segment_state_operand_owner_gap_audit.py`
   - `tests/embodiment/test_lang_segment_operand_arity_owner_gap_audit.py`
   - `tests/embodiment/test_lang_segment_operand_bounded_arity_carrier_prototype.py`
   - `tests/embodiment/test_lang_segment_operand_bounded_arity_production.py`
   - `tests/embodiment/test_lang_segment_operand_bounded_arity_hostiles.py`
   - `tests/embodiment/test_lang_segment_operand_arity_ceiling_audit.py`
   - `tests/embodiment/test_ms_substrate_indexed_execution_and_store.py`
   - `tests/embodiment/test_ms_substrate_boundary_authority_hardening.py`
   - `tests/embodiment/test_ms_substrate_biography_head_index.py`
   - `tests/embodiment/test_rehearsal_currentness_indexed_rebase.py`
   - `tests/embodiment/test_ms1943_signal_predictive_currentness.py`
14. **Methodology for the deeper conceptual constraints:** start with `methodology/MS1959_MS1961_AFFORDANCE_RELATIVE_PROTO_REFERENCE.md`, then follow the numbered lineage relevant to the mechanism being inspected.
15. **For exact continuity/current frontier**, use the separate `SEng-Kitathas/Proto-Microseed-RD-Continuity` repository if available. Its current re-entry/current-state/live-shadow surfaces are recovery authority, not a replacement for reading the organism code and experiments.

## What the current frontier actually earns

The current research lineage has earned bounded mechanisms for grounded operational association and composition. The same bounded direct composition owner can derive arity 2, 3, or held-out 4 from current grounded token chronology without caller-supplied arity. It can recognize an authenticated current-runtime action execution as an operational boundary and retrospectively derive a durable structural boundary witness when exactly one lawful split is compelled. The segment-consumption campaign can consume that CURRENT witness into append-only retrospective left/right structural segment state whose content identity matches the earned bounded-composition identity. The 2+2 segment-operand campaign earned two grouped fixed-depth-one recursive operands, and the bounded-arity campaign generalized each grouped LEFT/RIGHT child independently to leaf arity 2–4 while the parent remained exactly two child-composition digests at depth one. Subsequent substrate hardening removed the measured history-coupled act-cost scans and arbitrary-evidence grouping authority, and the current campaign restored canonical stale-learned-relation rehearsal currentness through indexed exact learned-owner lookup without reintroducing O(total learned relations) scans.

The current frontier is **not** “AGI complete.” `AGI substrate` here names the research target and architectural role: a small developmental substrate intended to grow cognition. The project still refuses to promote missing mechanisms by rhetoric. Among the explicit nonclaims are:

- generic/unbounded N-ary composition;
- generic/unbounded structural segment-state operand reuse beyond the earned bounded leaf arity 2–4 cases;
- deeper reuse of the grouped retrospective parent state or generic recursive closure;
- flattening or associativity inferred from reusable operand content identity;
- endogenous boundary monitoring / segment-consumer scheduling;
- unrestricted or generic planning;
- semantic truth/reference authority from language;
- grammar or language competence;
- semantic self/body/other ontology;
- generic exploration authority;
- canon promotion of every successful research branch.

## Current next discriminator

```text
STRUCTURAL_SEGMENT_RECURSIVE_PARENT_STATE_AS_REUSABLE_COMPOSITION_OPERAND_WITHOUT_FLATTENING_OR_ASSOCIATIVITY
```

Microseed now also has a history-stable timed-action substrate, authenticated operational grouping boundaries, and restored indexed canonical rehearsal currentness. The full 1,200-episode causal-shift soak passes selectively: stale R-41 blocks only its owning learned rehearsal, K/M remain current, and an explicitly qualified replacement R re-enters without global reset. With those substrate/currentness blockers closed, the next question returns to whether the grouped retrospective segment parent can become one nested child of a bounded depth-two composition without flattening, associativity, or generic recursive closure.

## Reading discipline

When reviewing Microseed, preserve these distinctions:

```text
MISSING BEHAVIOR != MISSING MECHANISM
DERIVED != QUALIFIED != CURRENT != AUTHORIZED
MODEL OUTPUT != OBSERVATION
PREDICTION != ACTUAL OUTCOME
SELECTION != EXECUTION
INFORMATION_VALUE != EFFECT_AUTHORITY
ORDERED_OPERATIONAL_COMPOSITION != SEMANTIC_COMPOSITION
ACTION_EXECUTION_BOUNDARY_RECOGNITION != AUTONOMOUS_BOUNDARY_OCCASION_SELECTION
BOUNDARY_OCCASION_CONTENT_OWNERSHIP != ENDOGENOUS_INVOCATION_SCHEDULING
STRUCTURAL_BOUNDARY_WITNESS != SEGMENTED_COMPOSITION_EVIDENCE
RETROSPECTIVE_BOUNDARY_RECOGNITION != PROSPECTIVE_BOUNDARY_PREDICTION
CHILD_LEAF_ARITY_2_TO_4 != PARENT_CHILD_COUNT
FIXED_DEPTH_ONE_GROUPED_REUSE != RECURSIVE_CLOSURE
REUSABLE_OPERAND != FLATTENING_OR_ASSOCIATIVITY
```

External analyses, including AI-generated reviews, are donor material until independently reconciled with code, tests, receipts, and current authority. Strip them for mechanisms, scars, counterexamples, and discriminators; do not import their conclusions wholesale.
