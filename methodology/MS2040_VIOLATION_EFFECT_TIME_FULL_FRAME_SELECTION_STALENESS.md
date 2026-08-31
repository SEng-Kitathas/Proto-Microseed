# MS2040 — VIOLATION: EFFECT-TIME FULL-FRAME SELECTION STALENESS

## Goal
Attack the production MS2039 nomination path at EFFECT time before repairing it.

## Hostile
1. Build a current full-frame P2 Pareto dominance fixture.
2. Capture the selected P2 owned opportunity/trial/decision context.
3. Nominate through production `nominate_current_strict_full_frame_referent_epistemic_opportunity`.
4. After nomination, register + observe a new current constitutional value X, but add no downstream action/X effect witnesses.
5. Re-derive the current full-frame selection surface. The frame expands to V/W/X; complete vectors are unavailable, so no current strict full-frame selection exists.
6. Call ordinary `execute_bounded_action` on the already-nominated P2 intent with the original current epistemic step context.

## Expected current violation
The current executor recognizes only the historical same-value selected-origin marker. The new full-frame marker is therefore expected to bypass global effect-time selection reauthorization and fall through to local step currentness.

If P2 executes despite the fresh full-frame selection surface being unavailable, earn:

`NOMINATION_TIME_FULL_FRAME_SELECTION != EFFECT_TIME_FULL_FRAME_SELECTION_CURRENTNESS`.

and:

`UNRECOGNIZED_SELECTED_ORIGIN_MARKER_BYPASSES_EFFECT_TIME_GLOBAL_SELECTION_REAUTHORIZATION`.

## Nonclaim
This campaign intentionally reproduces a violation. It does not repair it.


## First run — HARNESS OPPORTUNITY SHAPE FAILURE
The first direct run failed before the execution verdict because the scratch hostile took `by_probe["P2"]` from the public opportunity summary surface, which intentionally omits internal `trial` and `decision_context` objects needed to build `EpistemicStepExecutionContext`.

Classification:
`MS2040_HARNESS_PUBLIC_SUMMARY_NOT_INTERNAL_OPPORTUNITY_SHAPE__NO_SCIENTIFIC_VERDICT`.

The intended hostile remains unchanged. Repair shall recover the exact selected current internal opportunity through `_current_owned_referent_epistemic_opportunities` before nomination.


## Repair 1 — recover exact internal selected opportunity
Narrow harness repair only: retrieve the exact current internal P2 opportunity via `_current_owned_referent_epistemic_opportunities` before nomination so the existing trial/decision context can be supplied to ordinary execution. Public summary semantics remain unchanged.


## Observed result — VIOLATION REPRODUCED
After the published harness-shape failure, Repair 1 recovered the exact internal selected P2 opportunity before nomination. Direct hostile then reproduced the intended violation:

- production full-frame nomination succeeded for P2;
- a new current observed X expanded the constitutional frame to V/W/X without downstream action/X effect witnesses;
- fresh runtime full-frame selection became `NO_CURRENT_STRICT_FULL_FRAME_CROSS_DEFICIT_SELECTION`, reason `CURRENT_DOWNSTREAM_ACTION_VALUE_EFFECT_REQUIRED:A:X`, selection authority NONE;
- ordinary `execute_bounded_action` nevertheless returned `ACTION_EXECUTED`;
- P2 handler fired once;
- execution record contained only the local epistemic-step premise set, not full-frame nomination/current selection ancestry.

Earned violation:
`NOMINATION_TIME_FULL_FRAME_SELECTION != EFFECT_TIME_FULL_FRAME_SELECTION_CURRENTNESS`.

More precise:
`UNRECOGNIZED_SELECTED_ORIGIN_MARKER_BYPASSES_EFFECT_TIME_GLOBAL_SELECTION_REAUTHORIZATION`.

This violation SHALL remain in research Git. Repair follows in a later campaign.
