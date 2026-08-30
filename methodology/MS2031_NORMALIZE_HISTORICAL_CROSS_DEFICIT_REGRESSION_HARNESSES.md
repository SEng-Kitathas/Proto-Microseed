# MS2031 — NORMALIZE HISTORICAL CROSS-DEFICIT REGRESSION HARNESSES

## Why this campaign exists
MS2030 repaired the historical MS2025 stale-selection violation and promoted the MS2026 effect-time adapter into native runtime behavior. The current whole suite then failed because historical test code still demanded pre-repair behavior.

Git history already preserves the original MS2025 violation and MS2026 adapter exactly. The live branch must test current law rather than require repaired bugs to remain executable.

## First normalization pass
- MS2025 was rebound to the promoted runtime-owned selection/nomination path. It now passes by proving the historical stale-selection violation is closed: a new equal P4 competitor makes fresh selection UNKNOWN and native execution returns `CURRENT_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION` with zero handler calls.
- MS2026 was partially rebound to runtime-owned nomination but retained the old scratch adapter's identity comparison.

## First normalization result — PARTIAL FAILURE, preserved
Focused MS2025/MS2026/MS2030 run: 4 passed / 2 failed.
Both failures are MS2026 only.

The historical adapter compares its fresh scratch opportunity's selected deficit id (`MS2021-OP-*`) to the promoted runtime durable selection id (`OWNED-REFERENT-OP-*`). These are independently reconstructed lineage identities over the same current opportunity content. Forcing them equal would violate the project's lineage discipline.

Classification:
`HISTORICAL_SCRATCH_OPPORTUNITY_ID != PROMOTED_RUNTIME_OPPORTUNITY_ID`.

The adapter is therefore superseded, not repaired by aliasing ids. Current MS2026 replay should prove that the native MS2030 gate supplies the behavior the adapter originally established: stable selected P2 executes through ordinary EFFECT; new equal competitor blocks before EFFECT; no scheduler or persistent opportunity registry is introduced.

This partial-failure state is intentionally committed before updating the MS2026 current regression harness.
