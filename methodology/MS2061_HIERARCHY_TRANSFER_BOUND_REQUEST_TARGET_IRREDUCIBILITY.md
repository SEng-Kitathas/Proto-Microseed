# MS2061 — Bound Request Target Irreducibility Audit

## Purpose
After MS2057-MS2060 removed effect learning, shortlist relevance, factorized subordinate-state conditioning, and child-local-means autonomy as missing mechanisms, one donor term remained supplied: the finite request target handles T0/T1.

This audit asks whether current Microseed can lawfully use a newly learned opaque state as the target of a generic request channel **without** caller substitution after deliberation.

## Existing-path pressure
1. `CapabilityRegistry.invoke` accepts runtime kwargs.
2. `BoundedActionIntent` does not bind runtime invocation kwargs or a target digest.
3. action-outcome learning groups experience by `capability_id`, not by content-bound invocation parameters.
4. capability candidate admission is proposal/external-qualification plumbing but explicitly rejects EFFECT authority on newly admitted candidates.

## Hostile claims
- the same nominal action intent can be replayed in clean identical organisms with target T0 or T1 while retaining the same intent identity;
- alternating target parameters through one generic request capability collapse into one action-learning slot and prevent the two real target-conditioned laws from being represented;
- a learned target cannot escape this by becoming a new EFFECT capability through the existing candidate-admission bridge;
- no existing API content-binds a learned target to ordinary action intent.

## Interpretation
If these tests pass, the first irreducible host-transfer gap is not a hierarchy manager or desired-state ontology. It is a narrower operational carrier:

`LEARNED_OPAQUE_REQUEST_TARGET_REQUIRES_PRE_DELIBERATION_CONTENT_BINDING_TO_OPERATIONAL_INVOCATION`.

Any future embodiment must avoid caller execution-time target authority, preserve target representation ancestry/currentness, and keep the request-channel authority distinct from subordinate local means.

## First diagnostic-order scar
Initial focused audit returned **4 PASS / 1 FAIL** because the test expected the later `EFFECT_AUTHORITY_NOT_ADMISSIBLE_BY_THIS_BRIDGE` diagnostic. The external qualifier had already downgraded the EFFECT proposal to `RESEARCH_ONLY`, so admission correctly stopped earlier at `NOT_ADMISSIBLE:RESEARCH_ONLY`.

Classification: `EFFECT_VARIANT_ADMISSION_REJECTED_EARLIER_THAN_EXPECTED__DIAGNOSTIC_ORDER_MISMATCH_NOT_IRREDUCIBILITY_FAILURE`. Both lawful rejection paths preserve the same result: the existing admission bridge does not mint new executable request variants.

## Result
Focused irreducibility packet: **5/5 PASS in 1.35s**.
Broader historical/currentness/authority/MS2057-MS2061 guard: **86/86 PASS in 58.22s**.
Production delta: **none**.

Verified gap:
`LEARNED_OPAQUE_REQUEST_TARGET_REQUIRES_PRE_DELIBERATION_CONTENT_BINDING_TO_OPERATIONAL_INVOCATION`.

This is the first donor-transfer gap in the current campaign that survived existing-owner composition pressure. It is not evidence for a hierarchy manager or semantic desired-state subsystem.
