# MS2009 — OWNED CURRENT REFERENT PROBE PREFIX RECONSTRUCTION

## Question
Can Microseed reconstruct the current incomplete opaque probe prefix from its own authenticated action/outcome/raw-observation ancestry, without a caller supplying raw samples or action sequence?

## Composition
Reuse only ordinary bounded action execution, authenticated observation-basis outcome closure, `BOUNDED_RAW_OBSERVATION_COORDINATES`, current control-state evidence, and the exact predecessor outcome/intent chain.

## Rule
Start at the current control-state witness. Require exactly one current raw receipt for that witness. Walk backward through the unique outcome whose evidence *is* the current control-state evidence, recover the exact execution/intent/action, and require exactly one current raw receipt for the predecessor control-state witness. Continue only to the supplied finite depth ceiling. All receipts must share one current frame; multi-step history requires one current episode carrying that frame. Reverse the recovered chain to produce chronological raw samples and opaque actions.

The depth ceiling is a resource bound only. It supplies neither trace content, action identity, referent class, nor semantic boundary.

## Hostiles
- lawful P0→P1 history reconstructs `[raw0,raw1,raw2]` + `[P0,P1]`;
- close/reopen + exact compatible capability/frame/episode reattachment reconstructs the same prefix;
- duplicate current raw receipt => DEFER_UNKNOWN, no pick-first;
- frame drift => DEFER_UNKNOWN;
- insufficient predecessor chain => bounded incomplete, not fabricated history.

## Authority
No semantic coordinate, referent identity, truth, selection, projection or execution authority is added.
