# MS1919 Pass 8 Evidence — Durable Probe Lifecycle Evidence Rechecks

## Discriminator
`CURRENT_STATE_LABEL != DURABLE_PROBE_LIFECYCLE_OWNERSHIP`

## Parent authority
- Parent sealed research head: `01fc8e0b359d470a0a2ec97ff15685c55b6c7af7` — MS1918.
- Canonical Main-Dev remains MS1527; no promotion.

## Why MS1919 intervened
The planned post-MS1918 frontier was:
`AUTHENTICATED_PROBE_EVIDENCE_AND_REVISIT != LAWFUL_REVISED_SURFACE_REBINDING`.

Initial audit found no auto-revision defect:
- authenticated surprise can create `MODEL_SPACE_CHALLENGE -> REVISIT_REQUIRED`;
- one such surprise does not create a bounded visible-history refinement in the current fixture;
- `derive_current_revisit_hypothesis_revision_surface(...)` remains `NO_CURRENT_REVISED_HYPOTHESIS_SURFACE`;
- old existing binding cannot be accepted for D-1904;
- successor creation remains blocked until a lawful accepted/staled revision exists.

Existing MS1859–1862 machinery already demonstrates that with sufficient admitted predecessor/current visible history, a bounded refinement may be proposed, but it remains proposal-only and requires external projection qualification before consequential use.

During this audit a higher-priority lifecycle defect was discovered.

## Verified pre-repair defect
MS1918 required discriminator satisfaction and authenticated admitted observation for `PROBE_AVAILABLE` program-step bearing and completed-program evidence.

However, the first valid bearing call itself can transition the deficit:
`PROBE_AVAILABLE -> REVISIT_REQUIRED`.

Later consumers keyed their MS1918 rechecks only to the current state label. Therefore the lifecycle transition could erase the evidence obligations that had justified the probe.

Reproduced unsafe paths:
1. valid authenticated bearing -> REVISIT_REQUIRED -> observation-use basis becomes stale -> completed-program evidence still recorded;
2. valid authenticated bearing -> REVISIT_REQUIRED -> source relation content drifts so independent discriminator satisfaction becomes UNKNOWN -> completed-program evidence still recorded;
3. valid bearing -> observation/basis stales -> repeated step-bearing still returns the existing MODEL_SPACE_CHALLENGE instead of becoming unresolved;
4. raw/unauthenticated caller-shaped outcome plus an unrelated/manual REVISIT_REQUIRED transition could reach completed-program evidence.

Corrected pre-repair hostile baseline: 4/6 fail in the unsafe direction, 2 controls pass.

## Embodied repair
Added one private lifecycle predicate in `microseed/runtime/entity.py`:
`_probe_lifecycle_evidence_rechecks_required(deficit)`.

Probe evidence obligations remain active when the deficit either:
- is currently `PROBE_AVAILABLE`, or
- retains a persistent bound `probe_capability_id`, or
- retains a persistent bound `probe_capability_epoch`.

Either partial persistent marker is sufficient to retain conservative evidence rechecks.

Exactly four evidence-consumer gates use the durable predicate:
1. repeated step-bearing independent program-discriminator satisfaction;
2. repeated step-bearing authenticated observation admission;
3. completed-program independent program-discriminator satisfaction;
4. completed-program authenticated observation admission.

Nomination, execution, generic program behavior, and unrelated lifecycle gates were not broadened.

An initially over-broad mechanical patch was caught by diff audit before execution, discarded by restoring `entity.py` to sealed MS1918, and reapplied surgically to only these four consumers plus the helper.

## Final hostile surface
`tests/embodiment/test_ms1919_pass08_probe_lifecycle_evidence_recheck.py`

Final 7/7 PASS:
1. basis drift after bearing cannot bypass completed-evidence authentication;
2. source-relation drift after bearing cannot bypass completed-evidence discriminator satisfaction;
3. repeated bearing after observation/basis staleness must recheck authenticated observation;
4. unrelated REVISIT_REQUIRED transition cannot turn raw outcome into probe program evidence;
5. current authenticated probe can still record completed evidence after bearing moves to REVISIT_REQUIRED;
6. authenticated challenge does not auto-create revision/current revised surface/successor;
7. repeated bearing after source-relation drift must recheck discriminator satisfaction.

## Mutation adequacy
Final isolated source-mutant job: `job-ae886ebb5e32`.
Receipt: `reports/ms1919_pass08_source_mutants/receipt.json`.

5/5 REJECTED; 0 survivors; 0 unknown:
- `COLLAPSE_PROBE_LIFECYCLE_TO_CURRENT_STATE`
- `DROP_BEARING_SATISFACTION_RECHECK`
- `DROP_BEARING_AUTHENTICATED_OBSERVATION_RECHECK`
- `DROP_COMPLETED_EVIDENCE_SATISFACTION_RECHECK`
- `DROP_COMPLETED_EVIDENCE_AUTHENTICATED_OBSERVATION_RECHECK`

All mutants completed. Clean production source SHA recorded by the mutant runner: `d66d412f11f9b312eeb8ec0c2dc8aba4dc8b37d2b661835d1d7fcef44f182b04` for its target file.

## Compatibility
Lifecycle/program neighborhood job `job-728f5bf10e26`: 34/34 PASS.

Selective regression job `job-761416c0ccd7`:
- modern: 30/30 PASS;
- inherited cleanup-neutral: 74/74 PASS;
- compileall PASS;
- overall PASS / COMPLETE.

Frozen exact base verifier job `job-ddc8805b9885`:
- frozen source snapshot start/end: `a1bffd49c3c4d56f7befff06bdc1e5c2a3ca66b60dada7e83658cd8c453843dd`;
- source stable;
- 177 test files;
- 636 selected PASS;
- zero negative groups;
- compileall PASS;
- four terminal route-only singleton timeout groups: `s23aaa`, `s24aaa`, `s25aaa`, `s26aaa`.

Terminal leaf closure job `job-eff828c4d371`:
- terminal files: MS1533, MS1534, MS1535, MS1598;
- expected 34 test nodes;
- 34/34 PASS;
- no missing/extra/duplicate nodes;
- zero negative groups;
- zero remaining unknown groups;
- source stable against the same frozen snapshot;
- completion PASS.

Final exact compatibility: **670/670 PASS across 177/177 test files**.

## Earned laws
- `CURRENT_STATE_LABEL != DURABLE_PROBE_LIFECYCLE_OWNERSHIP`.
- `LIFECYCLE_TRANSITION != EVIDENCE_GUARD_DISCHARGE`.
- `REVISIT_REQUIRED != PERMISSION_TO_SKIP_PROBE_AUTHENTICATION`.
- `REVISIT_REQUIRED != PERMISSION_TO_SKIP_DISCRIMINATOR_SATISFACTION`.
- `BOUND_PROBE_METADATA_CAN_CARRY_CONSERVATIVE_EVIDENCE_OBLIGATION_ACROSS_STATE_TRANSITION`.

## Deferred original frontier
`AUTHENTICATED_PROBE_EVIDENCE_AND_REVISIT != LAWFUL_REVISED_SURFACE_REBINDING` remains OPEN.

Current evidence says missing sufficient admitted visible history is the immediate reason the live MS1918/MS1919 surprise does not produce a bounded refinement; this is not evidence for a missing revision primitive.

## HSP/SOP interaction
The project-local HSP Model-Adequacy & Corroboration Amendment is now active for future frontier selection. Any HSP/Pareto frontier after MS1919 is advisory only; actual selection must remain external/explicit/traceable, with model adequacy and independence status recorded.

## Claim boundary
MS1919 repairs probe-lifecycle evidence obligations across a state transition. It does not qualify a revised model, answer the epistemic deficit, grant execution authority, or promote canonical Main-Dev.
