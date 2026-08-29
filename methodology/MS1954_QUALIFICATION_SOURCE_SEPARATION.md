# MS1954 — Runtime Environment / Qualification Source Separation

Date: 2026-08-29 ET
Status: pre-repair conflation recorded; shadow-substrate role split verified
Parent: MS1953 `65a1b82dbcc7bb374c6be22e7e3c2d007bd47501`

## Question
Can the experimental substrate separate the source that the organism acts in from the source that supplies holdout qualification evidence, rather than letting the environment adapter qualify its own learned model?

Prewrite:
- `EXTERNAL_TO_MICROSEED != INDEPENDENT_QUALIFICATION_SOURCE`;
- `SEPARATE_QUALIFICATION_ROLE != EVIDENCE_INDEPENDENCE_PROVED`;
- `ENVIRONMENT_COMPATIBILITY != QUALIFICATION_TRUTH`.

## Pre-repair evidence
`scratch/ms1954_pre_repair_qualification_conflation.py`
Job `job-5573f75ae9a3`:
- adapter had no separate qualification-source role;
- 16 qualification evidence rows were generated internally from forks of the same environment provider family;
- evidence source label was `EXTERNAL-WORLD-HOLDOUT`;
- Microseed correctly still granted evidence independence authority `NONE`.

Thus this was a substrate responsibility conflation, not an authority escalation inside Microseed.

## Minimum repair
Added external substrate roles:
- `QualificationSource` protocol;
- `ForkedWorldQualificationSource` shadow implementation.

`ShadowEnvironmentAdapter.train_actual_history(...)` now requires an explicit qualification source before any physical training actions occur.

Early gates:
- missing source -> `EXTERNAL_QUALIFICATION_SOURCE_REQUIRED`;
- source/world compatibility mismatch -> `QUALIFICATION_SOURCE_ENVIRONMENT_COMPATIBILITY_MISMATCH`.

Matched qualification samples are stamped with:
- qualification provider id;
- qualification provider compatibility fingerprint;
- evidence source `EXTERNAL-QUALIFICATION:<provider_id>`.

The qualifier role is structurally separate from the runtime world role.

## Verification
`scratch/ms1954_qualification_source_separation.py`
Job `job-3fdf71c5f931` PASS.

Observed:
- missing source: 0 physical outcomes before rejection;
- mismatched source: 0 physical outcomes before rejection;
- matched source: 16 qualification rows from `QUAL-MATCHED`;
- runtime world object is not the qualification-source world object.

Earned statement:
`RUNTIME_ENVIRONMENT_AND_QUALIFICATION_SOURCE_ARE_SEPARATE_SUBSTRATE_ROLES_WITH_COMPATIBILITY_BOUNDARY`.

## Nonclaim
Different provider roles or object instances do not prove physical/statistical independence.
`evidence_independence_authority` remains `NONE`.

A future production substrate may require stronger external attestation/provenance, but the experimental substrate no longer structurally self-qualifies inside the runtime adapter.