# MS1949 — Shadow Substrate Environment Adapter

Date: 2026-08-29 ET
Status: Research ↔ Reality shadow embodiment; production promotion NOT YET
Parent: MS1948 `9c0e0b8554da1f30d59fd5f7841311f8122e75a1`

## Question
Across distinct external world dynamics, can the unchanged Microseed core use one reusable external adapter shape to acquire actual action/outcome history, admit externally qualified predictive relations, and re-enter zero-row rehearsal without campaign-specific organism code?

## Embodiment
External shadow adapter:
`research/substrate_shadow/environment_adapter.py`

The adapter owns environment-side wiring only:
- current effect capabilities;
- current observation capability;
- bounded observation-use basis;
- frame/value/episode attachment;
- conversion of world observations into Microseed's required `next_state_id + value_id + observed_value` outcome shape;
- explicit equipped seed evidence for first action sampling;
- independent holdout generation from forked external world instances.

It grants no truth, semantic, or autonomous exploration authority.

Two world implementations were used with the same adapter:
1. `CHARGE-WORLD`: scalar resource accumulator, `CHARGE -> LEVEL-2`, value 2.4.
2. `PARITY-WORLD`: integer parity dynamics, `STEP -> ODD`, value 2.4.

Each action was learned from 12 actual Microseed executions/outcomes, independently holdout-qualified from fresh world forks, and reused through zero-row ordinary rehearsal before final actual execution.

## Reality seam discovered
Initial runs `job-640d8efb28a4` and `job-cb3e4b2fa465` exposed `ACTION_OUTCOME_FIELDS_MISSING`.

Cause: generic worlds supplied actual state and scalar value but not Microseed's configured `value_id` coordinate identity.

Repair was correctly made in the adapter, not the organism:
`WORLD_OBSERVATION_SCALAR != MICROSEED_VALUE_COORDINATE_ID`.

The adapter now binds the world scalar observation to its configured Microseed value coordinate.

## Final result
`job-96952fdda8bc` — PASS.

Earned bounded statement:
`ONE_EXTERNAL_SHADOW_ADAPTER_SHAPE_CAN_CONNECT_UNCHANGED_MICROSEED_CORE_TO_DISTINCT_WORLD_DYNAMICS_FOR_ACTUAL_HISTORY_QUALIFICATION_AND_ZERO_ROW_REHEARSAL`.

This does NOT yet establish a general substrate. It establishes a reusable external shadow boundary worthy of further reality pressure.

## Assistance boundary
First unknown action sampling is explicitly EQUIPPED by external seed evidence generated from a separate world probe. MS1947's NAKED normative block remains intact.

## Next discriminator
Restart/reentry: can persisted learned competence survive restart without silently restoring operational authority, then lawfully reconnect when the current environment adapter is explicitly reattached?
