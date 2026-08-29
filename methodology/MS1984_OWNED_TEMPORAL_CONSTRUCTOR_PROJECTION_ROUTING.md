# MS1984 — Owned Temporal Constructor Projection Reuse Through Existing Relation Routing

Date: 2026-08-29 ET
Status: core-changing composition candidate
Parent: MS1983 `a363bdda9db4ff849fda1359107cc026eee1c962`

## Question
Can an externally qualified temporal constructor projection be reused online without caller-supplied raw history or projection bucket?

Prewrites:
- `ADMITTED_CONSTRUCTOR_PROJECTION != CALLER_HISTORY_AUTHORITY`;
- `CURRENT_RAW_HISTORY_DERIVATION != SEMANTIC_TEMPORAL_RELATION`;
- `OPAQUE_BUCKET_DERIVATION != SEMANTIC_CLASSIFICATION`;
- `PROJECTION_REUSE != EXECUTION_AUTHORITY`;
- `REPRESENTATION_REUSE != LANGUAGE`.

## Composition audit
MS1982 already provides durable bounded raw receipts and authenticated action ancestry.
The existing `ProjectionConstructorCandidate.project(raw_history)` already maps opaque temporal histories to opaque buckets.
MS1453–1477 already provides externally qualified projection-conditioned relation routing.
MS1983 removes caller bucket authority for current raw projections.

The missing online owner was therefore only:
`CURRENT_CONTROL_STATE -> AUTHENTICATED_RAW_PREDECESSOR_CHAIN -> EXACT_ADMITTED_CONSTRUCTOR -> OPAQUE_BUCKET`.

## Minimal embodiment
Refactored raw-receipt currentness into one private read-only helper shared by MS1983 and MS1984 so the two reuse paths cannot silently diverge in capability/frame/receipt validation.

Added:
`resolve_current_raw_constructor_projection_conditioned_relation(...)`.

It:
1. requires an existing current externally qualified projection-conditioned routing binding;
2. requires the exact current EpistemicProjectionRecord;
3. exact-matches one still-present nominated constructor candidate by digest;
4. checks candidate frame and EpisodeSchema ancestry is current;
5. starts from the exact current opaque control-state witness;
6. requires exactly one current bounded raw receipt for that control state;
7. walks backward only through unique actual ActionOutcomeRecord evidence that produced the current state;
8. re-derives each predecessor transition through the admitted opaque-transition bridge;
9. requires visible-state and exact frame continuity;
10. follows the predecessor action intent's exact `control_state_evidence_id` to the previous raw receipt;
11. repeats only to the candidate's bounded `lag_depth_used`;
12. invokes the existing constructor's opaque `project(raw_history)`;
13. delegates bucket->relation selection to the existing externally qualified routing owner;
14. persists nothing and grants no bucket-selection, semantic-coordinate, temporal-semantic-relation, semantic-projection, truth or execution authority.

## Process-backed world
Scratch:
`scratch/ms1984_owned_temporal_constructor_projection_routing.py`.

Reuses the MS1981 temporal raw world:
- first raw bit observed at ALIAS0;
- PREP -> ALIAS1;
- second raw bit observed at ALIAS1;
- B -> SAME vs DIFF according to equality of first and second bit.

48 actual histories train the MS1982 owned temporal constructor path. The exact admitted constructor uses atoms:
`L0:P0 + L1:P0`.

Two independently qualified predictive relations are then installed for B:
- SAME;
- DIFF.

The routing relations use a separate current EpisodeSchema (`EP-ROUTE`).  Hostile replay showed that changing the constructor's `EP` still invalidates the admitted projection/binding itself before relation-local currentness matters; this is a stricter early-stop surface than the test initially assumed.

## Online discriminator
A fresh current trial with bits `(0,1)` is prepared only through:
- current control-state evidence;
- first owned raw receipt;
- actual PREP execution/outcome;
- second owned raw receipt.

Before B executes:
- legacy generic routing is deliberately given the wrong qualified SAME bucket and returns `R-MS1984-SAME`;
- the new owned temporal resolver reconstructs raw history `(second, first)`, derives the DIFF bucket through the admitted constructor, and returns `R-MS1984-DIFF`.

Observed evidence order:
- current raw receipt `E-CUR-RAW1-0`;
- predecessor raw receipt `E-CUR-RAW0-0`.

Synchronous execution: rc=0 / PASS.

Earned:
`CURRENT_OWNED_TEMPORAL_RAW_HISTORY_CAN_BE_RECONSTRUCTED_THROUGH_AUTHENTICATED_ACTION_ANCESTRY_PROJECTED_BY_THE_EXACT_ADMITTED_CONSTRUCTOR_AND_REUSED_BY_EXISTING_QUALIFIED_RELATION_ROUTING`.

## Authority ceiling
- caller history authority: NONE;
- bucket selection authority: NONE;
- coordinate semantics: NONE;
- semantic temporal-relation authority: NONE;
- semantic projection/category authority: NONE;
- truth authority: NONE;
- execution authority: NONE;
- language authority: NONE.

## Next discriminator
After hostiles and whole-organism verification, the next high-information frontier is whether **one learned opaque representation can lawfully become raw input/evidence for another learned representation step** without semantic promotion.

Before adding any graph/concept layer, audit whether existing projection buckets can be captured as bounded derived evidence and fed into existing constructor/projection machinery under explicit qualification/currentness lineage.

Prewrite:
`OPAQUE_DERIVED_BUCKET != SEMANTIC_SYMBOL`.
