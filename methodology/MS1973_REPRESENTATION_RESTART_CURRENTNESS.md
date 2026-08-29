# MS1973 — Representation Restart / Exact-Premise Currentness

Date: 2026-08-29 ET
Status: process-backed restart/currentness pressure; no Microseed-core mutation
Parent: MS1972 `9621a62756258399042d5f17056331874469c192`

## Question
After process/frame/capability bindings disappear at restart, does a persisted history-derived refinement/projection remain unusable until exact current premises are reattached? Can a same-id/same-epoch but content-incompatible frame silently reactivate old history?

Prewrites:
- `PERSISTED_PROJECTION_RECORD != CURRENT_USABLE_REPRESENTATION`;
- `FRAME_ID_AND_EPOCH_MATCH != FRAME_CONTENT_MATCH`;
- `REATTACHMENT != SEMANTIC_REINSTATEMENT`;
- `REGISTRY_CURRENT_FLAG != SUFFICIENT_USE_AUTHORITY`.

## Experiment
Scratch:
`scratch/ms1973_representation_restart_currentness.py`

First life reuses the MS1972 process-backed alias world and earns one externally qualified generic projection from four actual two-step histories.

Projection id: `P-MS1973`.

### Restart with no live environment attachment
The durable `EpistemicProjectionRecord` replays from the event store, including its record-local `current=True` flag.

However:
- no current action capability exists;
- admitted transition samples cannot be re-derived;
- `derive_admitted_one_step_visible_history_refinements()` returns `NO_ONE_STEP_VISIBLE_HISTORY_REFINEMENT`;
- attempting a new generic admission with the old qualification ticket fails `CURRENT_HISTORY_REFINEMENT_FOR_TICKET_NOT_FOUND`.

Thus the replayed projection record is historical state, not sufficient current-use authority.

### Same-id/same-epoch incompatible frame hostile
The runtime is reattached with the exact MS1972 action/observation capability contract shapes, but operational frame `F@0` has a different content signature.

Every old transition sample is rejected specifically as:
`OPERATIONAL_FRAME_CONTENT_DRIFT`.

The old refinement does not reappear.

This confirms observation-admission receipts bind exact frame content, not only frame id/epoch.

### Compatible reattachment
A fresh compatible process world and exact compatible frame/capability contracts are attached in a new Microseed runtime.

Owned durable action/outcome history re-projects successfully and re-derives exactly one refinement whose digest matches the persisted projection signature.

No semantic context labels, hidden-state identities, or replacement projection content are supplied at reentry.

## Execution
Initial broad run:
`job-86cfcb474197` PASS.

Strengthened exact frame-content hostile:
`job-441e1e74157d` PASS / rc=0.

Earned:
`PERSISTED_HISTORY_REFINEMENT_RECORD_DOES_NOT_RESTORE_USABLE_REPRESENTATION_WITHOUT_CURRENT_EXACT_PREMISES_AND_COMPATIBLE_REATTACHMENT_REDERIVES_THE_SAME_OPAQUE_CONTENT`.

## Important currentness distinction
`EpistemicProjectionRecord.current` is registry-record currentness only. For history-derived projections it is not by itself sufficient to establish current usability after restart.

Actual use remains gated by re-derivation from current authenticated history/premises and, for projection-conditioned consumers, current relation/current-surface checks.

Preserve:
`REGISTRY_CURRENT_FLAG != CURRENT_CONTENT_RECOVERABILITY != CONSEQUENCE_AUTHORITY`.

## Authority ceiling
- truth authority NONE;
- hidden-state authority NONE;
- semantic-category authority NONE;
- language authority NONE;
- automatic reauthorization NONE.

## Next discriminator
Pressure a process-backed alias where **previous visible state is also identical** and only deeper visible history distinguishes the operational outcomes.

Question:
Can existing projection/discovery/constructor owners compose a deeper history-derived discriminator from owned evidence, or does MS1973 expose a genuinely missing bounded history-depth growth owner?

Do not add generic memory/ontology machinery unless composition first fails.