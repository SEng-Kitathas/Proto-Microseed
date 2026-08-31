# MS2033 — CROSS-VALUE EPISTEMIC CONSEQUENCE VECTOR CONSTRUCTION

## Goal
Attack the MS2032 blocker at the **vector-construction** layer, not the comparator layer.

Question:
Can existing owned/current mechanisms compose a complete multi-coordinate information-conditioned downstream regulatory consequence vector for one current epistemic opportunity, without cross-value rehearsal laundering or new decision authority?

## Composition hypothesis
Existing owners already provide two distinct ingredients:
1. current epistemic consequence / decision-bearing rehearsal exposes, for each live relational alternative, the **downstream first action** that would be selected after resolving the uncertainty;
2. current singleton trace discovery exposes that downstream action's separately bound effect on each current value coordinate.

Therefore a read-only adapter may derive, for every opportunity `o`, branch `h`, and requested value coordinate `v`:

`R(o,h,v) = residual_pressure_after_effect(value_contract(v), current_value(v), current_effect(first_action(o,h), v))`

Then summarize per coordinate:

`R_worst(o,v) = max_h R(o,h,v)`.

This does not reuse a V-bound rehearsal relation as if it were W-bound. The only cross-coordinate projection is through separately qualified/current action->value effect evidence already owned by the multi-value bridge.

## Binding requirements
The adapter must require:
- a current same-value epistemic consequence surface with branch first-actions and proposal digests;
- at least two branch first-actions;
- every requested value contract/current observation to be current;
- one `CURRENT_EFFECT` witness for every `(branch first_action, value_id)` pair;
- effect witness `value_epoch` equals the current value epoch;
- effect witness `capability_epoch` equals the current capability epoch;
- no ambiguous ancestry status;
- no missing coordinate fill;
- no caller-supplied residual/vector values.

## Hostiles
1. **Complete construction** — real P2 opportunity branches A/B and P4 branches D/C, with separately bound singleton trace effects on V and W, produce complete two-coordinate vectors read-only.
2. **Trade-off survives** — choose trace effects so P2 has lower worst residual on V but higher on W, while P4 is the reverse. Vector construction succeeds but grants no cross-value selection authority.
3. **Immediate probe effect is irrelevant** — also seed a large P2/W immediate effect; vector lineage must use A/B downstream actions, not P2.
4. **Missing downstream action/value effect** — no `B::W` witness -> vector `DEFER_UNKNOWN`; no zero-fill.
5. **Multiple current ancestry shapes** — conflicting current `A::W` effect ancestries -> vector `DEFER_UNKNOWN`; no averaging.
6. **Value epoch/currentness drift** — stale W -> vector `DEFER_UNKNOWN` even if an old effect witness exists.
7. **Read-only** — vector derivation itself changes no store/event state and grants no persistence, selection, execution, truth, semantic-goal, or value-priority authority.

## Expected interpretation
If complete vectors can be constructed and all hostiles fail closed, MS2032's blocker narrows:

`OWNED_MULTI_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR_IS_COMPOSABLE_FROM_BRANCH_ACTION_IDENTITY + CURRENT_ACTION_VALUE_EFFECT_EVIDENCE`.

This still does **not** authorize a Pareto comparator or cross-deficit selector. A later campaign must separately prove comparator semantics, incomparability, currentness, and selection authority.

## Nonclaims
No scalar utility, semantic value hierarchy, max-pressure executive, generic scheduler, curiosity score, cross-value rehearsal relation, caller-supplied vector, persistence, nomination, or EFFECT authority is introduced.


## Observed result — COMPOSITIONAL VECTOR CONSTRUCTION EARNED
Direct witness PASS. Using actual P2 branch actions A/B and P4 branch actions D/C from the owned epistemic consequence surface plus separately current singleton action/value trace effects:
- P2 vector = `{V: 0.0, W: 0.5}`;
- P4 vector = `{V: 0.5, W: 0.0}`;
- both vectors complete/current/read-only;
- trade-off remains no-selection.

A deliberately large immediate `P2::W` effect was present but did not enter the vector: downstream A/B effects were used instead. Missing `B::W` -> DEFER_UNKNOWN; conflicting current `A::W` ancestry -> DEFER_UNKNOWN without averaging; W value drift -> DEFER_UNKNOWN even with old effect witness.

Raw focused lineage: 8 passed + 10 Windows SQLite teardown-only failures; no mechanism assertion failure; stderr empty. Cleanup-neutral exact same lineage: **18/18 PASS in 34.96s**.

Earned composition:
`OWNED_MULTI_VALUE_EPISTEMIC_CONSEQUENCE_VECTOR_IS_COMPOSABLE_FROM_BRANCH_ACTION_IDENTITY + CURRENT_ACTION_VALUE_EFFECT_EVIDENCE`.

Still not earned: Pareto comparator, cross-value selection, persistence, nomination, or EFFECT authority.
