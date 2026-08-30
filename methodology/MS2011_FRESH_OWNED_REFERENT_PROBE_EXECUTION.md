# MS2011 — FRESH OWNED REFERENT PROBE EXECUTION

## Question
Can an internally-derived decision-bearing referent probe execute through ordinary `execute_bounded_action()` only after the runtime freshly reconstructs the owned referent decision surface, rather than trusting caller-cached alternatives?

## Embodiment
A narrow fresh-context adapter sits beside the existing revised-direct-probe adapter. It activates only for deficits whose assistance ancestry contains `DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY`. At execution it re-derives the current owned referent decision surface, checks the unique probe matches the trial step, checks exact probe relation ancestry, and replaces any caller decision context before the ordinary priority/information/action commitment is recomputed.

No new executor, registry, planner, authority or action basis is added. `execute_bounded_action()` remains the sole EFFECT path.

## Hostiles
- forged caller decision context is ignored; owned fresh surface still permits P2;
- duplicate current raw receipt after nomination destroys fresh surface and blocks before handler;
- regulatory pressure disappearing after nomination blocks before handler;
- forged trial source-relation ancestry is rejected even earlier by the existing nomination-time `PROGRAM_RELATION_ANCESTRY_MISMATCH` guard; the fresh execution guard remains defense in depth.

## Boundary
MS2011 executes P2 but does not yet claim the resulting observation closes the referent ambiguity or advances the epistemic trial. Actual outcome/observation closure is the next campaign.
