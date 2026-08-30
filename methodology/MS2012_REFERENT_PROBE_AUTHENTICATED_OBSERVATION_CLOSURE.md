# MS2012 — REFERENT PROBE AUTHENTICATED OBSERVATION CLOSURE

## Question
After a referent-derived P2 executes through ordinary action closure, can only an authenticated observation-admission path make that actual step admissible as epistemic program evidence and collapse the owned referent ambiguity?

## Pre-repair hostile
The existing MS1918 authentication recheck is tied to the PROBE_AVAILABLE lifecycle. MS2011 referent deficits remain ACTION_LIMITED and therefore may bypass that recheck. Execute the same referent-derived P2 twice in separate fixtures:
1. close via `record_bounded_action_outcome_via_observation_basis`;
2. close via a raw caller-built OBSERVATION_ONLY `Observation` using `record_bounded_action_outcome`, with no admission receipt.
Advance both trials from actual action-closure records and ask `record_completed_epistemic_program_evidence` to admit them.

## Positive closure
Authenticated P2 observation must:
- produce state-only epistemic outcome with prediction commitment UNKNOWN;
- produce one observation-admission receipt;
- admit an opaque transition sample;
- allow a post-P2 current raw receipt;
- extend the owned prefix to P0/P1/P2;
- collapse the live referent set to the actually observed historical bucket;
- complete the one-step trial and request REVISIT_REQUIRED with truth/answer/execution authority NONE.

## Repair criterion
If the forged raw observation is admitted as completed program evidence, separate observation-authentication eligibility from the older PROBE_AVAILABLE discriminator-satisfaction predicate. Reuse the existing `_authenticated_probe_program_step_observation`; do not force referent deficits into the unrelated PROBE_AVAILABLE contrast-satisfaction owner.

## Observed pre-repair violation
Direct hostile observation: the forged caller-built OBSERVATION_ONLY outcome was rejected by `derive_admitted_opaque_transition_sample()` as `AUTHENTICATED_OBSERVATION_INGRESS_REQUIRED`, yet `record_completed_epistemic_program_evidence()` still accepted the trial and moved the ACTION_LIMITED referent deficit to REVISIT_REQUIRED. This was a real evidence-laundering bypass.

## Repair
Added `_epistemic_program_step_observation_authentication_required(deficit)` as an orthogonal predicate. It returns true for the historical probe lifecycle *or* deficits with `DERIVED_FROM_CURRENT_PARTIAL_REFERENT_AMBIGUITY`. Existing discriminator-satisfaction checks remain exclusively under `_probe_lifecycle_evidence_rechecks_required`; referent deficits are not forced into the unrelated registered-contrast owner. Both `assess_epistemic_program_step_outcome_bearing()` and `record_completed_epistemic_program_evidence()` now use the new predicate only for authenticated observation ingress.

Post-repair: authenticated closure remains accepted and REVISIT_REQUIRED; forged closure is rejected and the deficit remains ACTION_LIMITED.
