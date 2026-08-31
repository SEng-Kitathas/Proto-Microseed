# MS2062 — Bound Learned Request-Target Specialization

## Why this embodiment exists
MS2061 verified the first irreducible donor-transfer gap: ordinary action intents do not bind runtime request-target parameters, so a generic request channel permits caller target substitution after deliberation and collapses target-conditioned learning by capability ID.

## Minimal repair
Do not add a hierarchy manager, desired-state registry, or generic parameterized-action system.

Add one authority-attenuating specialization path:
- base must already be a current externally qualified EFFECT request channel that explicitly declares `OPAQUE_PROJECTION_BUCKET_SPECIALIZABLE`;
- target must be one bucket from the exact current vocabulary of an **endogenous proposal that was externally qualified** as an opaque epistemic projection;
- derived capability ID/signature content-bind base capability ID/epoch/signature + target projection ID/epoch/signature + target bucket token;
- derived capability inherits base authority, qualification, obligation and operational scope unchanged;
- local subordinate means remain outside the specialization;
- runtime target override is forbidden;
- base capability drift stales the specialization through ordinary capability dependencies;
- projection drift stales the specialization through a new projection->capability currentness edge.

This is authority attenuation, not new EFFECT qualification:
`SPECIALIZING_ALREADY_QUALIFIED_EFFECT_CHANNEL_TO_FIXED_CURRENT_TARGET != MINTING_NEW_EFFECT_AUTHORITY`.

## Hostiles
- two learned buckets must create two different immutable capability identities before deliberation;
- arbitrary caller token rejected;
- supplied projection rejected;
- runtime override rejected;
- projection drift stales specialization but not base request channel;
- base-channel drift stales specialization transitively;
- ordinary effect capability without explicit request-target specialization interface cannot be recast;
- target binding grants no semantic desired-state or local-means authority.

## Boundary
This does not construct semantic goals, generate arbitrary new target representations, qualify new physical EFFECT channels, or solve recursive hierarchy. It only lets an already-qualified request channel lawfully bind one already-earned opaque current representation target into action identity.

## First harness scar
Initial focused run failed during test collection with `SyntaxError: positional argument follows keyword argument` in the MS2062 base request `CapabilityContract` fixture. Production modules had already compiled successfully; no MS2062 behavior was exercised.

Classification: `MS2062_TEST_CAPABILITY_CONSTRUCTOR_SYNTAX_ERROR__HARNESS_FAILURE_BEFORE_BEHAVIOR`. The test constructor was corrected from mixed positional/keyword fields to explicit `currentness=` and `resources=` with production bytes unchanged.

## Second test/API correction
The first behavioral run reached **5 PASS / 2 FAIL**. Both failures were test/API mismatches rather than carrier failures:
1. direct `CapabilityRegistry.invoke` was called without the required `QueryObligation`; corrected to pass the same bounded obligation and inspect the `CAPABILITY_RESULT.value` payload;
2. the test expected `capability_signature_sha256` to be duplicated inside ordinary serialized `BoundedActionIntent`. Ordinary intents bind capability ID + epoch and the registered capability content owns its signature. The hostile now asserts distinct specialized capability IDs/signatures before intent creation and distinct resulting intent IDs, without adding a redundant intent field.

Production bytes were unchanged for both corrections.

## Restart/readback pressure
Executable capabilities are intentionally not auto-rehydrated from event history because handlers are operational objects. Therefore MS2062 restart semantics are explicit re-registration + deterministic re-derivation, not executable resurrection. Added hostiles require:
- persisted qualified projection/candidate ancestry + explicitly re-registered base request channel reproduce the same specialization ID/signature and rebuild the projection dependency edge;
- a projection staled before shutdown blocks specialization re-derivation after restart.

## Restart hostile exposed projection-version requalification seam
The first restart pressure run returned **8 PASS / 1 FAIL**: a projection changed to a new signature was replayed as a new *current* projection version by historical projection semantics, so MS2062 could re-bind the old proposal candidate vocabulary after restart.

Classification: `CURRENT_CHANGED_PROJECTION_VERSION != EXTERNALLY_REQUALIFIED_TARGET_VOCABULARY`. This was a real MS2062 production defect, not a harness error.

Repair is local to request specialization: for endogenous qualified target projections, current `signature_sha256` must still equal the exact externally-qualified proposal candidate digest before its bucket vocabulary can be bound. A changed signature therefore requires the existing fresh external requalification/reactivation path before request specialization can resume. Historical projection `change()` semantics remain untouched.

## Pre-whole-suite result
Focused MS2062: **9/9 PASS in 1.49s**.
Broader historical/projection/recruitment/action-learning/P1A/N1A/MS2057-MS2062 guard: **95/95 PASS in 176.78s**.
Production delta is exactly two files:
- `microseed/development/epistemic.py`
- `microseed/runtime/entity.py`

Research candidate only. Authoritative whole cleanup-neutral regression remains pending before any promotion discussion.
