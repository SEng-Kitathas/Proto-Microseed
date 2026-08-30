# MS1933 — Invalidation / Requalification Blast-Radius Experiment

Status: NON-NOVELTY ARCHITECTURE-FACTOR EXPERIMENT.
Date: 2026-08-29 ET.
No organism source mutation. No canonical promotion.
Sealed organism head during run: MS1924 `6b0f012980a625143ea7137be848d6f13b57325b`.

## Question
Does Microseed's declared dependency/currentness graph measurably reduce requalification blast radius for a local premise change compared with a named centralized invalidation baseline, while still propagating broadly when the changed premise is genuinely shared?

This is an engineering/science question, not a novelty discriminator.

## Named baseline
`GLOBAL_AUTHORIZATION_EPOCH_BASELINE`.

Definition:
- every active capability authorization context is bound to one global authorization epoch;
- any load-bearing premise change increments that epoch;
- all active contexts must recheck before use;
- those rechecks may use the same underlying local owners, so final/extensional decisions can still match Microseed after revalidation.

Scope ceiling:
`SPECIFIC_NAMED_BASELINE_ONLY_NOT_ALL_GLOBAL_MANAGERS`.

The experiment does NOT claim all centralized managers require global invalidation.

## Fixture
Fresh temporary Microseed fixture per scenario:
- one common current counterparty `CP0`;
- 8 independently current coordination relations `R0..R7`, each qualified against `CP0`;
- one 3-capability transitive chain per relation;
- 24 current capabilities total.

Each branch:
`Ri -> Bi-0 -> Bi-1 -> Bi-2`.

Only the root capability is directly bound to its coordination relation; capability currentness then propagates through the declared transitive dependency chain.

## Harness
`tools/run_ms1933_invalidation_blast_radius.py`
SHA-256:
`9f820b473c68b2ef69e769111c568035483fb06f62a87ecb4c153e21ce4abf2c`.

Final receipt:
`reports/ms1933_invalidation_blast_radius/receipt.json`
SHA-256:
`5ba2d9a17618f2ef4606aa0646d5c6fb06f1ac3794bff432908811f98998de65`.

## Execution history
First job `job-93940c832054` was INVALID_RUN: the experiment reached its first fixture but Windows temp cleanup failed because Microseed SQLite stores remained open. This was a harness lifecycle failure, not a scientific negative.

The harness was repaired only to close `biography`, `evidence`, and event-store SQLite connections before temporary-directory cleanup.

Final durable job:
`job-63b5358b1410`.
Exit 0.
Duration ~0.444 s.
Checks: 10/10 PASS.
Organism worktree clean at run time.

## Results

### A — coordination-specific drift
Changed premise:
`R3` only.

Observed Microseed closure:
- stale relation count: 1 (`R3`);
- stale capabilities: `B3-0`, `B3-1`, `B3-2`;
- local recheck/stale count: 3 / 24;
- unrelated capabilities remaining current: 21 / 24.

Named global-epoch baseline:
- recheck count: 24 / 24.

Measured difference:
- 21 unrelated rechecks avoided;
- 8.0× smaller recheck blast radius.

### B — root capability drift
Changed premise:
`B3-0`.

Observed Microseed closure:
- stale capabilities: `B3-0`, `B3-1`, `B3-2`;
- local recheck/stale count: 3 / 24;
- unrelated current: 21 / 24.

Named global baseline:
24 / 24 rechecks.

Measured difference:
- 21 unrelated rechecks avoided;
- 8.0× smaller blast radius.

### C — leaf capability drift
Changed premise:
`B3-2`.

Observed Microseed closure:
- stale capability: `B3-2` only;
- local recheck/stale count: 1 / 24;
- unrelated current: 23 / 24.

Named global baseline:
24 / 24 rechecks.

Measured difference:
- 23 unrelated rechecks avoided;
- 24.0× smaller blast radius.

### D — genuinely shared counterparty drift
Changed premise:
`CP0`, which all eight coordination relations depend on.

Observed Microseed closure:
- all 8 coordination relations stale;
- all 24 capabilities stale;
- local recheck/stale count: 24 / 24;
- unrelated current: 0.

Named global baseline:
24 / 24 rechecks.

Measured difference:
- no rechecks avoided;
- locality gain 1.0×.

## Interpretation
The local dependency/currentness design is not simply "always more selective." It tracks declared dependency topology:
- narrow premise drift produces narrow transitive invalidation;
- leaf drift produces a still narrower closure;
- shared upstream drift correctly propagates across every dependent branch.

Against the specific global-epoch baseline, this creates a measurable requalification-work advantage when reality changes locally and no advantage when reality changes globally.

Earned engineering statement:
`DECLARED_DEPENDENCY_LOCALITY -> BOUNDED_INVALIDATION_BLAST_RADIUS` under this fixture/baseline.

Also preserved:
`SHARED_PREMISE_DRIFT -> SHARED_INVALIDATION_CLOSURE`.

## What this does NOT prove
- It does not prove behavioral novelty.
- It does not prove every global manager has a larger blast radius.
- It does not prove wall-clock speedup; it measures required invalidation/recheck set size under the named model.
- It does not establish real-world distribution statistics of local vs global drift.
- It does not prove local factorization is always preferable; centralized systems can maintain fine-grained dependency indexes too.
- It does not change the novelty posture.

## Current scientific value
This is the first concrete positive measurement for one residual architecture-factor hypothesis after the novelty demotion chain:

> local declared dependency ownership can reduce requalification blast radius relative to a simple global-epoch invalidation design without weakening propagation when the changed premise is actually shared.

Classification:
`MEASURED_ENGINEERING_PROPERTY_UNDER_NAMED_BASELINE`.

Novelty remains:
`UNKNOWN / NOT_ENTITLED_TO_CLAIM`.

## Next useful discriminator
The next Pareto-useful architecture experiment should pressure whether locality also improves **fault localization / diagnostic precision** under equal mutation budget, not merely invalidation set size.

A fair test should preserve final YES/NO/UNKNOWN behavior while comparing how narrowly a single injected premise fault can be localized from emitted reason/premise lineage under a named baseline. If the central baseline is allowed the same full typed trace, no diagnostic advantage should be assumed.
