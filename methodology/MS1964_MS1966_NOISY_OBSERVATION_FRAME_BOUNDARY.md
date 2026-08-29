# MS1964–MS1966 — Noisy Observation / Calibration Currentness Boundary

Date: 2026-08-29 ET
Status: reality boundary localized; robust observation-frame owner remains open
Parent scientific lineage: MS1958–MS1963 proto-reference

## Question
Does the newly earned proto-reference mechanism remain lawful under raw sensor jitter, and if not, is the missing mechanism referent identity or observation/change-frame construction?

## MS1964 — exact change detection fails under noisy reality
Reality world:
`research/substrate_shadow/noisy_referent_world_server.py`.

The world retains two external latent sources and four channels. True source changes are large, but every observation includes small independent channel jitter.

Scratch:
`scratch/ms1964_noisy_referent_boundary_hostile.py`

Job `job-ee02c291b23d` returned `BOUNDARY_CONFIRMED`.

With exact adjacent inequality:
- every channel changed at every sample;
- all channel boundary signatures became `(1,2,3,4,5,6,7,8)`;
- `nominate_by_boundary_coherence(...)` correctly returned `UNKNOWN_INCOMPLETE / BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS`.

Counterfactual evaluator-only threshold 8 recovered the true two groups `(0,1)` and `(2,3)`.

Earned:
`RAW_NOISY_OBSERVATIONS_DEFEAT_EXACT_REFERENT_BOUNDARY_COHERENCE_WHILE_SUPPLIED_ROBUST_CHANGE_DETECTION_RECOVERS_THE_PARTITION`.

Missing owner localized to:
`ROBUST_OBSERVATION_FRAME_OR_CHANGE_DETECTOR_NOT_REFERENT_IDENTITY`.

The supplied threshold is assistance only and grants no noise-model authority.

## MS1965 — passive bounded calibration can recover this world
Scratch:
`scratch/ms1965_passive_calibrated_change_frame.py`

Job `job-b28c9da0b92a` PASS.

Before acting, repeated passive observations were collected while the external latent state remained fixed. Across four starting phases of the deterministic jitter pattern:
- maximum observed adjacent jitter delta = 3;
- classifying only changes strictly greater than that observed baseline bound recovered `(0,1)` and `(2,3)`;
- affordance-relative proto-referent signatures remained identical across all four runs.

Earned:
`PASSIVE_FIXED_STATE_OBSERVATIONS_CAN_SUPPLY_A_BOUNDED_JITTER_CALIBRATION_THAT_RECOVERS_PROTO_REFERENT_CHANGE_STRUCTURE_UNDER_THIS_NOISY_WORLD`.

Authority ceiling:
- calibration authority `OBSERVED_BASELINE_BOUND_ONLY`;
- future noise bound authority NONE;
- general noise-model authority NONE.

Preserve:
`OBSERVED_BASELINE_JITTER_BOUND != GENERAL_NOISE_MODEL_OR_FUTURE_BOUND`.

## MS1966 — calibration currentness hostile
After the low-jitter calibration completed, the external process switched to a higher-noise mode where one channel gained nuisance changes exceeding the old observed bound.

Scratch:
`scratch/ms1966_calibration_currentness_hostile.py`

Job `job-fa2dbc28bb8d` returned `BOUNDARY_CONFIRMED`.

Using the old bound 3 after drift:
- channel 0 boundaries became every sample `(1..8)`;
- channel 1 retained `(2,5,7)`;
- channels 2/3 retained `(4,5,8)`;
- nomination fractured to `(0)`, `(1)`, `(2,3)`.

Earned:
`PASSIVE_CALIBRATION_CAN_BECOME_STALE_UNDER_SENSOR_NOISE_DRIFT_AND_MUST_NOT_BE_TREATED_AS_TIMELESS_FRAME_TRUTH`.

Missing owner:
`CALIBRATION_OR_OBSERVATION_FRAME_CURRENTNESS_AND_REQUALIFICATION`.

## Architectural consequence
Do NOT repair this by teaching `referents.py` a magic epsilon.

The referent owner is operating correctly on the boundary evidence it receives. The unresolved layer is upstream:
- robust observation/change-frame construction;
- calibration provenance/currentness;
- requalification or abstention after sensor/noise regime drift.

Existing research history already marked change detectors as supplied assistance in the event-frame/referent campaigns. MS1964–66 converts that old assistance denominator into a concrete reality-facing blocker.

## Exact next discriminator — MS1967
Can an explicitly bounded/current **observation calibration witness** be represented using existing frame/currentness owners so that:
1. calibration is valid only for one exact sensor/environment compatibility subject;
2. calibrated boundary derivation is allowed only while that witness is current;
3. sensor regime drift stales/blocks the derived boundary frame before referent nomination;
4. requalification can restore use;
5. no generic learned noise model or semantic sensor ontology is introduced?

Composition-first. Prefer existing OperationalFrame/currentness/qualification machinery before new calibration registries.