# MS2060 — Hierarchy Transfer: Request Channel != Subordinate Local Means

## Why this discriminator exists
MS2057 proved request-effect learning, MS2058 removed the externally supplied request shortlist for learned candidates, and MS2059 showed that higher context + subordinate current-state factors can be discovered from opaque raw observations.

A remaining donor law was still collapsed in the fixtures: U1/U2 had been treated as directly executable capabilities. The standalone solution instead requires the higher level to request a subordinate desired state while the subordinate independently decides how or whether to realize it.

## Bounded translation
Represent an opaque requested subordinate state as a **request-channel action handle** (`REQ-T0`, `REQ-T1`). The parent has EFFECT authority only over emitting the request-channel action. It does not own the subordinate's local means.

Harness-side ChildController owns local means `M0/M1`, which are absent from the parent's CapabilityRegistry. The same requested target is realized through different local means as child state C0/C1 changes.

This is not yet endogenous desired-state construction: T0/T1 request handles remain supplied finite operational affordances.

## Hostiles
- same request T0 must be realized through both M0 and M1 depending on child state;
- parent registry must not contain M0/M1;
- parent learns request->higher-effect relation while local means vary;
- child REFUSED/UNKNOWN blocks request before execution;
- request capability boundary explicitly denies local-actuation authority;
- recruitment proposal retains semantic-goal authority NONE;
- changing subordinate local means without changing higher request effect does not spuriously alter request identity/currentness;
- no claim of endogenous desired-state construction.

## Boundary
Success earns only:
`REQUEST_ACTION_HANDLE_CAN_PRESERVE_SUBORDINATE_LOCAL_MEANS_AUTONOMY_IN_BOUNDED_TRANSFER_FIXTURE`.

It does not earn arbitrary desired-state generation, recursive hierarchy, semantic child identity, or CFE transfer.

## Result
Focused: **6/6 PASS in 4.23s**.
Broader historical/currentness/authority/MS2057-MS2060 guard: **81/81 PASS in 57.76s**.
Production delta: **none**.

Earned for the bounded fixture:
`REQUEST_ACTION_HANDLE_CAN_PRESERVE_SUBORDINATE_LOCAL_MEANS_AUTONOMY_IN_BOUNDED_TRANSFER_FIXTURE`.

The same request target was realized by different child-local means as child state changed; those means never entered the parent CapabilityRegistry. Child REFUSED/UNKNOWN remained authoritative.

Next irreducible seam:
`FINITE_REQUEST_HANDLE_SET != ENDOGENOUS_SUBORDINATE_DESIRED_STATE_CONSTRUCTION`.
