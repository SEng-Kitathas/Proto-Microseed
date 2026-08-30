# MS2003 — Owned Operational Referent Context Enters Decision-Bearing Policy Without a Referent Manager

## Question
Can raw observation history produce operational referent pressure *inside* the Microseed and let that pressure change a bounded zero-row action intent through already-qualified routing, without caller-supplied boundaries, referent classes, projection buckets, preferred actions, semantic reference, object identity, or a new referent/policy manager?

## Upstream blocker inherited from MS2002
MS2002 persisted exact operational referent signature classes but the older crossing/occlusion harness still computed channel-change boundaries outside production.

The actual missing ownership seam was:

`RAW_OBSERVATION_TRACE != OWNED_REFERENT_BOUNDARY_SIGNATURES`

Routing integration was not lawfully testable until this upstream seam closed.

## Mechanisms added
### 1. `derive_channel_change_boundaries(...)`
Production now derives per-channel change indices directly from one rectangular, time-ordered raw observation history.

The operation is deterministic structural differencing only. It carries no:
- referent identity authority;
- semantic reference authority;
- causal authority;
- truth authority;
- action/execution authority.

Malformed/ragged/too-short histories fail closed.

### 2. `Microseed.derive_operational_referent_signatures_from_raw_trace(...)`
Caller supplies only:
- raw time-ordered observation rows;
- one opaque action handle per transition.

Microseed derives internally:
1. channel-change boundaries;
2. boundary-coherent groups through the existing nomination mechanism;
3. affordance-relative operational signatures through the existing signature mechanism.

Caller supplies no boundary signatures, groups, class IDs, latent object IDs, or semantic referent labels.

Symmetry remains `UNKNOWN_INCOMPLETE`.

### 3. Current operational signature-class-set context
`derive_current_operational_referent_class_set_context(...)` requires every currently derived operational signature to reassociate to persisted evidence through MS2002's existing EvidenceLedger path.

The discriminator is the canonical **set of operational signature classes**, not an individual historical witness and not a selected object.

`SIGNATURE_CLASS_SET_CONTEXT != OBJECT_IDENTITY`

Duplicate historical witnesses remain a class/set. No witness-selection authority is introduced.

### 4. Fixed opaque class-set projection coordinate
`operational_referent_class_set_projection_signature_sha256()` defines the exact content identity of the derivation rule used by this bridge.

The projection handle remains `SUPPLIED_AND_PROVENANCED`; MS2003 does not claim endogenous projection qualification. The exact signature check prevents an arbitrary supplied projection from laundering unrelated bucket semantics into the referent bridge.

### 5. Existing qualified routing remains sole routing owner
`resolve_current_operational_referent_class_set_conditioned_relation(...)`:
- requires one current existing projection-conditioned routing binding;
- requires the exact fixed supplied/provenanced class-set coordinate;
- derives the current class-set bucket internally from raw history;
- requires persisted class reassociation;
- delegates relation resolution to the existing qualified routing binding;
- carries no bucket-selection, identity, semantic-reference, truth, or execution authority.

### 6. Existing rehearsal remains sole policy owner
`nominate_current_operational_referent_class_set_conditioned_rehearsal(...)`:
- accepts raw referent observations/actions, current feasible options, and existing routing IDs;
- caller supplies neither class, bucket, routed relation, nor preferred action;
- resolves every eligible option through one internally derived class-set bucket;
- requires all options to agree on that current bucket;
- delegates to the existing counterfactual rehearsal owner;
- creates no new planner, policy registry, referent manager, or selector state.

## Hostile experiment A — owned raw boundary/signature derivation
Crossing/occlusion world is replayed with the old harness-side boundary computation removed from Microseed input.

Pressure:
- channel crossing/permutation;
- occlusion;
- reappearance;
- persistent vs perfect-copy replacement;
- alias symmetry;
- malformed/ragged histories.

Earned direct result:
- raw history -> owned boundary derivation -> operational classes: PASS;
- persistent and perfect-copy replacement remain operationally indistinguishable at this level;
- alias symmetry remains `UNKNOWN_INCOMPLETE`;
- caller-supplied boundaries/groups/classes: NO;
- numerical identity authority: NONE;
- semantic reference authority: NONE.

## Hostile experiment B — class-set-conditioned relation routing
Two different raw operational contexts produce different canonical persisted class-set buckets.

The same action/task is routed to two different pre-existing qualified predictive relations through one externally qualified projection-conditioned routing binding.

Pressure:
- no persisted witness for a current class -> DEFER;
- alias/symmetry -> DEFER;
- scan budget exhaustion -> DEFER;
- arbitrary supplied projection coordinate -> DEFER;
- caller projection bucket -> absent;
- caller class/object selection -> absent.

## Hostile experiment C — decision-bearing action intent
Two current EFFECT actions X/Y share one current frame, episode schema, and constitutional value coordinate.

Pre-existing qualified relation fixtures encode:
- Context A: X moves the value into viability; Y moves away.
- Context B: Y moves the value into viability; X moves away.

The routing qualifier sees independent holdout evidence for both class-set buckets and both actions.

With **zero supplied rehearsal rows**:
- Context A raw history -> internally derived class-set context -> rehearsal `X` -> bounded intent `X`.
- Context B raw history -> internally derived class-set context -> rehearsal `Y` -> bounded intent `Y`.
- unknown class ancestry -> no rehearsal;
- alias symmetry -> no rehearsal.

The intent still carries execution authority `NONE`; actual execution remains separately obligation- and capability-authorized.

## Laws / scars
- `RAW_OBSERVATION_TRACE != OWNED_REFERENT_BOUNDARY_SIGNATURES` — closed for bounded deterministic change-boundary derivation.
- `BOUNDARY_CHANGE_DERIVATION != REFERENT_IDENTITY`.
- `OPERATIONAL_SIGNATURE_CLASS_CONTEXT != SEMANTIC_REFERENT`.
- `SIGNATURE_CLASS_SET_CONTEXT != OBJECT_IDENTITY`.
- `QUALIFIED_CONTEXT_ROUTING != REFERENT_IDENTITY_AUTHORITY`.
- `PERSISTED_CLASS_REASSOCIATION != NUMERICAL_IDENTITY`.
- `CLASS_SET_BUCKET != CALLER_SUPPLIED_POLICY`.
- `ACTION_INTENT_NOMINATED != EXECUTION_AUTHORITY`.

## Earned candidate claim
If focused, self-test, compile/diff, whole-suite, hash readback, seal, push, and independent remote readback all succeed on frozen bytes:

`OWNED_RAW_OPERATIONAL_REFERENT_SIGNATURE_CLASS_SET_CONTEXT_CAN_CHANGE_ZERO_ROW_REHEARSAL_AND_BOUNDED_ACTION_INTENT_THROUGH_EXISTING_EXTERNALLY_QUALIFIED_ROUTING_WITHOUT_CALLER_BOUNDARIES_GROUPS_CLASSES_BUCKET_PREFERRED_ACTION_OBJECT_IDENTITY_SEMANTIC_REFERENCE_OR_A_NEW_REFERENT_POLICY_MANAGER`

## Authority ceiling
MS2003 grants no:
- numerical object identity;
- semantic reference;
- persistent semantic referent registry;
- truth authority;
- causal theorem authority;
- self-qualification;
- routing qualification authority;
- semantic policy/intention authority;
- execution authority.

## Remaining assistance / open seam
MS2003 still uses:
- a supplied/provenanced opaque class-set projection coordinate;
- externally qualified predictive relations;
- externally qualified projection-conditioned routing;
- externally supplied constitutional frame/episode/value/action authority.

Therefore:

`OWNED_REFERENT_CONTEXT_PARTICIPATION != ENDOGENOUS_SEMANTIC_REFERENCE`

and

`DECISION_BEARING_REFERENT_PRESSURE != GENERAL_RICH_WORLD_AUTONOMY`.

The next pressure surface should be a unified sustained external world where referent-class pressure, drift/relearning, restart/currentness, resource/ambiguity pressure, and action outcomes co-occur without campaign-side latent interpretation or a new cross-cutting manager.
