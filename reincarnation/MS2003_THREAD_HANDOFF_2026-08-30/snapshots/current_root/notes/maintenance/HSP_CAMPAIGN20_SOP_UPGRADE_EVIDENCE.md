# HSP Campaign20 SOP Upgrade Evidence — 2026-08-27

## Authority / plane
Source is a user-supplied RAHL R&D attachment and is treated as controlled external/donor process evidence. It is not Microseed organism authority, not canonical project promotion authority, and not automatic Research OS package authority.

Attachment:
`RAHL_ENGINEERING_ACTIVE_RND_DROP_HSP_CAMPAIGN20_COMPLETE_R1_2026-08-27.zip`

Attachment-side ZIP SHA-256:
`070ccbdb235e01e7da716c57f05c70d0743d7f1f40d3c39b936d5d7476428414`

Outer ZIP size: 1,802,181 bytes.
Outer entries: 4.

Outer manifest declares 3 payloads and all 3 matched declared byte length + SHA-256 with zero missing/mismatched/extra payloads.

Campaign-complete nested ZIP:
`RAHL_ENGINEERING_HSP_20PASS_CAMPAIGN_COMPLETE_R1_2026-08-27.zip`
SHA-256: `46528be5cf6d65f3e7258ac743e12dfe960c61d0623e51cfd8a7e1b482e09789`

Campaign-complete manifest declares 4 payloads and all 4 matched declared byte length + SHA-256 with zero missing/mismatched/extra payloads.

Campaign result hashes:
- `CAMPAIGN_RESULT.json`: `b544225bca89d34bd384ef2f27d792eb9ab4acfc443bc824a143f34d7895069e`
- `CAMPAIGN_RESULT.md`: `3ec06ace2dfbe4c60918b2af31f9710cdade8a8c23021d10436efaebd5d37aa3`
- Slice04 ZIP: `ea03b6547e3be52d57b8da46dc636352da4ae08b4fcd950d2a24b35ec1ae49e2`

A recursive attachment-side traversal found nine standard `MANIFEST_SHA256.json` package surfaces with zero missing/hash/size/extra mismatches under the generic standard-manifest verifier. One older nested F020 package used a different manifest shape and was not promoted into this standard-manifest count.

## Final package disposition
Campaign status: `COMPLETE_20_PASSES_NARROWED`.
Authority: `RESEARCH_ONLY`.
Canonical promotion: `NONE`.
Final disposition: `RETAIN_HSP_AS_ADVISORY_DISCRIMINATION_FRONTIER`.
Auto-selection: `DEFERRED_NOT_QUALIFIED`.
Next campaign discriminator: `MODEL_ADEQUACY_AND_CORROBORATION_PROTOCOL_OR_OPERATOR_HIDDEN_LIVE_FRONTIER`.

## Key earned evidence

### Slice03 package-domain underperformance
In the independent actual-package outcome engine:
- HSP identification rate: 0.6666666667; mean cost 1.4; mean steps 1.0; truth retention 0.6666666667.
- fixed baseline identification rate: 0.8541666667; mean cost 1.4708333333; mean steps 1.6770833333; truth retention 0.8541666667.

Interpretation retained by the campaign: underperformance localized to errors in the declared rival-prediction model, not an inability of the HSP frontier to include safer alternatives.

### Pass16 — declared model mismatch localized
For `same_tree_rerun`, two rival rows had predicted operation partitions that did not match actual operation behavior:
- `SELF_REFERENCE_RERUN`
- `STALE_PAYLOAD_HASH`

Earned scar:
`DECLARED_PREDICTION_PARTITION != ACTUAL_OPERATION_PARTITION`.

### Pass17 — cross-domain exact-model blind holdout
When the rival-prediction model was accurate:
- HSP: identification 1.0; mean cost 0.665; mean steps 1.0; model breach 0.0; truth retention 1.0.
- fixed baseline: identification 0.85; mean cost 1.07275; mean steps 1.9875; model breach 0.0; truth retention 1.0.

This is positive evidence for HSP as a discrimination-frontier mechanism conditional on a sufficiently accurate declared rival model.

### Pass18 — hidden model drift
Under model drift:
- HSP: identification 0.75; mean cost 0.6866666667; mean steps 1.0; model breach 0.25; truth retention 0.75.
- baseline: identification 0.3333333333; mean cost 0.8866666667; mean steps 1.6666666667; model breach 0.6666666667; truth retention 0.3333333333.

Earned scar:
`FRONTIER_OPTIMAL_UNDER_MODEL != WORLD_OPTIMAL`.

### Pass19 — same-model corroboration
A second discriminator before singleton authorization produced:
- definitive rate: 0.8541666667
- correct definitive rate: 0.6666666667
- false definitive rate: 0.1875
- model breach rate: 0.1458333333
- mean cost: 2.1

Corroboration reduced false definitive collapse but did not eliminate it because both discriminators came from the same imperfect prediction model.

Earned scars:
- `SINGLE_DISCRIMINATOR_COLLAPSE != CONFIRMED_RIVAL_IDENTITY`
- `CORROBORATION_WITH_SHARED_MODEL != INDEPENDENT_VALIDATION`

### Pass20 — narrowed disposition
Earned role:
`HSP -> ELIGIBILITY / DOMINANCE FILTER / ADVISORY CANDIDATE FRONTIER`.

Not earned:
`HSP -> SELECTION AUTHORITY`.

Final campaign scars:
- `PARETO_FRONTIER != SELECTION_AUTHORITY`
- `DECLARED_PREDICTION_PARTITION != ACTUAL_OPERATION_PARTITION`
- `FRONTIER_OPTIMAL_UNDER_MODEL != WORLD_OPTIMAL`
- `SINGLE_DISCRIMINATOR_COLLAPSE != CONFIRMED_RIVAL_IDENTITY`
- `CORROBORATION_WITH_SHARED_MODEL != INDEPENDENT_VALIDATION`

Required stronger guard stated by the package:
`INDEPENDENT_OR_MODEL_DIVERSE_CORROBORATION_OR_UNKNOWN`.

## Execution discipline evidence
Slice04 explicitly required:
- no live-process attachment;
- one-shot child processes only;
- per-child timeout <=15 seconds; final orchestrator <=30 seconds;
- stdout/stderr + receipt before evidence;
- no mutation of prior sealed artifacts;
- cross-domain public plans sealed before hidden truth;
- candidate failure retained as evidence rather than rewritten into PASS.

This is consistent with the project’s existing bounded durable execution preference and does not create a new execution doctrine by itself.

## SOP upgrade interpretation
The evidence supports a process amendment that makes HSP advisory by default, model-conditional, and non-authorizing. HSP may construct an eligibility/dominance/discrimination frontier, but an actual next-experiment decision requires external selection policy plus model-adequacy/corroboration evidence. A singleton collapse under an unqualified prediction model remains UNKNOWN unless independently or model-diversely corroborated.
