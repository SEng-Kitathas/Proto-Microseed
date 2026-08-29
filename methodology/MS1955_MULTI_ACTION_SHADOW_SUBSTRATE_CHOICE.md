# MS1955 — Multi-Action Shadow Substrate Choice

Date: 2026-08-29 ET
Status: research ↔ reality shadow-substrate embodiment
Parent: MS1954 `f6fb2ed278b88d39bc8f73fe38668bb757c8f4d8`

## Question
Can one external substrate world expose multiple already represented actions with different learned regulatory consequences, have each consequence learned/qualified from actual interaction, and let ordinary zero-row Microseed rehearsal select the better action rather than identifier order?

## World
`ChoiceWorld` exposes:
- `ACT-A`;
- `ACT-Z`.

Regulatory viable interval is supplied as `[3.0, 4.0]` and initial value is `0.0`.

Both actions improve pressure and therefore can independently earn bounded action commitments after external equipped seeding:
- stronger effect = `3.2` -> residual pressure 0;
- weaker effect = `2.5` -> residual pressure 0.5.

Each action is trained from 12 actual executions/outcomes and separately qualified through a structurally separate matched qualification source.

## Identity-reversal pressure
Two worlds use the same action ids but reverse which id has the stronger real effect.

World A:
- `ACT-A -> 3.2`;
- `ACT-Z -> 2.5`.

World B:
- `ACT-A -> 2.5`;
- `ACT-Z -> 3.2`.

Both individual actions receive `YES / BOUNDED_REHEARSAL_PREDICTS_LOWER_REGULATORY_PRESSURE` when considered alone.

## Result
Scratch:
`scratch/ms1955_multi_action_world_choice.py`

Job `job-f4387b5a9046` PASS.

Observed:
- World A winner = `ACT-A`;
- World B winner = `ACT-Z`;
- winner predicted effect = 3.2 in both;
- final actual state/value = `HIGH / 3.2` in both;
- lexical order loses when the later id has the better learned consequence.

Earned statement:
`MULTI_ACTION_SHADOW_SUBSTRATE_SELECTION_FOLLOWS_LEARNED_REGULATORY_CONSEQUENCE_NOT_OPAQUE_IDENTIFIER_ORDER`.

Preserve:
- `LEARNED_CONSEQUENCE_SELECTION != SEMANTIC_PREFERENCE`;
- `MULTI_ACTION_ENVIRONMENT != GENERAL_POLICY_AUTHORITY`;
- `IDENTIFIER_ORDER_ONLY_BREAKS_MODELED_TIES`.

No Microseed-core mutation was required.