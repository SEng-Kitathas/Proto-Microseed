# MS2006 — CAPABILITY-GATED REFERENT PROBE AVAILABILITY

## Question
Does a uniquely informative referent probe become lawfully available only when the same opaque action handle is backed by a current qualified EFFECT capability under the exact current scope/obligation, without executing it?

## Composition-first basis
MS2005 already derives unique or ambiguous informative opaque probe handles from owned referent evidence. Existing `CapabilityRegistry` already owns qualification, currentness, dependency closure, epochs, authority, scope, obligation binding, content signature and handler presence. MS2006 composes those surfaces only.

## Laws
- informative != available
- available != selected
- available != authorized/executed
- exact opaque probe handle must match capability id; similarly behaving aliases do not substitute
- capability must be EFFECT, current through dependency closure, qualified, handler-backed, and compatible with current obligation/scope
- epoch/signature are reported as ancestry, not authority
- no invocation occurs in the availability derivation

## Hostiles
1. no capability for unique P2 -> unavailable
2. P2 with wrong authority -> unavailable
3. P2 with wrong scope -> unavailable
4. current qualified EFFECT P2 -> inert availability with exact epoch/signature
5. `change_capability_dependency(P2)` -> availability disappears at the new stale epoch
6. unrelated P2-ALT does not satisfy exact P2 handle
7. ambiguous P2/P4 information surface remains ambiguous before capability gating

## Promotion boundary
PASS earns only current inert availability. It does not earn execution, selection among multiple informative probes, semantic identity, truth, or a referent-specific executor.
