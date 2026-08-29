# MS1967 — Calibrated Observation-Frame Currentness

Date: 2026-08-29 ET
Status: composition result; no new calibration manager justified
Parent: MS1966 `dd868d5b176fddd65a7839cab58fcbbeb777421e`

## Discriminator
Can an explicitly bounded passive-observation calibration witness use existing OperationalFrame/currentness machinery so calibrated proto-reference evidence is consumable only while the exact sensor/environment calibration subject is current?

Prewrites:
- `CALIBRATION_EVIDENCE != NOISE_MODEL`;
- `OBSERVED_BOUND != FUTURE_BOUND`;
- `CALIBRATION_CURRENT != SENSOR_REGIME_CURRENT` unless exact subject is current;
- `CALIBRATED_BOUNDARY != REFERENT_IDENTITY`;
- `FRAME_REQUALIFICATION != SEMANTIC_SENSOR_ONTOLOGY`.

## Existing owner audit
`OperationalFrameRegistry` already provides:
- externally qualified frame registration;
- content-bound frame signature;
- explicit epoch currentness;
- `change(...)` staling and downstream invalidation;
- no claim that Microseed constructs/self-qualifies the frame.

Therefore MS1967 pressure-tested composition before adding a calibration-specific registry.

## Experiment
Scratch:
`scratch/ms1967_calibrated_observation_frame_currentness.py`

A bounded `CalibrationWitness` records:
- exact external sensor-regime subject signature;
- passive calibration evidence digest;
- maximum observed adjacent baseline delta;
- frame id/epoch;
- authority ceiling `OBSERVED_BASELINE_BOUND_ONLY`.

The witness is embodied as an externally/shadow-qualified `OperationalFrameContract` with DERIVED_READ_ONLY authority and explicit assistance ancestry.

### Low-noise frame
Passive baseline bound = `3.0`.
With matching external regime subject:
- frame is current;
- calibrated boundaries recover `(0,1)` and `(2,3)`;
- affordance-relative signatures derive normally;
- identity/semantic-reference authority remain NONE.

### Regime drift
The external sensor-regime subject changes to high-noise mode.
Before proto-reference nomination, exact subject mismatch causes existing `OperationalFrameRegistry.change(...)` to:
- increment old frame epoch;
- set old frame qualification to STALE;
- set frame currentness to STALE.

The attempted old-frame use returns:
`UNKNOWN_INCOMPLETE / CALIBRATION_FRAME_NOT_CURRENT_FOR_SENSOR_REGIME`.

### Fresh qualification
Fresh high-noise passive calibration is represented as a **new content-bound frame artifact**, not in-place resurrection of the stale low-noise frame.

Observed high-noise baseline bound = `15.0`.
The new frame is current and lawful, but the resulting referent partition remains fragmented:
`(0), (1), (2,3)`.

This is scientifically important:
`CURRENT_CALIBRATION != SUFFICIENT_ROBUST_OBSERVATION_FRAME`.

Currentness is necessary for lawful use but does not imply that the calibration representation is discriminatively adequate.

## Execution
Durable job:
`job-d60e3498790a`

Result: PASS / rc=0.

Earned:
`EXISTING_OPERATIONAL_FRAME_CURRENTNESS_CAN_OWN_BOUNDED_CALIBRATION_LIFECYCLE_WHEN_EXTERNAL_SENSOR_REGIME_COMPATIBILITY_IS_EXPLICIT`.

Requalification form:
`NEW_CONTENT_BOUND_FRAME_ARTIFACT_NOT_IN_PLACE_RESURRECTION`.

## Authority ceiling
- calibration authority: `OBSERVED_BASELINE_BOUND_ONLY`;
- future-noise-bound authority: NONE;
- general noise-model authority: NONE;
- referent identity authority: NONE;
- semantic reference authority: NONE;
- language authority: NONE.

## Minimum sufficient embodiment
No `microseed/**/*.py` production change is justified by MS1967.
Existing OperationalFrame/currentness owners are sufficient for the lifecycle/currentness part of the problem.

Do not add:
- generic calibration manager;
- self-authored sensor ontology;
- learned universal noise model;
- referent identity promotion.

## Next discriminator
The remaining problem is no longer calibration lifecycle ownership.

`CURRENT_CALIBRATION != SUFFICIENT_ROBUST_OBSERVATION_FRAME`.

Next pressure should ask whether existing multi-view/action-response evidence can supplement a current but weak boundary frame, or whether a genuinely new robust observation representation is required. A lower-risk sibling is noisy calibrated sensor handoff using separately current frames; prefer whichever discriminator most directly distinguishes composition from a new mechanism.