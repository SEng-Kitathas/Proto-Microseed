# MS1979 — Raw Observation Receipt Currentness / Replay

Date: 2026-08-29 ET
Status: hostile verification of MS1978 raw-coordinate ingress; no additional Microseed-core mutation
Parent: MS1978 core draft on MS1976 baseline

## Question
Are durable raw-coordinate receipts treated as bounded exact-premise evidence, or can they become timeless sensor truth / silently survive ambiguity?

Prewrites:
- `RAW_RECEIPT_PERSISTED != RAW_RECEIPT_CURRENT`;
- `DUPLICATE_RAW_RECEIPTS != ARBITRATION_AUTHORITY`;
- `FRAME_ID != FRAME_CONTENT`;
- `RESTART_PERSISTENCE != AUTOMATIC_REAUTHORIZATION`;
- `COORDINATE_LIMIT != FEATURE_ONTOLOGY`.

## Experiment
Scratch:
`scratch/ms1979_raw_observation_receipt_currentness.py`

Durable job:
`job-bc10cdad4c86` PASS / rc=0.

### Coordinate bound refusal
A two-coordinate process observation was presented to a call bounded at `max_coordinates=1`.

Result:
- `RAW_OBSERVATION_REJECTED`;
- reason `BOUNDED_RAW_TOKENS_REQUIRED`;
- evidence id was not persisted.

Thus the ingress bound is enforced before durable admission.

### Duplicate current receipts
Two separately persisted raw receipts were bound to the same exact current control-state evidence before one action execution.

Result:
- derived raw projection sample count = 0;
- sample rejection = `EXACT_SINGLE_CURRENT_RAW_OBSERVATION_FOR_CONTROL_STATE_REQUIRED`.

No deterministic tie-break or last-write-wins behavior was used.

Earned:
`DUPLICATE_CURRENT_RAW_OBSERVATIONS_DO_NOT_CREATE_IMPLICIT_ARBITRATION_AUTHORITY`.

### Frame drift
Before drift, one raw receipt + actual outcome produced one admitted owned projection sample.

After `frames.change('F')`:
- admitted sample count = 0;
- raw receipt rejected `RAW_OBSERVATION_FRAME_NOT_CURRENT`;
- authenticated transition rejected `OPERATIONAL_FRAME_NOT_CURRENT`.

Thus raw receipt currentness and transition currentness fail together under the same sensor/frame drift.

### Restart without attachment
After process/runtime restart, durable raw receipt evidence remains in the EvidenceLedger.

Without live observation/frame/action contracts:
- sample count = 0;
- raw receipt rejected `RAW_OBSERVATION_CAPABILITY_NOT_CURRENT`.

No automatic restart authority exists.

### Compatible reattachment
A fresh runtime reattached the same exact observation/action/frame contracts.

The durable raw receipt + durable authenticated action/outcome history rejoined lawfully and produced exactly one projection sample:
- raw tokens `('0','1')`;
- effect token `ODD`.

No raw token was supplied to the re-derivation call.

Earned:
`OWNED_RAW_OBSERVATION_RECEIPTS_ARE_BOUNDED_EXACT_PREMISE_EVIDENCE_NOT_TIMELESS_SENSOR_TRUTH_AND_COMPATIBLE_REATTACHMENT_CAN_REACTIVATE_THEIR_USE`.

## Authority ceiling
- automatic duplicate arbitration: NO;
- automatic restart authority: NO;
- semantic coordinate authority NONE;
- truth authority NONE;
- language authority NONE.

## Next discriminator
Test higher-arity owned raw support inside the already-existing bounded projection grammar. Use a process world where every 1- and 2-coordinate subset is insufficient but a 3-coordinate conjunction is predictive.

If max subset 2 fails and max subset 3 succeeds using only owned raw receipts, representation support growth is compositional within the existing grammar rather than an XOR-specific repair.