# MS2030 — PROMOTE EFFECT-TIME CROSS-DEFICIT SELECTION REAUTHORIZATION

## Goal
Close the MS2025 stale-selection authority leak inside the ordinary epistemic execution path, while preserving ordinary EFFECT ownership and execution lineage.

## Runtime rule
After the existing local epistemic step is freshly re-derived and its commitment id still matches the nominated intent:
- if the durable deficit was not materialized from strict cross-deficit selection, legacy behavior is unchanged;
- if it was, validate the persisted selected-UNKNOWN evidence/ancestry;
- re-enumerate the current owned referent opportunity set;
- re-derive current strict same-value selection;
- require the same deficit/probe to remain uniquely selected;
- conjoin the current local step commitment with the current selection commitment;
- return that conjoined commitment to ordinary `execute_bounded_action`.

## Execution lineage
The conjoined execution commitment includes:
- local step commitment id + premises;
- fresh cross-deficit selection commitment id + premises;
- nomination-time selected UNKNOWN evidence id;
- nomination-time cross-deficit selection commitment id.

This is an execution-premise commitment only. `CapabilityRegistry.invoke` remains the sole EFFECT owner.

## Hostiles
1. Stable asymmetric P2 dominance -> execute exactly once; execution record contains fresh + nomination selection ancestry.
2. New equal P4 competitor after nomination -> current selection tie/UNKNOWN; `NO_EXECUTION`; zero handler calls.
3. Legacy MS2017 owned-observable execution without selected-origin marker remains green.
4. Forged/missing selected UNKNOWN ancestry fails closed.

## Scar closed
`NOMINATION_TIME_CROSS_DEFICIT_SELECTION != EFFECT_TIME_CROSS_DEFICIT_SELECTION_CURRENTNESS` is closed only for the bounded selected-owned-referent lineage; no generic scheduler or cross-value priority is introduced.


## First execution result — AUTHORITY VIOLATION, preserved
Stable and stale-competitor paths reached the intended gate, but the forged selected-UNKNOWN ancestry hostile reproduced a deeper authority bug. After nomination, the durable registry entry for the selected deficit was replaced in-memory with the same deficit content but `unknown_evidence_id` redirected to the current raw observation premise. The selected-origin marker remained. `execute_bounded_action` still returned `ACTION_EXECUTED` and fired P2.

Diagnosis: the MS2030 gate is reading the deficit object carried by `EpistemicStepExecutionContext` / trial derivation rather than first resolving the authoritative persisted deficit record from `self.epistemic_deficits.records`. The caller's ephemeral selected deficit still points at the legitimate selected UNKNOWN, so forged registry drift is invisible to the global gate.

Earned scar: `CALLER_EXECUTION_CONTEXT_DEFICIT != AUTHORITATIVE_PERSISTED_DEFICIT`.

More precise rule: any effect-time gate whose authority depends on durable deficit lifecycle/selected-UNKNOWN provenance SHALL resolve that deficit from the current deficit registry by id and compare it against the caller-carried trial context; caller context may supply trial/decision structure but not durable deficit authority.

Classification: `MS2030_PRE_REPAIR_AUTHORITY_VIOLATION`. This state is intentionally committed before repair.
