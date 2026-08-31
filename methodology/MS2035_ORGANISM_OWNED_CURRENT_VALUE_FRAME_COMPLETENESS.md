# MS2035 — ORGANISM-OWNED CURRENT VALUE-FRAME COMPLETENESS

## Goal
Close the MS2034 coordinate-omission authority blocker without adding a value manager, scheduler, scalar utility, or caller-selected comparison frame.

## Existing owner
`ValueVariableRegistry` already owns:
- every registered constitutional `ValueVariableContract`;
- exact current epoch per value;
- current qualification/currentness through `is_current`;
- latest value observation for the current epoch;
- content-bound contract signature.

No additional persistent frame registry is required for a read-only current frame.

## Research-only frame derivation
Derive the complete current frame by scanning the registry itself, never caller-supplied value ids.

For every registered value whose contract is current/qualified, require a latest observation at the same epoch and emit exactly:

`(value_id, value_epoch, current_value, contract_signature_sha256)`.

Rows are sorted by `value_id`; coordinate order therefore has no authority.

If any current constitutional value lacks a current observation, the entire frame is:
`DEFER_UNKNOWN / CURRENT_VALUE_FRAME_OBSERVATION_MISSING:<value_id>`.

A stale/unqualified value may be absent only because `ValueVariableRegistry.is_current(value_id)` is false. Such exclusions are reported explicitly rather than caller-selected.

## Frame digest
Content-bind the sorted frame rows into a deterministic SHA-256 digest. The digest is a current read-only witness, not a durable authority token.

A vector is frame-compatible only when its exact current coordinate descriptors equal the organism-owned current frame rows. A caller-selected V-only vector cannot match a current V/W frame.

## Hostiles
1. V/W both current + observed -> COMPLETE frame with V/W independent of insertion order.
2. Caller-built/subset V-only vector -> frame mismatch, no selection authority.
3. Register current X but do not observe X -> whole frame UNKNOWN/incomplete; X not silently omitted.
4. Stale X after `change()` -> X excluded only through explicit registry currentness; exclusion reported.
5. Add current observed X after old frame -> new frame includes X and old frame no longer current-complete.
6. Same-epoch W observation changes -> frame digest/descriptor changes; old frame no longer current-complete.
7. Derivation read-only -> no store/events/persistence/selection/EFFECT changes.
8. Duplicate value identity remains rejected by existing registry registration law.

## Expected result
If hostiles pass, earn:

`COMPLETE_CURRENT_VALUE_FRAME_IS_DERIVABLE_FROM_VALUE_REGISTRY_WITHOUT_CALLER_SUBSET_AUTHORITY`.

and:

`CURRENT_VALUE_WITHOUT_CURRENT_OBSERVATION_BLOCKS_FRAME_COMPLETENESS`.

This closes the MS2034 frame-completeness representation/authority seam research-only.

## Still not earned
- runtime Pareto selection;
- cross-deficit persistence/nomination;
- effect-time cross-value reauthorization;
- scalar value ranking;
- semantic value importance;
- autonomous first-probe authority;
- PRELINGUAL_SUBSTRATE_V1 promotion;
- language/reference admission.


## Observed result — CURRENT VALUE FRAME COMPLETENESS EARNED
Direct witness PASS. The registry-derived frame over current V/W was complete, order-independent, and read-only. A caller V-only vector failed exact complete-frame matching.

Hostiles:
- current X registered without current observation -> entire frame DEFER_UNKNOWN `CURRENT_VALUE_FRAME_OBSERVATION_MISSING:X`;
- X observed then explicitly staled through registry `change()` -> X excluded only through `is_current=False`, with exclusion reported;
- new current observed X -> old V/W frame stale because full frame becomes V/W/X;
- same-epoch W observation change -> frame digest/descriptor changes and old frame becomes stale;
- duplicate V registration rejected by existing registry law;
- derivation produced no handler calls, selection, persistence, or EFFECT authority.

Cleanup-neutral focused MS2032–MS2035 lineage: **25/25 PASS in 75.28s**, stderr empty.

Earned:
`COMPLETE_CURRENT_VALUE_FRAME_IS_DERIVABLE_FROM_VALUE_REGISTRY_WITHOUT_CALLER_SUBSET_AUTHORITY`.

Also:
`CURRENT_VALUE_WITHOUT_CURRENT_OBSERVATION_BLOCKS_FRAME_COMPLETENESS`.

MS2034's omission blocker is therefore closed at the frame-representation/currentness layer research-only. Runtime Pareto selection is still not authorized until vector construction and comparison are bound to this organism-owned frame and pressured under currentness/effect-time conditions.
