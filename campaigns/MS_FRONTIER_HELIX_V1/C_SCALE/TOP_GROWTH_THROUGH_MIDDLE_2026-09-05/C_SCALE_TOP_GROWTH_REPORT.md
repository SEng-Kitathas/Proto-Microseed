# C_SCALE — Top Policy Growth Through a Learned Middle — 2026-09-05

## Mechanism
The original C_SCALE experiment trained two complete two-level controllers separately and only then nested them. This pass removes the flat-pretrained top controller.

The middle controller is still already developed. The top starts with only its bounded runtime/request interface, an externally qualified opaque request-token projection, and two derived bound request specializations. It has **no learned request/effect relation and no context-conditioned routing binding**.

The top then lives through actual nested executions. Each top request is fulfilled by the learned middle, and only the opaque middle receipt plus the top-boundary world effect is visible upward. Those nested outcomes become the top's own action/outcome evidence. From that lived history the top learns its first predictive request/effect relations, detects their later drift, qualifies replacements, discovers a context projection from its own bounded raw observations, qualifies a context-conditioned routing binding, and then chooses/executes the correct top request through the same middle.

No flat top training world is used.

## Example
At first the top has two opaque request buttons but no learned rule saying which one is useful in a given `(higher, child)` context. It repeatedly presses both buttons while the already-developed middle handles each request using its own leaf choices. The top only observes whether the resulting nested episode was good or bad at the top boundary.

After enough lived examples, the top can learn that one request is useful in one context class and the other request in the other class. When the useful relation reverses in a later developmental phase, the top detects the drift from its own nested outcomes, replaces the stale relations, and learns the context routing needed to choose the current request.

## Technical name
**Staged hierarchical policy growth from nested outcome experience.**

This is stronger than post-hoc composition but weaker than full simultaneous three-level end-to-end learning.

## Application
The result removes one major assistance layer from C_SCALE: the top controller does not need to be prequalified in a separate flat environment before hierarchy composition. Existing Microseed action/outcome learning, currentness replacement, projection discovery, and routing qualification can operate on outcomes generated through a learned subordinate.

The next assistance seam is now precise: the harness still maps each top request token to one opaque current middle context. `C-SCALE-LEARN-03B` should test whether that binding can itself be discovered/owned below the top boundary rather than supplied by the evaluator.

## Verification
- Focused growth surface: **3/3 PASS**.
- Growth + C_SCALE + SH1 + MS2063 adjacent stack: **12/12 PASS**.
- Public continuity verifier: **PASS**, issues empty.
- Production `microseed/` delta: **none**.

## Preserved scars
1. Repeated identical middle `current_proposal()` calls produced duplicate deterministic rehearsal IDs. The registry rejection was correct. The lawful repair selects the current middle capability once and gathers repeated actual evidence through unique execution episodes, matching the existing SH1 scar.
2. Flat and nested top training produced the same semantic 64-sample projection-evidence multiset but different opaque sample IDs/order. The original research split therefore changed outcome solely because of incidental ID ordering. The repaired split orders on raw/action/scope/frame metadata only, explicitly excludes the outcome label, then uses the same seeded shuffle and unchanged discovery thresholds.
3. One ceiling assertion referenced the obsolete one-shot log key after the repeated-execution repair. That bookkeeping assertion was corrected without changing the mechanism.

## Claim ceiling
The middle is already independently learned/current. External qualification still exists. The top-request-to-middle-current-context mapping is still harness supplied. This is **not** full unassisted simultaneous three-level learning, not self-qualification, and not evidence for a hierarchy manager or atomic learned macro.
