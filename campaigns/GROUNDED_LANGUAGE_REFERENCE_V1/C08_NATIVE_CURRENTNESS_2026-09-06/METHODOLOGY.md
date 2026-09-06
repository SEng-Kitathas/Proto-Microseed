# C08 Methodology — Native Evidence Association / Currentness Boundary

## Mechanism
C07 left the token/relation association as durable evidence but not as an organism-native currentness-bearing record. C08 adds a **generic opaque evidence association** surface to the research-branch Microseed. It contains an opaque left identifier, an opaque right content digest, exact source-evidence identities, and a currentness state. It contains no predicate meaning, semantic role, language authority, or execution path.

A record is historically durable. Currentness is separate. Fresh registration is current in the live runtime; replay after restart demotes a non-stale historical record to `REVALIDATION_REQUIRED`. A durable drift witness stales only the affected record and remains stale across restart. Later matching evidence does not silently reactivate it.

## Example
Two C07 token/relation bindings create two native opaque association records. A negative currentness witness for one record stales only that record; the other remains current. After restart, the stale record is still stale while the unrelated historical record requires fresh revalidation.

## Technical name
**Native opaque evidence association lifecycle with selective empirical staleness and restart non-reauthorization.**

## Why C08 stops partial
The lifecycle is native, but C08A's fresh currentness observation includes `observed_right_digest_sha256` authored by the external research harness. That means the experiment has not yet given Microseed an organism-owned way to derive the current C06/B1 relation digest from its own evidence surfaces.

`HARNESS_AUTHORED_RELATION_DIGEST != ORGANISM_OWNED_CURRENTNESS`

Calling the assisted confirmation full C08 success would smuggle evaluator-owned currentness into the organism. The correct next seam is C08B: embody the C06/B1 relation-currentness evidence owner first, then return to token-association revalidation.
