# P06 Attribution Report — Grounded Causal Schema Abstraction and Cross-Context Transfer

## Training evidence
Veya owns two P05 two-step causal chains from concretely disjoint contexts: their capability IDs and state labels do not overlap. Each chain was itself grounded in independently qualified action→outcome relations, owned P03 concepts, P04 couplings, and P05 state-join composition.

## New abstraction
P06 compares the owned chains and extracts only structure shared across them:
- two empirical edges;
- three state roles with an exact middle-state join;
- the sequence of grounded concept-content identities;
- the sign roles of step value effects.

Concrete training capability IDs and state labels are deliberately excluded from schema content. One context alone, or two overlapping concrete contexts, cannot qualify as abstraction.

## Cross-context transfer
The schema is applied to a third held-out context with new capability IDs, new state labels, and a separate P03 concept set whose **surface words are swapped**. Transfer resolves the grounded concept-content roles, selects the corresponding current held-out empirical couplings, requires the exact state join and effect-role pattern, and produces a concrete held-out chain prediction.

A fresh actual held-out execution matches the transferred capability sequence, state path, and cumulative value effect.

## Negative transfer
- broken held-out state join: refused;
- effect-sign role mismatch: refused;
- text-only schema assertion: refused;
- forged/unowned schema: refused;
- one-context or overlapping-context pseudo-abstraction: refused;
- held-out relation drift: blocks transfer;
- held-out concept-grounding drift: blocks transfer.

## Language role
Language remains useful in concept indexing/remapping, but schema identity is grounded in owned concept-content digests and empirical structural roles rather than spelling. Swapping words in the held-out context does not change the transferred structural role when grounding is preserved.

## Capability attribution
This is a legitimate abstraction/generalization gain: Veya carries structure learned in multiple grounded contexts into a novel grounded context. It is not an external language oracle because schema acquisition, state ownership, role matching, transfer, and held-out validation are all inspectable and evidence-bound.

## Nonclaims
No general ontology, unrestricted analogy engine, general causal theorem, planner, policy optimizer, execution authority, truth authority, value-priority authority, external LLM/oracle authority, or canon promotion.
