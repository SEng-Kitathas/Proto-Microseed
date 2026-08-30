# MS1994 — Multiple Intervention-Trace Persistence Under Conflict

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1993 `76db4aa62c802fb744aca4d6a66ad4fb78d3cbd6`

## Question
Does more than one independently bound intervention trace strengthen external operational persistence without collapsing mixed evidence into a score or promoting numerical identity?

Prewrites:
- `MULTIPLE_RETAINED_TRACES != NUMERICAL_IDENTITY`;
- `ONE_LOST_TRACE != PROOF_OF_REPLACEMENT`;
- `TRACE_MAJORITY != IDENTITY_AUTHORITY`;
- `PERSISTENT_CAUSAL_TRACE != METAPHYSICAL_SAMENESS`;
- `UNRELATED_NUISANCE_CHANGE != TARGET_PERSISTENCE_EVIDENCE`.

## Why MS1994
MS1993 showed that one retained content-bound intervention trace can add real operational persistence evidence beyond bare affordance reappearance. It also preserved the perfect-copy counterexample: a hidden replacement carrying the same trace remains indistinguishable from persistence.

The next question is whether multiple traces should be collapsed into a scalar confidence or identity vote.

They should not be assumed to. MS1994 therefore preserves exact per-trace topology.

## Process world
Server:
`research/substrate_shadow/referent_multi_trace_world_server.py`.

The evaluator has two latent sources over four opaque channels. Existing represented effects remain:
- `FX-A`;
- `FX-B`;
- `FX-G`.

Two independent represented target interventions are added:
- `FX-MARK-A1` -> target-group delta `(211,307)`;
- `FX-MARK-A2` -> target-group delta `(401,503)`.

An unrelated nuisance intervention exists on the other referent:
- `FX-MARK-B-NOISE` -> nuisance-group delta `(601,709)`.

All marker terms are persistent additive offsets, so the existing affordance-relative action-effect signature remains invariant after marking.

Hidden evaluator variants:
1. `PERSIST`: target generation unchanged; A1+A2 retained;
2. `REPLACE_UNMARKED`: target generation changes; neither A trace retained;
3. `REPLACE_PARTIAL_A1`: target generation changes; A1 retained, A2 lost;
4. `REPLACE_PERFECT_COPY`: target generation changes; both A traces retained;
5. `REPLACE_NUISANCE_ONLY`: target generation changes; target traces lost; unrelated nuisance group changes;
6. `PERSIST_NUISANCE_B`: target generation persists with A1+A2 retained while only the unrelated nuisance group changes.

Generation counters are evaluator-only falsification evidence and are never used by the organism-visible route.

## Boundary construction
Scratch:
`scratch/ms1994_multiple_trace_persistence_conflict.py`.

Existing referent functions are reused unchanged:
- `nominate_by_boundary_coherence(...)`;
- `derive_affordance_relative_referent_signature(...)`.

The target referent is first nominated and affordance-signed. A1 and A2 are then applied sequentially. Each trace digest binds:
- exact represented action ID;
- nominated target group;
- before values;
- after values;
- exact observed delta.

The two target trace deltas are linearly represented as a small exact finite basis. After the gap, the observed target delta relative to the pre-mark baseline is matched only against exact subset sums of that basis. This yields an exact retained-trace topology rather than a scalar score.

No majority rule is used.

## Results
### Persistent
- retained topology: `{A1,A2}`;
- support: `SUPPORTED_BY_ALL_OBSERVED_TRACES`;
- evaluator persistence: true.

### Unmarked replacement
- retained topology: `{}`;
- support: `REFUTED_FOR_ALL_OBSERVED_TRACES`;
- evaluator persistence: false.

This is trace-relative refutation only. It does not prove metaphysical replacement.

### Partial-copy replacement
- retained topology: `{A1}`;
- A1: RETAINED;
- A2: LOST;
- support: `MIXED_TRACE_EVIDENCE`;
- evaluator persistence: false.

The mixed topology is preserved as mixed. It is not averaged into a confidence score and is not resolved by majority voting.

### Perfect-copy replacement
- retained topology: `{A1,A2}`;
- support: `SUPPORTED_BY_ALL_OBSERVED_TRACES`;
- evaluator persistence: false.

Organism-visible evidence remains identical to the persistent case at this trace resolution. Therefore even multiple retained causal traces do not establish numerical identity.

### Nuisance-only replacement
- target retained topology: `{}`;
- unrelated nuisance group changes;
- support: `REFUTED_FOR_ALL_OBSERVED_TRACES`;
- evaluator persistence: false.

An unrelated environmental change cannot masquerade as target persistence evidence.

### Persistent target with unrelated nuisance change
- retained topology: `{A1,A2}`;
- unrelated nuisance group changes;
- support remains `SUPPORTED_BY_ALL_OBSERVED_TRACES`;
- evaluator persistence: true.

This closes the orthogonal direction: nuisance outside the target neither fabricates nor falsely destroys valid target persistence evidence.

## Earned
`MULTIPLE_INDEPENDENT_INTERVENTION_TRACES_CAN_PRESERVE_EXACT_OPERATIONAL_PERSISTENCE_EVIDENCE_TOPOLOGY_ACROSS_A_GAP_WITHOUT_PROMOTING_NUMERICAL_IDENTITY`.

Authority ceiling:
- operational persistence authority: `TRACE_TOPOLOGY_RELATIVE_ONLY`;
- partial conflict policy: `PRESERVE_MIXED_EVIDENCE_NO_MAJORITY_COLLAPSE`;
- numerical identity: NONE;
- semantic reference: NONE;
- language: NONE.

Remaining boundary:
`PERFECT_COPY_WITH_ALL_RETAINED_TRACES_REMAINS_OPERATIONALLY_INDISTINGUISHABLE_FROM_PERSISTENCE`.

## Mechanism verdict
No new referent-core mechanism is required for this level.

The existing referent substrate plus exact represented intervention traces can preserve a finite evidence topology compositionally. A persistent-object ID layer, confidence-voting manager, semantic object system, or genealogy authority would be premature.

## Final verification
- focused referent regression through MS1994: `job-6ca5c8f0c398` -> **16/16 PASS in 2.30s**;
- whole cleanup-neutral embodiment suite: `job-72006a068385` -> **791/791 PASS in 700.65s**;
- whole-suite stderr: empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS;
- executable/test candidate hashes were frozen before focused/whole verification and matched exactly after the whole-suite pass.

## Concurrency scar
During initial construction, a concurrent writer briefly created a second untracked MS1994 scratch draft targeting a different world contract. That draft was removed by the writer, after which the same four intended MS1994 artifacts were rewritten once into the current reconciled candidate. Verification did not begin until those four files were stable. The focused and whole-suite witnesses therefore apply to the reconciled frozen tree, not to either earlier draft.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
