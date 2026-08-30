# MS1993 — Intervention-Bound Operational Persistence

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1992 `9427eaacf8f07655dfb08264a22a82c6f14bc61d`

## Question
Can an already lawful, represented intervention leave a content-bound trace that survives an observation gap and strengthens external referent re-association into operational persistence support, without claiming numerical object identity?

Prewrites:
- `INTERVENTION_BOUND_CONTINUITY != NUMERICAL_IDENTITY`;
- `PERSISTENT_CAUSAL_TRACE != METAPHYSICAL_SAMENESS`;
- `OPERATIONAL_PERSISTENCE_SUPPORT != SEMANTIC_OBJECT_REFERENCE`;
- `TRACE_LOSS_CAN_REFUTE_THIS_PERSISTENCE_HYPOTHESIS_WITHOUT_PROVING_REPLACEMENT`;
- `PERFECT_COPY_WITH_RETAINED_TRACE_REMAINS_IDENTITY_AMBIGUOUS`.

## Existing substrate
MS1958–MS1970 already earned, in bounded form:
- boundary-coherent proto-referent partitions;
- affordance-relative referent signatures;
- overlap-bound continuity;
- calibrated noisy handoff;
- gap reappearance with operational re-association;
- explicit refusal to promote reappearance into numerical identity;
- split/decomposition evidence without genealogy promotion.

MS1969 specifically showed that same-affordance reappearance after an unobserved gap cannot distinguish persistence from hidden substitution.

## Process world
Server:
`research/substrate_shadow/referent_intervention_trace_world_server.py`.

The evaluator maintains two latent sources projected through four opaque channels. Microseed-visible operations are only:
- observe current channels;
- execute already represented effects `FX-A`, `FX-B`, `FX-G`;
- execute represented marker action `FX-MARK-A`;
- enter an observation gap;
- reappear.

Three hidden evaluator variants exist:
1. `PERSIST`: source persists and retains intervention mark;
2. `REPLACE_UNMARKED`: latent generation changes and the replacement lacks the mark;
3. `REPLACE_PERFECT_COPY`: latent generation changes but the replacement carries the same mark.

Generation counters are evaluator-only falsification evidence and are not used by the organism route.

## Boundary construction
Scratch:
`scratch/ms1993_intervention_bound_operational_persistence.py`.

The existing referent functions first nominate the target channel group and derive its affordance-relative signature from represented action effects.

`FX-MARK-A` then changes exactly the nominated target group. A SHA-256 trace digest binds:
- target group;
- pre-intervention values;
- post-intervention values;
- observed delta;
- exact action ID.

The mark is an additive persistent channel term, so action-effect deltas remain unchanged. Therefore the existing affordance signature still re-associates the same operational referent after the gap.

## Three-world result
### Persistent world
- evaluator generation unchanged;
- affordance-relative re-association succeeds;
- intervention trace retained;
- operational persistence support: `SUPPORTED`.

### Unmarked replacement
- evaluator generation changes;
- same affordance-relative re-association still succeeds;
- intervention trace is absent;
- operational persistence support for this trace: `REFUTED_FOR_THIS_TRACE`.

This shows the intervention trace adds discriminating evidence beyond bare affordance reappearance.

### Perfect-copy replacement
- evaluator generation changes;
- affordance-relative re-association succeeds;
- intervention trace retained;
- organism-visible evidence is operationally indistinguishable from the persistent case.

Therefore retained trace cannot establish numerical identity.

## Earned
`INTERVENTION_BOUND_CAUSAL_TRACE_CAN_SUPPORT_OPERATIONAL_PERSISTENCE_ACROSS_AN_OBSERVATION_GAP_WITHOUT_ESTABLISHING_NUMERICAL_IDENTITY`.

Authority ceiling:
- operational persistence authority: `TRACE_RELATIVE_ONLY`;
- numerical identity: NONE;
- semantic reference: NONE;
- language: NONE.

Remaining boundary:
`PERFECT_COPY_WITH_RETAINED_TRACE_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE`.

## Mechanism verdict
No new referent-core mechanism is required for this level of persistence support.

Existing components compose lawfully:
1. boundary coherence nominates an operational referent partition;
2. affordance-relative signature re-associates it across the gap;
3. represented intervention supplies a content-bound causal trace;
4. retained/lost trace supplies additional operational persistence evidence.

So:
`MISSING_BEHAVIOR != MISSING_MECHANISM` applies again.

A new object manager, persistent object ID, genealogy layer, or semantic reference system would be premature.

## Final verification
- focused MS1958–MS1970 + MS1993 referent regression: `job-7e970e912589` -> **11/11 PASS in 1.71s**;
- whole cleanup-neutral embodiment suite: `job-65c8c2e1d49f` -> **790/790 PASS in 494.89s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
