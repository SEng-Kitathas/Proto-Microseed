# MS2041 — REPAIR EFFECT-TIME FULL-FRAME SELECTION REAUTHORIZATION

## Trigger
MS2040 proved that a production full-frame selected-origin deficit could bypass effect-time cross-deficit reauthorization because `_fresh_action_commitment_for_intent` recognized only the historical same-value selected-origin marker.

## Goal
Repair ordinary execution without weakening the historical same-value gate or moving EFFECT authority out of `CapabilityRegistry.invoke`.

## Design
1. Add a distinct full-frame selected execution-premise commitment in `development/epistemic_action.py` rather than broadening the old same-value function's accepted target/authority.
2. In `_fresh_action_commitment_for_intent`, detect the full-frame durable marker separately from the same-value marker.
3. Validate exact selected endogenous UNKNOWN ancestry:
   - source `MICROSEED_ENDOGENOUS_SELECTED_FULL_FRAME_EPISTEMIC_OPPORTUNITY`;
   - kind `SELECTED_OWNED_REFERENT_FULL_FRAME_EPISTEMIC_UNKNOWN`;
   - exact durable deficit/probe;
   - authority `STRICT_FULL_FRAME_PARETO_REGULATORY_DOMINANCE_ONLY`;
   - nomination selection commitment id present;
   - nomination frame digest present.
4. Re-derive the current full-frame selection surface at EFFECT time.
5. Require exact current selected deficit/probe and full-frame selection authority.
6. Reconstruct the fresh full-frame selection commitment from current vectors/frame and conjoin it with the exact current local step commitment.
7. Preserve in execution premises:
   - local commitment id/premises;
   - fresh full-frame selection commitment id/premises;
   - selected endogenous UNKNOWN evidence id;
   - nomination-time full-frame selection commitment id;
   - nomination-time frame digest.
8. Ordinary capability invocation remains the sole EFFECT owner.

## Hostiles
- stable full-frame P2 winner executes exactly once and records nomination + fresh selection ancestry;
- add current observed X with no action/X effects after nomination -> NO_EXECUTION before handler;
- forged selected UNKNOWN pointer/source/kind/authority -> fail closed;
- historical MS2030 same-value effect-time reauthorization remains green;
- execution authority on selection/combined commitments remains NONE.

## Expected repair laws
`FULL_FRAME_SELECTED_ORIGIN_REQUIRES_FRESH_FULL_FRAME_SELECTION_AT_EFFECT`.

`SELECTION_AUTHORITY != EXECUTION_AUTHORITY` remains exact.


## Observed result — EFFECT-TIME FULL-FRAME REAUTHORIZATION GREEN
Direct MS2041 witness PASS. Cleanup-neutral focused MS2029/MS2030 + MS2039–MS2041 lineage: **13/13 PASS in 41.78s**, stderr empty.

Observed:
- stable current full-frame P2 winner executes exactly once;
- execution record preserves local commitment ancestry + fresh full-frame selection commitment ancestry + selected UNKNOWN evidence id + nomination selection commitment id + nomination frame digest;
- new current observed X without action/X effects -> `NO_EXECUTION` / `CURRENT_FULL_FRAME_CROSS_DEFICIT_SELECTION_REQUIRED_AT_EXECUTION`, zero handler calls;
- forged selected UNKNOWN pointer fails closed before effect;
- historical same-value MS2030 effect-time reauthorization remains green;
- ordinary EFFECT owner remains `CapabilityRegistry.invoke`;
- selection and combined premise commitments carry execution authority NONE.

Current-branch MS2040 regression now reports `HISTORICAL_VIOLATION_CLOSED`; the original violation remains preserved at commit `b1e7598e026901f5b90523dfb9454f943f048265`.

Earned:
`FULL_FRAME_SELECTED_ORIGIN_REQUIRES_FRESH_FULL_FRAME_SELECTION_AT_EFFECT`.

`SELECTION_AUTHORITY != EXECUTION_AUTHORITY` remains exact.
