# IDENTITY-DEV-03 — Matched Current Surface / Different Developmental History

## Mechanism
Two Microseed instances end at the same defined current observable surface. One arrived through authenticated `P0 -> P1` history; the other begins fresh at the same current state. Both restart under the same runtime contracts. The existing read-only provenance mechanism then reconstructs what authentic predecessor history is actually present.

## Example
Both instances are at `s2`, both expose raw sample `[1,1,1,1]`, and their capability/frame/episode/value epochs match. The historyful instance reconstructs `P0 -> P1` with `step_count=2`; the fresh-current instance reconstructs no predecessor action with `step_count=0`.

## Technical name
**Matched-current-surface / different-developmental-history discriminator** over authenticated provenance.

## Application
This separates two ideas that should not be collapsed. A numerical identity primitive is still not required by the tested operational referent mechanism. But developmental provenance can be a real, durable, read-only state variable that current observables alone do not reconstruct.

## Verification
- New hostile surface: **3/3 PASS**.
- MS2007 + MS2009 + original Frontier E composition: **7/7 PASS**.
- SH4 long-horizon composition: **1/1 PASS**.
- Public continuity verifier: **PASS**, issues empty.
- B/C guard: **2/2 PASS**.
- `microseed/` production delta: **none**.

## Ceiling
`AUTHENTICATED_DEVELOPMENTAL_PROVENANCE_CAN_BE_OPERATIONALLY_READABLE_ACROSS_RESTART_WHEN_CURRENT_OBSERVABLE_SURFACES_MATCH__THIS_DOES_NOT_ESTABLISH_NUMERICAL_IDENTITY_OR_SELFHOOD`

This result does **not** establish numerical identity, selfhood, semantic reference, truth authority, selection authority, or execution authority. It also does not yet show that matched-current-state histories should produce different actions. The earned difference is read-only provenance reconstruction.
