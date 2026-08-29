# MS1952 — Environment Compatibility Reentry Boundary

Date: 2026-08-29 ET
Status: pre-repair violation reproduced; shadow-adapter repair verified
Parent reality tranche: MS1949–1951

## Question
If a restarted environment exposes the same adapter IDs and same action ID but materially different dynamics, can historical competence become current merely because epochs/interface names line up?

Prewrite:
- `SAME_ADAPTER_INTERFACE != SAME_ENVIRONMENT_DYNAMICS`;
- `CAPABILITY_IDENTITY_REATTACHMENT != WORLD_DYNAMICS_EQUIVALENCE`;
- `HISTORICAL_COMPETENCE_REACTIVATION_REQUIRES_ENVIRONMENT_COMPATIBILITY`.

## Pre-repair hostile
`scratch/ms1952_cross_world_compatibility_hostile.py`

Original world:
`CHARGE -> LEVEL-2`, value 2.4.

Drifted world:
- same world name;
- same action id `CHARGE`;
- same adapter ids/scope;
- but `CHARGE -> LEVEL-1`, value 0.0.

Job `job-f6d5bf275b3a` reproduced a real violation:
- old relation became CURRENT after incompatible attach;
- old proposal became CURRENT;
- old prediction remained `LEVEL-2` while new world would produce `LEVEL-1`.

Cause:
Action-outcome structural currentness binds capability epoch but not capability content signature. Across process restart, a fresh same-id capability can again be epoch 0. The shadow adapter had no independent environment-compatibility premise, so historical competence could be misbound across changed dynamics.

This is a substrate/reality membrane defect. It does not require semantic world identity inside Microseed.

## Minimum repair
Reuse existing Microseed historical-admission premise machinery.

The shadow adapter now requires an externally declared 64-hex `compatibility_sha256` for each world contract and registers a current `SUBSTRATE-ENV-BINDING` DERIVED_READ_ONLY capability whose content signature binds:
- environment compatibility fingerprint;
- current action capability signatures;
- observation capability signature;
- observation-basis signature.

Every adapter-recorded action outcome now uses this environment-binding capability as its historical admission basis. Learned relation evidence therefore carries the environment-binding **content signature** as an exact currentness premise.

This grants no truth or execution authority. It only answers whether historical competence was earned under a compatible declared environment contract.

## Post-repair pressure
Parallel regression tranche:
- MS1949 `job-86f3e6f857f9`: PASS;
- MS1950 `job-723f3ee32a12`: PASS;
- MS1951 `job-5c9e305c8a15`: PASS;
- MS1952 incompatible-dynamics hostile `job-36547ea44f8e`: BLOCKED as intended.

In the incompatible world after repair:
- relation = `STALE_PREDICTIVE_RELATION / STRUCTURAL_PREMISE_NOT_CURRENT`;
- proposal = `UNKNOWN_INCOMPLETE / REHEARSAL_EVIDENCE_PREMISE_SIGNATURE_DRIFT:SUBSTRATE-ENV-BINDING`.

The old prediction is therefore not action-usable before any contradictory physical execution is required.

## Earned result
`HISTORICAL_WORLD_COMPETENCE_REACTIVATION_REQUIRES_CURRENT_CONTENT_BOUND_ENVIRONMENT_COMPATIBILITY`.

Preserve:
- `WORLD_NAME != WORLD_COMPATIBILITY`;
- `SAME_ACTION_ID != SAME_ACTION_DYNAMICS`;
- `SAME_EPOCH_AFTER_RESTART != SAME_STRUCTURAL_PREMISE`;
- `ENVIRONMENT_COMPATIBILITY_BASIS != TRUTH_AUTHORITY != EXECUTION_AUTHORITY`.

No Microseed-core mutation was required. The fix lives at the external substrate adapter membrane using an already-earned core currentness mechanism.