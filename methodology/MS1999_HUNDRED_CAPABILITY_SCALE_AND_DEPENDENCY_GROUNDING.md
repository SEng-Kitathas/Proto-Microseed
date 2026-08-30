# MS1999 — Hundred-Capability Composition and Dependency-Closure Grounding

Date: 2026-08-30 ET
Status: embodied / direct boundary PASS / verification pending at initial write
Parent: published MS1998 `66052ff913fc481336d96d866200e95e2dd96cd2`

## Question
Does the compositional substrate still preserve caller-free endogenous program construction when the current EFFECT alphabet reaches 100 primitives, and can declared capability dependencies be prevented from bootstrapping executable/current authority when they are missing, stale, deferred, or cyclic?

This campaign deliberately separates three claims:
1. **search/composition scale**;
2. **dependency-closure safety/currentness**;
3. **requalification/recovery after staleness**.

Success on the first two does not silently promote the third.

## Prewrites
- `LARGE_N_INVALIDATION_LOCALITY != LARGE_N_QUALIFICATION_CLOSURE`;
- `INVALIDATION_TERMINATES != CYCLIC_QUALIFICATION_IS_LAWFUL`;
- `DEPENDENCY_CYCLE != AUTHORITY_TO_SELF_SUPPORT`;
- `LOCAL_STALE_SET != LOCAL_EVIDENCE_REACQUISITION_COST`;
- `STRUCTURAL_DEPENDENCY_REFERENCE != EXECUTABLE_DEPENDENCY_CLOSURE`;
- `DEFERRED_DEPENDENCY != INVALID_DEPENDENCY`;
- `CYCLE_REPRESENTABLE != CYCLE_EXECUTABLE`;
- `LOCAL_QUALIFICATION_BIT != TRANSITIVE_CURRENTNESS`;
- `STALED_CAPABILITY != REQUALIFIED_CAPABILITY`.
- `TRANSITIVE_UNUSABILITY != LOCAL_OWNER_STALENESS_ATTRIBUTION`;

## Rejected first repair
A concurrent unsealed draft attempted to reject every missing/forward capability dependency at registration time.

That was pressure-tested against existing earned behavior and rejected. The targeted regression:
- `test_ms1352_integration.py::test_external_qualification_of_rehearsed_whole_enlarges_second_order_capability_closure`

failed because MS1352 intentionally registers higher-order `X` while dependency `BC` is not yet admitted, expects `NO_PATH`, then admits `BC` and expects composition to become available.

The rejected gate would have converted a lawful deferred structural dependency into an admission error.

Therefore MS1999 does **not** ban forward references or cycles at the structural registry layer.

This rejection preserves the older TRCH ceiling:
`CYCLES_ARE_NOT_INVALID_BY_DEFAULT`.

## Actual repair
### One ephemeral dependency-closure assessor
`CapabilityRegistry.assess_dependency_closure(capability_id)` now computes operational usability over the current declared capability graph.

Properties:
- iterative traversal; no Python recursion dependency;
- checks root and all reachable dependencies for registered presence, qualified/shadow-qualified lifecycle, and local `CURRENT` state;
- memoizes completed nodes within one assessment;
- detects an active-path cycle;
- returns `UNKNOWN_INCOMPLETE` with authority NONE on missing/stale/unqualified ancestry;
- returns `DEPENDENCY_CYCLE_UNQUALIFIED:<path>` for a cycle when no separately qualified cycle-closure mechanism exists;
- does **not** mutate contracts, install a manager, or declare the graph shape false;
- returns `CURRENT_DEPENDENCY_CLOSURE` only when the full reachable graph is currently grounded.

`CapabilityRegistry.is_current(...)` is the compact boolean adapter over that assessment.

### Use-time defense
Direct capability invocation now requires the full dependency closure before the handler can run.

Relevant authority-bearing consumers that previously used only the local qualification/currentness bit were moved to the same registry-owned closure, including:
- current epistemic feasibility routes;
- current EFFECT action alphabet derivation;
- epistemic program creation/revalidation;
- recruitment proposal currentness;
- rehearsal/action/probe currentness boundaries;
- raw-observation and predictive-relation currentness checks;
- operational trace/topology capability premises.

The goal is not a second currentness system. It is to make the registry's declared dependency graph part of the meaning of “current capability” everywhere the capability is used.

### Candidate admission defense
For a dependency-bearing capability candidate:
- every declared dependency must have a current dependency closure at admission time;
- missing/stale/cyclic dependency ancestry cannot be converted into executable authority by an external qualification ticket;
- if `dependency_epochs` are supplied in the operational signature, their dependency-ID set must exactly match the declared dependency set and each epoch must still match;
- dependency-free legacy candidates remain unaffected;
- dependency-bearing legacy candidates without an epoch signature remain admissible **only when their declared dependencies are actually current**, preserving MS852/MS1352 behavior.

## Direct boundary A — 100 current EFFECT capabilities
The MS1996 endogenous-program fixture is enlarged to exactly 100 current EFFECT primitives:
- existing fixture primitives plus the useful opaque chain `K-17 -> M-23 -> R-41`;
- fallback primitive;
- 94 opaque distractor primitives.

No caller-preferred program/action is supplied.

Observed direct result:
- generator token count: 100;
- useful generated program remains `K-17 -> M-23 -> R-41`;
- two hostile history insertion orders produce the same candidate ID and SHA-256;
- bounded `max_nodes=1` still reports `SEARCH_BUDGET_EXHAUSTED_NOT_SATURATED` rather than false “no discriminator”;
- staling `R-41` stales exactly `R-41` and `FEAS-R-41` and removes the target program from current generation;
- arbitration then abstains `CURRENT_GENERATOR_TRANSITION_UNREPRESENTED`;
- no action intent or execution occurs.

A separate 100-EFFECT equal-information hostile produces two admissible programs and retains:
`MULTIPLE_CURRENT_EPISTEMIC_OPPORTUNITIES / NO_UNIQUE_STRICT_PARTITION_REFINEMENT`, with selection/execution/truth authority NONE.

Earned positive:
`ONE_HUNDRED_CURRENT_EFFECT_CAPABILITIES_CAN_PRESERVE_CALLER_FREE_ENDOGENOUS_PROGRAM_CONSTRUCTION_BUDGET_CURRENTNESS_AND_INSERTION_ORDER_BOUNDARIES_WITHOUT_A_NEW_SEARCH_MANAGER`.

This is not a universal hundred-capability cognition claim. It is one explicit current EFFECT alphabet and represented decision surface.

## Direct boundary B — dependency grounding
### Missing dependency
A SHADOW_QUALIFIED contract may structurally name an absent dependency. Registration succeeds so deferred composition remains representable.

Before that dependency exists:
- dependency closure = `UNKNOWN_INCOMPLETE`;
- reason = `DEPENDENCY_NOT_REGISTERED:<id>`;
- direct invoke = `UNKNOWN_INCOMPLETE`;
- authority = NONE.

### Deferred dependency
A structurally registered capability depending on not-yet-present `LATER` is initially unusable. After `LATER` is registered/current, the same existing capability obtains `CURRENT_DEPENDENCY_CLOSURE` and can invoke without replacement or hidden mutation.

Thus:
`DEFERRED_STRUCTURE_CAN_BECOME_USABLE_FROM_ACTUAL_CLOSURE`.

### Cycle
Two SHADOW_QUALIFIED contracts `A -> B -> A` may remain structurally represented.

Both assessments return `UNKNOWN_INCOMPLETE / DEPENDENCY_CYCLE_UNQUALIFIED` and direct invocation returns authority NONE.

MS1999 does **not** claim “cycles are invalid.” It claims only:
`UNQUALIFIED_CAPABILITY_DEPENDENCY_CYCLE != EXECUTABLE_CURRENTNESS`.

### Candidate admission
External qualification cannot admit:
- a candidate whose declared dependency is absent;
- a candidate whose declared dependency is stale;
- a candidate whose explicit dependency-epoch binding omits a declared dependency.

### Endogenous action alphabet
Missing/cyclic locally-qualified EFFECT contracts are omitted from the current endogenous EFFECT alphabet because the alphabet now consumes full registry currentness closure rather than the local qualification bit.

Earned repair:
`EXECUTABLE_CAPABILITY_CURRENTNESS_CAN_REQUIRE_A_FULLY_REGISTERED_CURRENT_ACYCLIC_DEPENDENCY_CLOSURE_WHILE_PRESERVING_UNRESOLVED_GRAPH_SHAPES_AS_NONAUTHORITATIVE_REPRESENTATION`.

Here “acyclic closure” means the currently executable dependency ancestry contains no unqualified cycle. It does not assert that cyclic structures are universally invalid.

## Direct boundary C — locality and deep traversal
Synthetic topology arm:
- 100-capability branch graph (10 × depth 10): one branch-root invalidation stales 10, leaf invalidation stales 1;
- 101-capability shared-root graph: shared-root invalidation stales all 101;
- 1,500-deep chain: dependency closure visits all 1,500 nodes with max depth 1,500 and completes without recursive-stack failure.

This earns only traversal/locality evidence. Timing values are diagnostic and machine-dependent, not doctrine.

## Earned negative — recovery is still missing
After local capability invalidation:
- the stale capability and transitive dependents correctly refuse current use;
- same-ID candidate nomination is blocked by duplicate capability identity;
- no general `requalify_capability` / explicit same-ID replacement lifecycle exists.

Therefore:
`LOCAL_INVALIDATION_AT_SCALE_DOES_NOT_YET_HAVE_A_LAWFUL_SAME_ID_CAPABILITY_REQUALIFICATION_CLOSURE_PATH`.

MS1999 must not claim full large-N qualification closure until that recovery lifecycle is either earned or an explicit replacement/reentry law is demonstrated.

## Mechanism verdict
One narrow missing mechanism was real:
**ephemeral transitive dependency-closure assessment at use/admission time**.

This is not a dependency manager. It owns no new persistent state and does not schedule requalification.

`MISSING_CURRENTNESS_GUARD != MISSING_GLOBAL_MANAGER`.

## Authority ceiling
- dependency graph shape truth: NONE;
- cycle semantic validity: NONE;
- candidate qualification authority: remains external;
- action-selection authority gain: NONE;
- execution authority gain: NONE;
- truth authority gain: NONE;
- automatic stale-capability recovery: NONE.

## Remaining blocker / next campaign
The next scale/currentness question is no longer whether missing/cyclic dependency ancestry can bootstrap use. It cannot for the tested surfaces.

The remaining blocker is:
**lawful capability recovery after staleness**.

Pressure options must distinguish:
1. external requalification of the same durable capability identity with a new epoch;
2. explicit replacement capability identity with lineage/supersession;
3. bounded reentry from historical capability evidence.

Do not choose one by convenience. First audit historical reentry/currentness mechanisms and the reason same-ID capability requalification was never integrated.

## Whole-suite regression scar — local owner attribution versus transitive unusability
The first frozen whole-suite witness completed with **800 PASS / 1 FAIL**.

Failing earned behavior:
`tests/embodiment/test_ms1598_observation_basis_ingress.py::test_observation_channel_currentness_is_checked_even_if_basis_metadata_is_still_current`.

The new transitive `CapabilityRegistry.is_current(...)` made a locally-current BASIS appear unusable when its OBS dependency was stale. That operational result was correct, but the ingress then misattributed the local owner failure as `OBSERVATION_BASIS_NOT_CURRENT` instead of the existing MS1598 diagnostic `OBSERVATION_CAPABILITY_NOT_CURRENT`.

Repair:
- add `CapabilityRegistry.is_locally_current(...)` for owner-specific metadata attribution only;
- preserve transitive `is_current(...)` / `invoke(...)` for actual executable usability;
- check local BASIS and OBS owner state independently before transitive invocation.

This preserves both laws:
- `LOCAL_OWNER_STALENESS_ATTRIBUTION` remains exact;
- `TRANSITIVE_DEPENDENCY_CLOSURE` remains mandatory for use.

Targeted post-repair regression: MS1598 + MS1999 **13/13 PASS**.

The failed 800/1 whole run is retained as a rejected seal witness and must not be promoted.

## Verification required before seal
- direct MS1999 scratch;
- MS852 + MS1352 deferred/candidate compatibility;
- capability currentness/invalidation lineage;
- MS1996/MS1998 endogenous-program/context regression;
- MS1999 tests;
- self-test;
- compileall;
- `git diff --check`;
- whole cleanup-neutral embodiment suite;
- frozen executable/test hashes post-whole;
- local Git seal;
- push research branch;
- independent remote ref readback.
