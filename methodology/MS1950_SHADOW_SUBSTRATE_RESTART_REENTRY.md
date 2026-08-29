# MS1950 — Shadow Substrate Restart / Reality Reattachment

Date: 2026-08-29 ET
Status: Research ↔ Reality restart embodiment; shadow adapter remains unpromoted
Parent reality tranche: MS1949

## Question
Can persisted developmental competence survive process restart while live environment action authority remains absent, then reconnect lawfully when the environment adapter explicitly reattaches current operational contracts and handlers?

## Experiment
Scratch:
`scratch/ms1950_shadow_substrate_restart_reentry.py`

Phase 1:
- attach `CHARGE-WORLD` through the shadow adapter;
- learn and externally qualify the `CHARGE -> LEVEL-2` predictive relation from actual history;
- create a zero-row rehearsal proposal;
- verify current YES action commitment;
- close Microseed cleanly.

Phase 2:
- reopen `Microseed(root)` from the same persistent store with no environment adapter attached;
- verify the learned relation and rehearsal proposal replay from history;
- verify no current `CHARGE` capability/handler exists;
- inspect currentness before reattachment.

Phase 3:
- attach a fresh `CHARGE-WORLD` adapter instance with a new adapter instance identity;
- verify current operational contracts are re-established;
- verify the exact persisted relation/proposal become current again only after reattachment;
- execute the historical proposal through fresh current action authority and observe the actual world outcome.

## Reality seam discovered
First restart attempt `job-5958b26bd3f8` failed before reentry because adapter attachment reused a persistent evidence ID and SQLite correctly rejected the duplicate.

This localized another substrate requirement:
`WORLD_IDENTITY != ADAPTER_ATTACHMENT_INSTANCE_ID`.

A reusable adapter must namespace capture/evidence identities by attachment/session instance across organism lifetime.

The shadow adapter therefore gained explicit `adapter_instance_id`; no Microseed-core code changed.

## Final result
`job-47e153aaecc2` — PASS.

Before restart:
- relation = CURRENT;
- proposal = CURRENT.

After restart but before adapter attachment:
- relation = `STALE_PREDICTIVE_RELATION / STRUCTURAL_PREMISE_NOT_CURRENT`;
- proposal = `UNKNOWN_INCOMPLETE / REHEARSAL_CAPABILITY_NOT_CURRENT:CHARGE`;
- no live `CHARGE` capability exists.

After fresh adapter reattachment:
- the same persisted relation = CURRENT;
- the same persisted proposal = CURRENT;
- ordinary bounded commitment again returns YES;
- a fresh current action intent executes;
- actual external outcome = `LEVEL-2`.

Earned bounded statement:
`PERSISTED_DEVELOPMENTAL_COMPETENCE_CAN_RECONNECT_TO_REALITY_AFTER_RESTART_ONLY_AFTER_EXPLICIT_CURRENT_ENVIRONMENT_REATTACHMENT`.

Preserve:
- `HISTORICAL_COMPETENCE != CURRENT_OPERATIONAL_AUTHORITY`;
- `REPLAYED_MODEL != REAUTHORIZED_EFFECT_CAPABILITY`;
- `REATTACHMENT != NEW_LEARNING`;
- `PERSISTENCE != AUTOMATIC_EXECUTION_PERMISSION`.

## Substrate implication
This is a strong candidate invariant for an honest substrate:
- developmental evidence/models persist;
- environment authority is ephemeral/current and must be reacquired;
- reattachment may make historical competence usable again only when exact current structural premises match.

## Next discriminator
Sustained run / repeated restart pressure: does this separation remain stable across multiple attachment sessions and continued post-reentry learning, rather than only one restart?