# MS1934 — Fault Localization / Diagnostic Precision

Status: NON-NOVELTY ARCHITECTURE-FACTOR EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Does Microseed's explicit typed premise/event lineage localize one injected fault more precisely than a named centralized flat reason-vector baseline, and does any apparent advantage survive when a centralized fairness baseline receives equivalent typed trace/dependency information?

## Harness / receipt
Harness:
`tools/run_ms1934_fault_localization.py`
SHA-256:
`1129d48e26bc461efad4a6896ffeeb2cf9945851b2506b217e774b41451949d9`.

Receipt:
`reports/ms1934_fault_localization/receipt.json`
SHA-256:
`97f3cda8cdbeb2c0de96debcbac80f7db55de0f40c20f605640b238250a4a795`.

Durable job:
`job-2d3e20bff6a2`.
Exit 0.
Duration ~0.439 s.
Checks: 12/12 PASS.
Organism worktree clean.

## Fixture
Reused the already-verified MS1933 synthetic topology:
- 8 independent coordination branches `R0..R7`;
- one common counterparty `CP0`;
- 3 capabilities per branch (`Bi-0 -> Bi-1 -> Bi-2`);
- 24 capabilities total;
- one injected load-bearing fault per scenario;
- premise universe: 1 counterparty + 8 coordination relations + 24 capabilities;
- explicit typed dependency graph: 32 edges.

All scenarios preserve the same final CURRENT/STALE capability vector across compared diagnostic representations. The experiment changes diagnostic information, not authorization semantics.

## Baseline A — GLOBAL_DECISION_REASON_VECTOR_BASELINE
Centralized diagnostic representation containing:
- final per-capability CURRENT/STALE vector;
- generic changed-premise type (`COUNTERPARTY`, `COORDINATION`, or `CAPABILITY`);
- no premise-identity-to-context ancestry graph.

For capability faults the changed capability itself must be stale, so this baseline is legitimately allowed to narrow candidate roots to the stale capability set. It is not forced to consider all 24 capabilities when the final vector already provides narrower information.

Scope ceiling:
`SPECIFIC_NAMED_BASELINE_ONLY`.

## Baseline B — CENTRALIZED_TYPED_DEPENDENCY_TRACE_BASELINE
Fairness control.

The centralized owner receives:
- the same final capability vector;
- equivalent typed origin-event identity/reason lineage;
- the explicit 32-edge dependency graph.

It therefore receives the information required to run the same origin extraction as Microseed.

Purpose:
separate the value of explicit trace/dependency information from the physical distribution of authority owners.

## Actual Microseed trace shape
The experiment uses only emitted store events.

Examples:
- relation drift emits `OPERATIONAL_COORDINATION_INVALIDATED` containing exact `coordination_id`, epoch, reason, direct dependent, followed by `CAPABILITY_INVALIDATED` carrying stale closure and causal reason `COORDINATION:<id>:...`;
- capability drift emits `CAPABILITY_INVALIDATED` with exact `root`, reason and stale closure;
- shared counterparty drift emits `OPERATIONAL_COUNTERPARTY_INVALIDATED` for `CP0`, then eight causally attributed coordination invalidations, then eight branch capability invalidations.

The injected opaque reason string is identical across all scenarios; exact-origin extraction therefore cannot cheat by reading the scenario name/type from the reason text.

## Results

### A — coordination-specific fault (`R3`)
Final stale capabilities:
`B3-0`, `B3-1`, `B3-2`.

Microseed typed trace:
- candidate roots: `{COORDINATION:R3}`;
- candidate count: 1;
- false positives: 0;
- exact unique localization: YES.

Flat centralized reason vector:
- knows a coordination premise changed but lacks mapping from stale capability contexts to a specific coordination ID;
- candidates: all 8 coordination relations;
- candidate count: 8;
- false positives: 7;
- exact unique localization: NO.

Centralized typed-trace fairness baseline:
- candidate roots: `{COORDINATION:R3}`;
- candidate count: 1;
- false positives: 0;
- exact unique localization: YES.

### B — branch-root capability fault (`B3-0`)
Final stale capabilities:
`B3-0`, `B3-1`, `B3-2`.

Microseed:
- candidate count 1 (`B3-0`), false positives 0.

Flat centralized reason vector:
- changed premise type is capability;
- final stale vector legitimately narrows changed root to one of the 3 stale capabilities;
- candidate count 3;
- false positives 2.

Centralized typed-trace baseline:
- candidate count 1 (`B3-0`), false positives 0.

### C — leaf capability fault (`B3-2`)
Only `B3-2` is stale.

All three representations uniquely localize `B3-2`.
The flat baseline needs no ancestry graph because the final stale vector already contains one possible changed capability.

### D — shared counterparty fault (`CP0`)
All 24 capabilities stale.

All three representations uniquely localize `CP0` because the fixture contains exactly one counterparty and the generic changed-premise type is COUNTERPARTY.

Microseed's emitted trace is much larger in this broad scenario (17 invalidation events) because it explicitly records causal propagation through all eight relations and capability closures. This is trace richness/overhead, not an unqualified advantage.

## Fairness result
The centralized typed-dependency-trace baseline matched Microseed candidate roots **exactly in all four scenarios**.

This is the load-bearing negative result.

Rejected overclaim:
`PHYSICAL_DISTRIBUTION_OF_AUTHORITY_OWNERS_CAUSES_UNIQUE_DIAGNOSTIC_PRECISION`.

Earned engineering statement under this fixture:
`DIAGNOSTIC_PRECISION_FOLLOWS_EXPLICIT_TYPED_TRACE_INFORMATION_UNDER_THIS_FIXTURE`.

Companion:
`EQUIVALENT_TYPED_TRACE -> EQUIVALENT_FAULT_LOCALIZATION`.

## Diagnostic information / overhead observation
The richer trace can cost more bytes than a flat vector:
- coordination fault: Microseed diagnostic payload ~979 bytes vs flat ~467 bytes; centralized typed trace ~1161 bytes;
- shared counterparty fault: Microseed ~5150 bytes vs flat ~425 bytes; centralized typed trace ~1114 bytes under the compact fairness representation.

These byte counts are representation-specific and NOT a benchmark of runtime performance. They demonstrate a real precision/trace-richness tradeoff that should be measured explicitly rather than assuming richer diagnostics are free.

## Interpretation
MS1934 narrows the residual architecture claim further.

The measurable value is not that authority owners are physically distributed. The value in this experiment comes from keeping explicit typed origin and causal dependency information available at invalidation time.

A centralized architecture can reproduce the same localization when it maintains the same information.

Therefore future architecture comparisons should ask about:
- cost of maintaining that trace/dependency information;
- mutation/failure coupling when the trace is centralized versus locally owned;
- requalification/update complexity;
- trace compression without losing root-cause precision;
- developmental acquisition/reuse of the dependency structure.

## Novelty posture
Unchanged:
`UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

This is an engineering/science result only.

## Next Pareto-useful discriminator
The strongest next question is now **authority-coupling / fault-containment under equal mutation budget**:

> when one authorization/trace component is mutated incorrectly, does local typed ownership limit the number of logically unrelated authority judgments that can be corrupted compared with a named centralized coupled implementation, and does any advantage survive a centralized implementation that preserves independent typed submodules?

The same fairness discipline must apply: do not compare modular local owners to an intentionally monolithic strawman without also testing a modular centralized control.
