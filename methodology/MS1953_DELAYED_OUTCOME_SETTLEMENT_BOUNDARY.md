# MS1953 — Delayed Outcome Settlement Boundary

Date: 2026-08-29 ET
Status: pre-repair timing violation reproduced; shadow-adapter repair verified
Parent: MS1952 `b466ebca72eb52d5cd60149fc3e409de12b44792`

## Question
Can the shadow substrate handle an environment where the immediate post-effect state is not yet the action's settled consequence?

Prewrite:
- `IMMEDIATE_POST_EFFECT_OBSERVATION != SETTLED_ACTION_OUTCOME`;
- `ACTION_HANDLER_RETURN != OUTCOME_SETTLEMENT`;
- `CURRENT_STATE_SNAPSHOT != ACTION_CLOSURE_OBSERVATION`.

## World
`DelayedChargeWorld`:
- action `CHARGE-DELAYED` schedules an effect for two external ticks;
- immediate observation = `PENDING`, value `0.0`;
- settled observation after two ticks = `LEVEL-2`, value `2.4`.

## Pre-repair violation
Job `job-fdebcb2f9785` reproduced the hidden synchronous assumption:
- adapter equipped seed rows used immediate `PENDING` as final outcome;
- predicted effect = 0.0;
- bounded action commitment = UNKNOWN / `NO_DISCRIMINATING_REGULATORY_ADVANTAGE`;
- meanwhile the same external world settles to `LEVEL-2 / 2.4`.

Thus the adapter could not lawfully collect the useful delayed history even though the external effect was real.

## Minimum repair
The external world protocol now distinguishes:
- `observe()` = current-state snapshot;
- `observe_outcome()` = externally settled observation appropriate for closing the action outcome.

The Microseed observation capability uses `observe_outcome()` only at action closure. Ordinary control-state attachment/reset still uses `observe()`.

Synchronous worlds implement `observe_outcome() == observe()`.
Delayed worlds own their own settlement mechanism; Microseed receives only the settled authenticated outcome and is not given semantic timing rules.

## Post-repair result
Boundary rerun `job-84c324f40fdb`:
- adapter seed = `LEVEL-2`, effect 2.4;
- commitment = YES / `BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE`;
- immediate world state remains separately observable as `PENDING / 0.0`.

Full delayed reality run `job-adfacb54d79f`:
- 12 actual delayed executions settle through the external observation boundary;
- candidate support = 12, consistency = 1.0;
- candidate evidence carries exact `SUBSTRATE-ENV-BINDING` signature ancestry;
- externally qualified relation predicts `LEVEL-2 / 2.4`;
- zero-row rehearsal reuses it;
- final actual execution observes `LEVEL-2 / 2.4`.

Earned statement:
`DELAYED_WORLD_OUTCOMES_CAN_SETTLE_AT_EXTERNAL_OBSERVATION_BOUNDARY_BEFORE_MICROSEED_ACTION_CLOSURE`.

No Microseed-core mutation was required.

## Substrate implication
A general environment adapter needs an explicit outcome-settlement boundary. Immediate state observation is not universally equivalent to action outcome completion.

This is an external environment/runtime concern, not a semantic cognition primitive.