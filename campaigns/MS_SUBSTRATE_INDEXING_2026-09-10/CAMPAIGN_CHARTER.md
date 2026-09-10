# Microseed Substrate Indexing / Boundary Authority Hardening — 2026-09-10

## Mode
BUILD-COMMIT / substrate hardening before developmental soak.

## Base authority
- branch: `research/ms-substrate-indexing-v1`
- exact base: `793be7a81c9c3a71f57d4d89046882f22ed6207a`
- prior science: `38bf32af09962f7d4718ed0d1dbb0fbf6fc2905a`
- deeper-parent WIP preserved separately at `7b26c7105f36bb66f7887301a4dfe608ec61dff4`; NOT science authority.
- soak branches exist but soak execution is BLOCKED until latency-growth confound is removed.

## Priority discriminator A — history-independent act substrate
`ACCUMULATED_HISTORY != PER_ACT_LINEAR_WORK`

Verified baseline defects:
1. `execute_bounded_action()` performs `any(e.intent_id==intent_id for e in executions.values())` on every act.
2. `ActionClosureRegistry.add_execution()` repeats the same full execution scan on every successful act.
3. `StateStore.events()` materializes/JSON-decodes the complete event log.
4. `_current_runtime_boot_seq()` calls `StateStore.events()` and therefore scales linearly with total event history.
5. Several post-boot surfaces materialize full events and then filter after boot.

Required repair discipline:
- derive in-memory execution membership index from the same authoritative execution records; no new authority.
- populate it through all load/add paths and verify restart equivalence.
- add query-indexed state-store primitives for latest event of kind and suffix access; append-only chronology remains authority.
- only replace full scans where semantics are byte/result-equivalent and the query is exact.
- performance gate is scaling/ratio based, not a fragile absolute millisecond threshold.

## Priority discriminator B — boundary delimiter ownership
`CALLER_EVIDENCE_INGRESS != GROUPING_BOUNDARY_AUTHORITY`

Verified baseline violation:
`_derive_current_store_aware_bounded_operand_window()` resets the token window on ANY represented non-token EVIDENCE event. A caller can append arbitrary valid non-token evidence between two token pairs and thereby force the post-evidence pair to become the current arity-2 window, despite `caller_supplied_boundary = NO`.

This tranche must preserve historical lineage honestly. Do not silently rewrite the earlier evidence-delimiter law. First localize which non-token evidence classes have genuinely earned delimiter authority; if no general endogenous owner exists, add a new stricter current boundary substrate rather than laundering arbitrary evidence ingress into grouping authority.

## Soak gate
`SOAK_RESULT_WITH_HISTORY_COUPLED_LATENCY != CLEAN_DEVELOPMENTAL_MEASUREMENT`.
The 1200-episode developmental soak SHALL NOT be rerun or interpreted as clean developmental performance until the per-act growth gate passes.

## Hard ceilings
- indexing != cognition;
- cache/index != authority;
- performance equivalence must preserve exact execution refusal/idempotence semantics;
- no deletion or rewriting of append-only event/evidence history;
- no semantic delimiter, planner, scheduler, truth, or EFFECT authority from indexing;
- boundary hardening must not silently invalidate old evidence without replaying affected tests.

## Working laws
`AUTHORITY_RIGOR != SUBSTRATE_RIGOR`.
`ACCUMULATED_HISTORY != PER_ACT_LINEAR_WORK`.
`INDEXED_LOOKUP != NEW_AUTHORITY`.
`CALLER_BOUNDARY_ARGUMENT_ABSENCE != CALLER_GROUPING_INFLUENCE_ABSENCE`.
`CALLER_EVIDENCE_INGRESS != GROUPING_BOUNDARY_AUTHORITY`.
