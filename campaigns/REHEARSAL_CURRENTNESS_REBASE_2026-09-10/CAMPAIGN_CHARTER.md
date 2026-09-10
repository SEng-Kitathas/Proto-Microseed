# Rehearsal Currentness Rebase on Hardened Substrate — 2026-09-10

## Mode
BUILD-COMMIT / lineage repair.

## Base authority
- branch: `research/rehearsal-currentness-rebase-on-substrate-v1`
- exact substrate receipt: `5206925e2b82bc9b0ca4073d0ddaa76378b28310`
- substrate science: `75ac873d5fe3330c31ff0321078930320fa59045`
- historical canonical P1A promotion: `c036ab55dca2bca057c0f84ca6d5c8bc3e313fa7`
- historical violation: `a5b6796e8d62d359442a7f7c9b7d9acab7f4ae32`
- historical research repair: `7b1278dc1ed6dbaa94dda110130cd36ed44edd99`

## Primary discriminator
`STALE_PREDICTIVE_RELATION_TO_DERIVED_REHEARSAL_PROPOSAL_CURRENTNESS_PROPAGATION`

Restore the already-canonical P1A law on the current substrate without reintroducing an O(n)-per-act learned-relation scan.

## Required law
A durable rehearsal proposal that owns an exact learned transition digest cannot remain a lawful execution premise when matching learned owners exist and all are stale. If at least one matching learned owner is current, the proposal remains current. Transition digests with no learned-registry owner (supplied-row assistance) remain governed by existing premise checks.

## Substrate constraint
`CANONICAL_SEMANTICS != CANONICAL_IMPLEMENTATION_COST`.
Use a derived digest->relation-id index rebuilt through the authoritative add/replay path. No full `relations.values()` scan in fresh proposal currentness.

## Anti-overreach
`STALE_RELATION != GLOBAL_PROPOSAL_INVALIDATION`.
`NO_LEARNED_OWNER != STALE_LEARNED_OWNER`.
`ONE_CURRENT_MATCHING_OWNER != ALL_MATCHING_OWNERS_STALE`.
`DERIVED_INDEX != CURRENTNESS_AUTHORITY`.
No planner, scheduler, semantics, truth, EFFECT, or canon authority gain.
