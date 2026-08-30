# MS2000 — Same-Identity Capability Requalification Without a Lifecycle Manager

## Question
Can one stale capability return to current operational use under the **same capability identity and immutable content** after fresh external evidence, without duplicate registration, silent metadata reset, authority gain, auto-recovering dependents, or adding a global lifecycle manager?

## Controlling scars
- `STALED_CAPABILITY != REQUALIFIED_CAPABILITY`.
- `LOCAL_INVALIDATION != LAWFUL_REENTRY`.
- `REQUALIFICATION != SILENT_METADATA_RESET`.
- `SAME_IDENTITY_REENTRY != DUPLICATE_REGISTRATION`.
- `REQUALIFICATION_EVIDENCE != NEW_AUTHORITY_GRANT`.
- `ROOT_REQUALIFICATION != DEPENDENT_AUTO_REQUALIFICATION`.
- `DEPENDENCY_CYCLE != AUTHORITY_TO_SELF_SUPPORT`.
- `TRANSITIVE_UNUSABILITY != LOCAL_OWNER_STALENESS_ATTRIBUTION`.

## Existing mechanisms reused
1. `CapabilityContract.computed_signature_sha256()` already binds immutable operational content while excluding mutable qualification/currentness and runtime handler state.
2. `CapabilityRegistry` already owns capability identity, dependency graph, epochs, invalidation, and transitive executable currentness.
3. `DevelopmentRegistry` already owns developmental qualification/currentness history.
4. `ExternalCapabilityQualifier` + `FixedQualifier` already supply an external evidence boundary.
5. Epistemic projection recurrence already establishes the architectural precedent: stale same identity + fresh external requalification + current dependency ancestry -> new current epoch, without semantic recurrence identity authority.
6. Historical reentry already establishes that durable history may justify consideration but never restores authority by itself.

## Narrow mechanism added
### `CapabilityRequalificationTicket`
A fresh external ticket bound to:
- exact `capability_id`;
- immutable contract signature SHA-256;
- exact stale epoch;
- externally supportive requalification evidence;
- external qualifier identity.

The ticket intentionally has **no authority field**.

### `CapabilityRegistry.reactivate(...)`
A currentness transition only:
- requires an existing locally stale capability;
- requires an admissible qualified state;
- requires every declared dependency to have current transitive closure;
- increments the capability epoch;
- changes only qualification/currentness;
- does not alter immutable content;
- does not alter authority;
- does not reactivate dependents.

### `DevelopmentRegistry.requalify(...)`
Records the externally validated requalification evidence and new qualification state while preserving the existing authority and stale-history notes.

### `Microseed.requalify_capability(...)`
Consumes and validates the external ticket, calls the registry currentness transition, synchronizes the developmental record, records a `CAPABILITY_REQUALIFIED` event, and explicitly reports:
- authority gain `NONE`;
- dependent auto-reactivation `NONE`.

## Why EFFECT authority is not newly granted
The existing immutable capability signature already includes the capability's authority. Invalidation removes operational currentness but does not rewrite that historical authority field.

MS2000 does **not** activate the dormant `FixedQualifier.allow_effect` path and does not add any new initial EFFECT-admission mechanism. Fresh requalification evidence is checked through the existing fixed qualifier as read-only supportive evidence. The requalification ticket contains no authority grant.

Therefore:
`FRESH_REQUALIFICATION_EVIDENCE + SAME_SIGNATURE != NEW_EFFECT_AUTHORITY_GRANT`.

It only licenses reconsideration of the already-qualified identical contract's currentness.

## Hostile boundary
The campaign constructs an EFFECT chain:
`RQ-ROOT -> RQ-MID -> RQ-LEAF`.

After root drift, all three are stale. The campaign requires:
1. a dependent cannot requalify before its stale root;
2. forged immutable signature is rejected;
3. stale-epoch replay is rejected;
4. negative evidence is rejected;
5. root requalification increments only root epoch/currentness;
6. root recovery does not auto-recover MID or LEAF;
7. the same ticket cannot be reused after root becomes current;
8. MID must independently requalify after ROOT is current;
9. LEAF must independently requalify after MID is current;
10. final LEAF invocation succeeds with exactly the original EFFECT authority;
11. all immutable signatures remain byte-identical;
12. two stale cyclic capabilities cannot bootstrap each other by pairwise requalification.

## Authority ceiling
MS2000 grants no:
- self-qualification authority;
- authority escalation;
- truth authority;
- semantic capability identity authority beyond the existing opaque capability ID/content signature;
- automatic dependent recovery;
- global lifecycle-manager authority;
- cycle-resolution authority.

## Expected earned claim
If the direct boundary, focused lineage, self-test, compile/diff checks, and whole embodiment suite all pass on a frozen tree:

`SAME_IDENTITY_STALE_CAPABILITY_CAN_REENTER_AS_A_NEW_CURRENT_EPOCH_FROM_FRESH_EXTERNAL_EVIDENCE_AND_CURRENT_DEPENDENCY_CLOSURE_WITHOUT_DUPLICATE_REGISTRATION_AUTHORITY_GAIN_DEPENDENT_AUTO_RECOVERY_OR_A_NEW_LIFECYCLE_MANAGER`.

## Remaining boundary
This campaign does not establish:
- endogenous qualification;
- autonomous reacquisition of qualification evidence;
- automatic recovery scheduling;
- restart reconstruction of executable runtime handlers;
- lawful cyclic closure;
- sustained rich-world lifetime composition.

Those remain separate pressure surfaces.

## Successor compatibility scar — historical negative versus future prohibition
The overnight frozen soak completed **10,000/10,000** direct lifecycle repetitions and **50,000/50,000** randomized dependency/currentness graph cases before the first focused regression stopped on an MS1999 assertion that the live `Microseed` object must not have a `requalify_capability` method.

That assertion was valid as evidence at the MS1999 seal, because MS1999 had earned the negative:
`SAME_IDENTITY_CAPABILITY_REQUALIFICATION_PATH_MISSING`.

It was not a constitutional rule that every successor tree must preserve the absence forever. MS2000 exists specifically to pressure and potentially close that seam. Therefore the MS1999 witness is successor-scoped as:
- `MISSING_AT_MS1999_SEAL`;
- `NOT_AVAILABLE_AT_MS1999_SEAL__SAME_IDENTITY_CAPABILITY_REQUALIFICATION_PATH_MISSING`.

The historical negative remains true and is not erased. The successor tree may expose a later requalification API if it independently earns that mechanism.

New law:
`HISTORICAL_NEGATIVE != PERMANENT_FUTURE_PROHIBITION`.

The overnight focused failure is retained as a rejected seal witness, not hidden.
