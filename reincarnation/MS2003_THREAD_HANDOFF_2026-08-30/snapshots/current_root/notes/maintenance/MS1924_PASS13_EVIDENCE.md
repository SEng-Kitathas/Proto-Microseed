# MS1924 Pass 13 Evidence — Restart History Is Not Reauthorization

## Discriminator
`HISTORY != CURRENT_AUTHORITY`

Companion law:
`RESTARTED_STATE != REAUTHORIZED_STATE`.

## Sealed parent
- Parent experimental head: `646f3a5ca9acd311ff30c436d63a5cf0f1fe1e78` — MS1923.
- Canonical Main-Dev remains MS1527; no promotion.

## Classification
NEGATIVE / NO_PRODUCTION_CHANGE.

The audit did not reproduce a restart/re-entry path that restores current selection or execution authority from historical state alone.

## New MS1924 audit
Test file:
`tests/embodiment/test_ms1924_pass13_restart_history_not_reauthorization.py`

Final result: 2/2 PASS.

### Ranger 1 — caller-retained direct-probe trial after restart
Before restart:
- current control state `s1`;
- current direct-probe decision surface exists;
- trial is instantiated;
- grounded epistemic program-step intent can be nominated.

After closing and reopening the same Microseed store:
- historical control-state observation `s1` is reconstructed with its historical evidence ID;
- capability contracts/providers are not automatically restored;
- retained trial cannot re-earn current discriminator satisfaction;
- nomination abstains at the local precheck;
- no new intent/execution record is created.

Interpretation:
historical/current-state representation can survive restart without restoring the operational contracts and current ancestry required for authority.

### Ranger 2 — historical restart cannot rematerialize direct-probe surface/trial
Before restart the current revised direct-probe decision surface exists.
After restart:
- direct-probe program candidate abstains;
- direct-probe decision surface abstains;
- execution authority remains NONE;
- no persistent `trial_registry` or `epistemic_program_trials` surface exists.

Interpretation:
trial/program representation is not durably reloaded as current executable state.

## Existing reentry owner
`microseed/development/reentry.py` already separates historical projection from authority:
- historical replay records use `HISTORICAL_NOMINATION_ONLY`, `HISTORICAL_STALE`, or `HISTORICAL_CONFLICT` states;
- `HistoricalReentryProjection.authority = NONE`;
- external `ReentryWarrant` must itself carry authority NONE;
- `assess_reentry(...)` checks historical fingerprint, provider compatibility, executable challenge, evidence-plane separation, requested diagnostic scope, dependency currentness, and cycles;
- even a fully green result is only `READY_FOR_EXISTING_REGISTRATION_PATH` with authority NONE.

The ordinary existing registration path remains the sole owner of current operational authority.

## Focused restart/reentry verification
Durable job: `job-9754b80bd6ed`.

Included:
- MS1502 integration;
- MS1527 integration/reentry owner tests;
- MS1841 revisit restart;
- MS1844 bearing replay suppression after restart;
- MS1874 stale revision restart behavior;
- MS1885 successor deficit restart/projection drift;
- MS1909 discriminator satisfaction restart;
- MS1924 audit.

Result: **30/30 PASS**.

MS1527 already independently verifies:
- history survives while current operational authority does not;
- projection is read-only and does not persist readiness;
- provider/executable/scope/dependency planes remain orthogonal;
- READY result is authority NONE and does not register;
- existing registration paths remain the only current authority owner;
- no loader/snapshot/auto-reentry API is promoted.

## Selective regression
Durable job: `job-49d93027f4ec`.

- modern: 30/30 PASS;
- inherited cleanup-neutral: 74/74 PASS;
- compileall PASS;
- stderr empty.

## Production compatibility boundary
No production source changed in MS1924. Production exact compatibility therefore remains inherited from the latest production-changing sealed pass MS1919: 670/670 across 177 files.

MS1920–MS1924 are test/audit-only seals unless separately stated; their added audit tests do not change production behavior.

## Earned laws
- `HISTORY != CURRENT_AUTHORITY`.
- `RESTARTED_STATE != REAUTHORIZED_STATE`.
- `HISTORICAL_CONTROL_STATE_REPRESENTATION != CURRENT_OPERATIONAL_CONTRACT`.
- `READY_FOR_EXISTING_REGISTRATION_PATH != REGISTRATION`.
- `REENTRY_WARRANT != EXECUTION_AUTHORITY`.
- `RESTARTED_TRIAL_REFERENCE != CURRENT_TRIAL_AUTHORIZATION`.

## Claim boundary
MS1924 does not prove universal restart safety for every future artifact type. It verifies the currently embodied restart/reentry surfaces and direct-probe lineage under the audited owners. Reopen if a later persistent trial/registry/snapshot mechanism is introduced or if restart begins restoring provider/handler/currentness state automatically.
