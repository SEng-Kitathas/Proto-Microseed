# Frontier E — Matched Current Surface / Different Developmental History — 2026-09-04

## Mechanism
Two Microseed instances are brought to the same **current observable surface**: the same opaque control state, the same current raw sample, and the same capability/frame/episode/value epochs. One instance reached that state through authenticated `P0 -> P1` action/outcome ancestry. The other begins at the same current state without those predecessors. Both are restarted under the same runtime contracts.

The discriminator asks only whether the existing read-only owned-history mechanism can reconstruct a different predecessor prefix. It does not add an identity label, identity manager, or caller-supplied history class.

## Example
Both instances currently see `s2` and raw sample `[1,1,1,1]` with the same current contracts. The historyful instance can reconstruct `P0 -> P1`; the fresh-current instance can reconstruct no predecessor action. That difference comes from authenticated raw receipts plus the action/outcome predecessor chain.

## Technical name
This is a **matched-current-state / different-developmental-history discriminator** over authenticated provenance. It separates operationally readable causal history from numerical identity.

## Competing interpretations
1. **Current-state sufficiency:** once current observables and runtime contracts match, no lawful read-only distinction remains.
2. **History-bearing provenance:** authenticated developmental history can lawfully remain readable even when current observables match, without requiring numerical identity.
3. **Hidden identity smuggling:** the setup accidentally encodes the answer through evidence IDs, a caller-provided history label, database size, or an identity manager.

The hostile design rejects interpretation 3 by excluding evidence IDs/database size from the current-surface match, supplying no history label, adding no identity primitive, and requiring all truth/selection/execution/semantic authority fields to remain `NONE`.

## Claim ceiling
A positive result shows only that **authenticated developmental provenance can be operationally readable across restart when current observable surfaces match**. It does not establish numerical identity, selfhood, semantic reference authority, truth authority, selection authority, or execution authority.

## Authority
Research-only. No `microseed/` production mutation. No public-main movement. No canon promotion.
