# P05 Attribution Report — Grounded Multi-Step Causal Chaining and Counterfactual Composition

## What was learned separately
Veya learned two current evidence-bound action→outcome relations from **separate** experience sets:
- `A: S0 -> S1`, value effect `+1.0`
- `B: S1 -> S2`, value effect `+1.0`

No executed `A -> B` chain appeared in the relation-training phase. Each relation was independently nominated and qualified with holdout evidence under the existing action-outcome learner.

## Language-mediated composition
P04 had already coupled each current empirical relation to an owned P03 grounded concept. P05 derives a durable two-step chain only when the empirical state join is exact: relation-1 next state equals relation-2 start state. Language indexes the owned concept sequence; it does not manufacture the state join.

## Held-out actual chain
After deriving the chain from separately learned edges, Veya executes a fresh actual `A -> B` sequence. The observed capability sequence, state path `S0 -> S1 -> S2`, and cumulative value effect `+2.0` match the composed prediction.

## Counterfactual composition
The learned concept order corresponding to `A -> B` yields a bounded counterfactual chain prediction. Reversing the concept order maps to `B -> A`; because `B.next = S2` and `A.start = S0`, the empirical join fails and the counterfactual is marked `COUNTERFACTUAL_CHAIN_INFEASIBLE_RESEARCH_ONLY`. Language does not narratively repair the missing edge.

## Negative/currentness controls
- broken empirical state join: refused;
- wrong language concept sequence: refused;
- text-only multi-step causal story: refused;
- stale A or stale B relation: blocks current chain use while owned history remains;
- stale concept grounding: blocks language-mediated chain use;
- forged chain evidence: refused;
- actual heldout chain violation: reported as violation, not reinterpreted;
- language-disabled ablation: lexical retrieval disappears but owned chain content remains inspectable.

## Capability attribution
This is a legitimate compositional cognitive gain. Language participates by indexing and composing owned learned concepts with empirical relations. The multi-step result comes from grounded relations, exact state joins, owned coupling state, and heldout execution—not from prose or an external oracle.

## Nonclaims
No general planner, policy optimizer, causal theorem, execution authority, goal authority, value-priority authority, general semantics, external LLM/oracle authority, or canon promotion.
