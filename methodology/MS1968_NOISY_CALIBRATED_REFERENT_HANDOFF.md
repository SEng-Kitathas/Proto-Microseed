# MS1968 — Noisy Calibrated Referent Handoff

Date: 2026-08-29 ET
Status: research ↔ reality composition result; no core mutation
Parent: MS1967 `cc32c0064b708a2d5a1f474b13e4bc154a38cdb7`

## Discriminator
Can operational proto-referent continuity survive a noisy old→overlap→new sensor-layout handoff when each layout is governed by a separately qualified/current calibration frame, rather than one persistent shared frame identity?

Prewrites:
- `FRAME_IDENTITY != REFERENT_IDENTITY`;
- `FRAME_CURRENTNESS != CROSS_FRAME_CONTINUITY`;
- `HISTORICAL_REFERENT_SIGNATURE != CURRENT_FRAME_AUTHORITY`;
- `OVERLAP_BRIDGE != NUMERICAL_OBJECT_IDENTITY`.

## Reality world
`research/substrate_shadow/noisy_referent_handoff_world_server.py`

Separate-process world exposes:
- OLD sensor layout;
- OVERLAP old+new layout;
- NEW sensor layout;
- two latent causal sources;
- independent bounded channel jitter.

Each phase starts a fresh observation epoch.

## Calibration/frame lifecycle
For each phase:
1. collect nine passive fixed-state observations;
2. derive maximum observed adjacent jitter bound (`3.0`);
3. create a content-bound SHADOW_QUALIFIED OperationalFrameContract for that exact phase/layout subject;
4. derive calibrated change boundaries only while that frame is current.

At handoff:
- `CAL-OLD` is explicitly staled before overlap;
- `CAL-OVERLAP` is explicitly staled before new;
- `CAL-NEW` remains current at final state.

Historical affordance signatures remain evidence but do not keep their source frame current.

## Result
Scratch:
`scratch/ms1968_noisy_calibrated_referent_handoff.py`

Durable job:
`job-0187bf09a79b`

PASS / rc=0.

OLD groups:
- `(0,1)` -> signature `314f0740...` -> evaluator latent source 0;
- `(2,3)` -> signature `7497dbe2...` -> evaluator latent source 1.

OVERLAP groups bridge channels from both layouts:
- `(0,1,5,7)` -> same source-0 signature;
- `(2,3,4,6)` -> same source-1 signature.

NEW groups:
- `(1,3)` -> same source-0 signature;
- `(0,2)` -> same source-1 signature.

The exact set of two operational affordance signatures is stable old→overlap→new despite different sensor layouts and different current calibration-frame identities.

Earned:
`SEPARATELY_CURRENT_CALIBRATED_SENSOR_FRAMES_CAN_SUPPORT_OPERATIONAL_PROTO_REFERENT_CONTINUITY_ACROSS_NOISY_LAYOUT_HANDOFF_WITHOUT_SHARED_FRAME_IDENTITY`.

## Authority ceiling
- continuity authority: `OPERATIONAL_REFERENT_CONTINUITY_ONLY`;
- frame identity authority: NONE;
- numerical identity authority: NONE;
- semantic reference authority: NONE;
- language authority: NONE.

## Minimum sufficient embodiment
No `microseed/**/*.py` change is justified.
Existing OperationalFrame currentness + existing affordance-relative referent signatures compose across the noisy handoff.

## Next discriminator
No-overlap disappearance/reappearance:

Can a reappearing operational signature be lawfully re-associated after an observation gap, and can a hidden same-affordance substitution demonstrate that such re-association still does **not** prove numerical persistence?

Prewrite:
`SIGNATURE_REASSOCIATION != INDIVIDUAL_PERSISTENCE`.