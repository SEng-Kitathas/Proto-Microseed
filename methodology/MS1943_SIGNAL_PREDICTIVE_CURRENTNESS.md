# MS1943 — Opaque Signal Predictive Currentness Without Convention Rewrite

Date: 2026-08-29 ET
Status: composition-only mechanism closed; regression embodiment pending integrated release validation at time of writing
Parent local research head: `4c46d21f7665c439f4b8a8f578a5e9d94628c6f6`

## Question
When repeated external outcomes contradict a currently qualified opaque signal-response predictive relation, can existing predictive-currentness machinery expose the learned operational association as stale while leaving the externally supplied coordination contract current and untouched and without inventing new token meaning?

Prewritten boundaries:
- `PREDICTIVE_DRIFT != SEMANTIC_CONVENTION_CHANGE`;
- `STALE_SIGNAL_MODEL != NEW_TOKEN_MEANING`;
- `MODEL_REPLACEMENT != COORDINATION_CONTRACT_REWRITE_AUTHORITY`;
- `FAILED_SIGNAL_PREDICTION != COORDINATION_CONTRACT_STALE_BY_FIAT`;
- `MODEL_CURRENTNESS_OWNER != COORDINATION_CURRENTNESS_OWNER`.

## Existing mechanism inspection
No new production mechanism was needed.

MS1452 already supplies the relevant owner:
- `assess_action_outcome_predictive_currentness(...)` evaluates post-admission outcomes in bounded windows;
- isolated/transient errors can remain current;
- two consecutive below-threshold windows create a durable `DRIFT_WITNESS`;
- `action_outcome_predictive_relation_status(...)` then reports `STALE_PREDICTIVE_RELATION / EMPIRICAL_DRIFT_WITNESS`;
- history is retained;
- `nominate_action_outcome_replacement_candidates(...)` may propose a drift-scoped replacement from the exact drift evidence;
- replacement qualification, model switch, drift-cause identity, semantic-regime identity and truth authority remain absent.

This currentness owner is separate from `OperationalCoordinationRegistry`, which owns the externally qualified coordination contract and its epoch/signature/currentness.

## Composition-only experiment
Project-local probe:
`sandbox/temp/ms1943_predictive_currentness_composition_probe.py`
SHA-256 `51f3d190f18e97a37cbceb0698c1959bc4f60baa419ca22742f6d73ef0b10358`.

Durable job:
`job-99e181d82163`.

Receipt:
`sandbox/temp/MS1943_PREDICTIVE_CURRENTNESS_COMPOSITION_PROBE_RECEIPT.json`
SHA-256 `236bb26acb920cde88b38438298639b2c7a9e1e0f2ac95e78e30ad9590946afd`.

Result: 9/9 checks PASS.

### Isolated miss
After qualifying the learned `SIG-T0 -> CP-ACK` relation, one contradictory `T0 -> CP-NOACK` outcome plus seven matching outcomes produced:
- window accuracy `0.875`;
- `CURRENT_WITHIN_BOUNDS`;
- relation remains `CURRENT_PREDICTIVE_RELATION`;
- coordination epoch/signature/currentness unchanged.

Therefore:
`ONE_SIGNAL_PREDICTION_MISS != PREDICTIVE_DRIFT`.

### Transient bad window then recovery
Eight contradictory outcomes followed by eight matching outcomes produced:
- window accuracies `[0.0, 1.0]`;
- `CURRENT_WITHIN_BOUNDS`;
- relation remains current;
- coordination exact subject unchanged.

Therefore:
`TRANSIENT_BAD_PREDICTIVE_WINDOW != SEMANTIC_CONVENTION_CHANGE`.

### Sustained contradiction
Sixteen consecutive contradictory outcomes produced:
- window accuracies `[0.0, 0.0]`;
- `DRIFT_WITNESS`;
- old learned relation -> `STALE_PREDICTIVE_RELATION / EMPIRICAL_DRIFT_WITNESS`;
- historical relation preserved;
- zero-row rehearsal can no longer use the stale relation;
- coordination contract remains exact at epoch `0`, current `true`, signature `b1fb449f08bcec8017e99c8aedf38b23f4d637f4fca4c2213c078ab00ee29eeb`;
- no coordination mutation was invoked or inferred.

A replacement candidate was nominated from the 16 exact drift outcomes:
- next state `CP-NOACK`;
- value effect `0.0`;
- support `16`;
- consistency `1.0`;
- qualification authority `NONE`;
- model-switch authority `NONE`;
- semantic-regime authority `NONE`;
- no replacement relation was admitted.

The external fixture's expected token changed to `T1`, but Microseed did not infer a new token, new meaning, or coordination rewrite.

Therefore:
`SUSTAINED_OUTCOME_CONTRADICTION -> LEARNED_RELATION_EMPIRICAL_STALENESS` under the supplied MS1452 bounds,
while
`LEARNED_RELATION_EMPIRICAL_STALENESS != COORDINATION_CONTRACT_STALENESS`.

### Recovery after durable drift
Sixteen later matching outcomes did not reactivate the historical stale relation. The durable drift witness remained currentness-negative while the coordination contract remained unchanged.

Therefore:
`LATER_PREDICTIVE_RECOVERY != AUTOMATIC_HISTORICAL_MODEL_REACTIVATION`.

## Authority and semantic ceiling
Throughout the experiment:
- drift-cause authority `NONE`;
- semantic-regime authority `NONE`;
- model-switch authority `NONE`;
- no `signal_policy` surface;
- no token-meaning registry;
- no auto-switch API;
- language status remains `DEFERRED_PRELINGUAL_COGNITION_ACTIVE`.

MS1943 does not establish:
- semantic convention detection;
- token meaning;
- reference;
- endogenous token invention;
- coordination-contract rewrite authority;
- automatic model replacement;
- language.

The empirical owner can only say the previously qualified predictive relation no longer survives its bounded post-admission currentness criterion.

## Minimum Sufficient Embodiment
Because existing MS1452 + MS1941 composition closes the discriminator, **no production-code mutation is justified**.

MS1943 embodiment is regression evidence only:
`tests/embodiment/test_ms1943_signal_predictive_currentness.py`.

This is a direct RAHL minimum-sufficient result:
`MISSING_BEHAVIOR != MISSING_MECHANISM`.

## New earned distinctions
- `ONE_SIGNAL_PREDICTION_MISS != PREDICTIVE_DRIFT`;
- `TRANSIENT_BAD_PREDICTIVE_WINDOW != SEMANTIC_CONVENTION_CHANGE`;
- `SUSTAINED_OUTCOME_CONTRADICTION -> LEARNED_RELATION_EMPIRICAL_STALENESS` under declared bounds;
- `LEARNED_RELATION_EMPIRICAL_STALENESS != COORDINATION_CONTRACT_STALENESS`;
- `LATER_PREDICTIVE_RECOVERY != AUTOMATIC_HISTORICAL_MODEL_REACTIVATION`;
- `REPLACEMENT_CANDIDATE != QUALIFIED_REPLACEMENT_RELATION`.

## Next discriminator
If MS1943 regression/integrated validation closes, the next highest-information signaling question is **replacement qualification without semantic convention promotion**:

> Can the proposal-only `CP-NOACK` replacement relation earn fresh exact-subject external qualification and re-enter rehearsal while the coordination contract still remains unchanged and no semantic convention identity is inferred?

This is intentionally narrower than automatic adaptation. Prewrite:
- `FRESH_REPLACEMENT_QUALIFICATION != SEMANTIC_CONVENTION_IDENTIFICATION`;
- `QUALIFIED_REPLACEMENT_MODEL != COORDINATION_CONTRACT_REWRITE`;
- `REHEARSAL_REENTRY != AUTO_SWITCH_AUTHORITY`.
