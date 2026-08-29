# MS1971 — Generic History-Refinement Projection Admission

Date: 2026-08-29 ET
Status: minimal core embodiment after pre-repair scoping violation
Parent: MS1970 `ac2a215c23e055f0f3ac6b4a5bbec0af50c4d32e`

## Scientific discriminator
When the incumbent visible representation aliases behaviorally distinct operational situations, can Microseed grow an opaque discriminating representation from owned actual history without supplied semantic categories or self-qualification?

Prewrites:
- `REPRESENTATION_INADEQUACY != NEED_FOR_LANGUAGE`;
- `NEW_OPERATIONAL_DISCRIMINATOR != SEMANTIC_CATEGORY`;
- `REPRESENTATION_GROWTH != SELF_QUALIFICATION`;
- `CONSTRUCTOR_DISCOVERY != ONTOLOGY_TRUTH`.

## Existing mechanism audit
The project already contains a bounded representation-growth mechanism:

`derive_admitted_one_step_visible_history_refinements()`
+
`discover_one_step_visible_history_refinements(...)`

It derives an `OpaqueOneStepVisibleHistoryRefinementCandidate` only when owned admitted history shows:
- the same current visible state/action slot;
- at least two distinct previous visible-state contexts;
- recurrent support per context;
- endpoint unanimity inside each context;
- different endpoints across contexts;
- one current operational frame.

The candidate is explicitly proposal-only and grants NONE for:
- truth;
- hidden state;
- causal explanation;
- previous action identity;
- evidence independence;
- deeper-history authority.

`ExternalProjectionQualifier` already accepts this candidate content by exact candidate id/digest and external qualification evidence.

## Pre-repair scoping violation
Scratch:
`scratch/ms1971_generic_history_refinement_admission_hostile.py`

Pre-repair durable job:
`job-9ba92e94341d`

Observed:
- owned actual history derived exactly one refinement for `(s1,B)`;
- contexts were `s0 -> sx` and `r -> s2`, each support 2;
- external projection ticket was SHADOW_QUALIFIED;
- revisit-scoped admission rejected because the existing deficit was not `REVISIT_REQUIRED`;
- `register_epistemic_projection(...)` is explicitly supplied-only (`Register one supplied opaque evidence coordinate; never discover one.`);
- no generic endogenous history-refinement admission method existed.

Earned pre-repair conclusion:
`HISTORY_REFINEMENT_DERIVATION_AND_EXTERNAL_QUALIFICATION_EXIST_BUT_GENERIC_ENDOGENOUS_PROJECTION_ADMISSION_IS_ARTIFICIALLY_REVISIT_SCOPED`.

This did **not** demonstrate a missing representation discovery mechanism. It demonstrated a missing generic embodiment/admission route for an already-earned candidate type.

## Minimum core repair
Added one method on the existing Microseed facade:

`admit_one_step_visible_history_refinement_projection(ticket, *, projection_id=None)`

The method:
1. re-derives the current refinement surface from owned admitted history at admission time;
2. matches the external ticket against exact current candidate id + candidate digest;
3. requires exactly one current match;
4. re-validates the external qualification ticket through existing `validate_external_projection_ticket(...)`;
5. rechecks the candidate's operational frame currentness;
6. registers an existing `EpistemicProjectionRecord` with origin `ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED`;
7. persists a bounded admission event with explicit authority ceilings.

It does **not** add:
- a new registry;
- a new learner;
- a new constructor;
- a hidden-state model;
- a semantic-category owner;
- a deficit lifecycle;
- an execution permission path.

The caller cannot supply refinement content. The external ticket may identify exact candidate content, but the candidate must independently re-exist in the current owned-history surface.

## Post-repair embodiment
Post-repair scratch job:
`job-b8594c26cead`

Result: `GENERIC_ADMISSION_COMPOSED` / rc=0.

Projection:
- id `P-MS1971-GENERIC`;
- origin `ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED`;
- exact candidate digest `da94bf288edae9f715d3aba9fc3a79e66ca869840d0af39548ebea28b83a82a2`;
- current frame `F@0`;
- no deficit ancestry;
- truth/hidden-state/semantic-category/execution authority NONE.

## Consequential reuse / hostiles
Regression:
`tests/embodiment/test_ms1971_generic_history_refinement_projection_admission.py`

Focused job `job-8caa7292433f`: **3/3 PASS**.

Verified:
1. generic admitted projection is consumed by the existing projection-conditioned relation-routing stack;
2. exact current predecessor evidence derives the `s0` bucket without caller bucket labeling and selects the independently qualified `sx` relation;
3. bucket-selection / hidden-state / deeper-history authority remain NONE;
4. zero-evidence external projection tickets fail closed;
5. post-ticket frame staleness prevents admission;
6. no revisit deficit is required to make the current representation usable.

## Earned result
`OWNED_HISTORY_DERIVED_REFINEMENT_CAN_BE_EXTERNALLY_QUALIFIED_AND_GENERically_ADMITTED_AS_OPAQUE_CURRENT_PROJECTION_WITHOUT_REVISIT_OR_SEMANTIC_AUTHORITY`.

Interpretation:
The representation-growth **mechanism** was already present. MS1971 removes a campaign-shaped admission bottleneck so the earned representation can participate in the general projection/routing substrate.

## Authority ceiling
- projection discovery authority: bounded owned-history derivation only;
- qualification authority: external only;
- truth authority: NONE;
- hidden-state authority: NONE;
- semantic-category authority: NONE;
- causal-explanation authority: NONE;
- execution authority: NONE;
- language authority: NONE.

## Remaining representation-growth boundary
MS1971 grows only one **previous-visible-state** discriminator in a fixed one-step grammar. It does not establish:
- arbitrary history-depth growth;
- raw-coordinate constructor expansion;
- automatic grammar expansion;
- semantic ontology discovery;
- self-qualification;
- general state representation learning.

Next pressure should move from fixture-owned action history into a process-backed reality world where the coarse current visible token aliases two operational situations and test whether the generic route survives restart/currentness and held-out external qualification.