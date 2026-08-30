# MS2025 — EFFECT-TIME CROSS-DEFICIT SELECTION STALENESS HOSTILE

## Question
Does ordinary epistemic effect-time reauthorization preserve the MS2023 cross-deficit selection premise, or can a probe execute after the global competitor set changes even though its selected deficit remains locally current?

## Hostile
1. Use the MS2024 asymmetric fixture: P2 worst residual pressure 0.0, weak P4 worst residual 0.5. Strict selection nominates P2 and persists only its selected deficit.
2. Before EFFECT, add a new separately qualified current P4 referent routing whose alternative-conditioned downstream C/D actions both reach residual pressure 0.0 on the same exact current V coordinate.
3. Re-enumerate: P2 and the new P4 opportunity now tie at worst residual 0.0, so no strict cross-deficit selection commitment exists.
4. Execute the already-nominated P2 through ordinary `execute_bounded_action` with the selected trial/decision context.

## Observed result — VIOLATION REPRODUCED
- nomination-time selected probe: P2;
- new independently qualified P4 competitor becomes current after nomination;
- fresh opportunity surface contains P2 and P4;
- fresh same-value comparison: `NO_STRICT_SAME_VALUE_REGULATORY_DOMINANCE`, reason `WORST_RESIDUAL_PRESSURE_TIE`;
- fresh cross-deficit selection commitment: UNKNOWN, selection authority NONE;
- selected P2 deficit and its local referent/priority/information premises remain current;
- ordinary `execute_bounded_action` returns `ACTION_EXECUTED`;
- P2 handler fires exactly once.

Therefore local selected-deficit reauthorization is insufficient to preserve the premise that made P2 the unique cross-deficit winner.

Earned scar:
`NOMINATION_TIME_CROSS_DEFICIT_SELECTION != EFFECT_TIME_CROSS_DEFICIT_SELECTION_CURRENTNESS`.

More precise authority boundary:
`CURRENT_SELECTED_DEFICIT != CURRENT_COMPETITOR_SET`.

This violation must remain in history before repair. It does **not** imply a generic scheduler. The missing requirement is narrower: effect-time authorization for an action whose nomination depended on cross-deficit selection must re-derive that exact selection over the current competitor surface, or fail closed.
