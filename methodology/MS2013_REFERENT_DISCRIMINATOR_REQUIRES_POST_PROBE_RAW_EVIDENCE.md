# MS2013 — REFERENT DISCRIMINATOR REQUIRES POST-PROBE RAW EVIDENCE

## Question
Is an authenticated P2 action outcome sufficient evidence for a referent discriminator whose actual content is defined over opaque raw-response boundaries, or must the post-P2 raw response itself be durably owned and current?

## Hostile
Execute P2 lawfully and close it through the authenticated observation-basis path, producing an admitted transition sample. Advance the one-step epistemic trial, but deliberately do **not** call `record_bounded_raw_observation_coordinates` in the resulting control state. Then call completed-program evidence.

Expected law:
`AUTHENTICATED ACTION OUTCOME != OBSERVED EXACT REFERENT DISCRIMINATOR`.

A referent-derived completed trial may request revisit only when the current owned probe prefix closes through the exact execution and contains the post-step raw receipt. Duplicate/missing/stale raw receipts must fail closed.

## Observed pre-repair violation
The hostile passed the authenticated action/outcome ingress but deliberately omitted the post-P2 raw receipt. `derive_current_owned_opaque_probe_prefix()` returned DEFER_UNKNOWN with zero current raw matches, yet completed-program evidence was accepted and the deficit moved to REVISIT_REQUIRED. This directly demonstrated that authenticated state outcome had been laundered into evidence for a raw-content discriminator.

## Repair
Added a referent-only post-step raw observation requirement that reuses `derive_current_owned_opaque_probe_prefix()`. For referent-derived deficits, both step-bearing and completed-program evidence now require the completed program execution to be the **last owned action** in the current prefix and require exactly one current raw receipt after it. Missing/duplicate/stale post-probe raw evidence fails closed. No new raw store or discriminator registry was added.
