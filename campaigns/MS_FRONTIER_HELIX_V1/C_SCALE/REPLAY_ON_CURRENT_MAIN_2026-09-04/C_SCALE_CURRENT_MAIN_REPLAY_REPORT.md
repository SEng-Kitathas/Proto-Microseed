# Frontier C_SCALE — Current-Main Replay — 2026-09-04

## Mechanism
Two already-qualified two-level controllers are nested for one bounded execution chain. The top controller emits an L2 request. The middle controller receives only the bounded request/context mapping, independently chooses its own L0 request, and retains its own refusal boundary. No hierarchy manager is added and leaf-local means do not flow upward.

## Example
The top controller asks the middle controller for one of two learned request classes. The middle controller then runs its own `current_proposal`, selects the corresponding leaf request, and may refuse at its own gate. The top receives only the bounded middle outcome, not the leaf target/local mechanism.

## Technical name
**Bounded three-level execution composition of independently qualified two-level request-effect controllers.**

## Application
This shows that one extra hierarchy level can be composed from the existing bounded request/execution split without introducing a new recursive hierarchy primitive at this tested surface.

## Current replay
- Direct C_SCALE: **2/2 PASS**.
- Current MS2063 + MS2065 hierarchy surfaces: **6/6 PASS**.
- Public continuity verifier: **PASS**, issues empty.
- Production `microseed/` delta: **none**.

Historical source context was 2/2 focused + 44/44 related regression. The current replay does **not** claim to have rerun that historical 44-test command; it uses the current hierarchy guards instead.

## Claim ceiling
`ONE_BOUNDED_THREE_LEVEL_EXECUTION_COMPOSITION != GENERAL_RECURSIVE_HIERARCHY != THREE_LEVEL_END_TO_END_LEARNING. Both controllers are already trained/qualified two-level controllers, and the harness supplies an opaque mapping from the L2 request token to an L1 current context. The middle controller independently chooses the L0 request. Cross-level learning/currentness propagation after internal middle drift is not established here.`

## Remaining seam
`THREE_LEVEL_END_TO_END_LEARNING_AND_CROSS_LEVEL_CURRENTNESS_PROPAGATION_AFTER_INTERNAL_MIDDLE_DRIFT`

## Authority
Research only. No main movement, canon promotion, production mutation, or general recursive-hierarchy authority.
