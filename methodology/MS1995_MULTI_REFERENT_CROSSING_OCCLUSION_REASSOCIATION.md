# MS1995 — Multi-Referent Crossing, Occlusion, and Appearance-Change Reassociation

Date: 2026-08-29 ET
Status: VERIFIED / ready for local seal and research-branch publication
Parent: published MS1994 `cd60c48a0fd8a4e0fea0995ca8550af2f8c394d3`

## Question
Can the existing operational referent substrate preserve lawful re-association when multiple referents change presentation position, cross/interleave, temporarily disappear, and return under a different raw appearance transform?

Can intervention traces still discriminate retained versus lost causal history after those changes without turning channel position into identity or guessing through ambiguous evidence?

Prewrites:
- `CHANNEL_POSITION != REFERENT_IDENTITY`;
- `TRAJECTORY_CROSSING != REFERENT_SWAP`;
- `OCCLUSION_GAP != IDENTITY_BREAK`;
- `REASSOCIATION_SUPPORT != NUMERICAL_IDENTITY`;
- `AMBIGUOUS_POST_GAP_EVIDENCE != PERMISSION_TO_GUESS`;
- `PERFECT_COPY_OPERATIONAL_HISTORY != NUMERICAL_IDENTITY`.

## Existing substrate
The experiment reuses unchanged:
- boundary-coherence nomination;
- affordance-relative referent signatures;
- gap deferral from MS1969;
- intervention-bound trace evidence from MS1993;
- exact trace-topology discipline from MS1994.

No persistent object ID, tracker, semantic class, or genealogy layer is introduced.

## Process world
Server:
`research/substrate_shadow/referent_crossing_occlusion_world_server.py`.

Two latent evaluator sources generate four opaque channels through phase-specific presentation maps and affine appearance transforms.

### PRE
Mapping:
- A -> channels `[0,1]`;
- B -> `[2,3]`.

### CROSS
Presentation interleaves/crosses:
- A -> `[0,3]`;
- B -> `[1,2]`.

Raw channel scales and offsets also change.

### OCCLUDE_A
Only B's two channels remain visible. With only one coherent visible group, boundary nomination correctly returns:
`UNKNOWN_INCOMPLETE / BOUNDARY_SYNCHRONY_DOES_NOT_IDENTIFY_DISTINCT_REFERENTS`.

The system does not infer A's identity from absence.

### GAP
No channels visible.

### POST
Presentation swaps:
- A -> `[2,3]`;
- B -> `[0,1]`.

A new affine appearance transform changes all raw channel magnitudes while preserving action/non-action boundary structure.

## Represented traces
While the referents occupy CROSS positions, two idempotent represented interventions are applied:
- `FX-MARK-A`;
- `FX-MARK-B`.

Each mark changes exactly the currently nominated group for its referent.

After POST re-association, the same represented marker is re-applied:
- zero effect -> the prior mark is retained;
- current-group-local effect -> the prior mark was absent/lost.

This retention test depends on action effect at the current re-associated group, not equality of pre/post raw channel values. It therefore survives the presentation and appearance transforms used here.

## Hidden variants
1. `PERSIST`: both evaluator generations persist; both marks retained.
2. `REPLACE_A_UNMARKED`: A generation changes and A mark is lost; B persists.
3. `REPLACE_B_UNMARKED`: B generation changes and B mark is lost; A persists.
4. `REPLACE_BOTH_PERFECT_COPY`: both generations change, but all represented affordances and both marks are copied.
5. `ALIASED_POST`: post-gap A/B action effects become symmetric, so every visible channel has the same boundary response.

Generation state is evaluator-only falsification evidence and is not part of the organism route.

## Boundary result
### Presentation crossing
The same two affordance signatures follow different concrete channel groups:
- PRE: A `[0,1]`, B `[2,3]`;
- CROSS: A `[0,3]`, B `[1,2]`;
- POST: A `[2,3]`, B `[0,1]`.

Thus re-association follows action-response content rather than fixed channel position.

### Occlusion
During full A occlusion, the local result is explicitly `UNKNOWN_INCOMPLETE`. After the gap, when sufficient differentiated evidence returns, both prior signatures re-associate again.

So:
`OCCLUSION_GAP != IDENTITY_BREAK`, but also
`OCCLUSION_GAP != PERMISSION_TO_ASSUME_PERSISTENCE`.

### Trace retention after crossing/appearance change
Persistent:
- A RETAINED;
- B RETAINED.

Replace A unmarked:
- A LOST, detected by marker effect on POST A group `[2,3]`;
- B RETAINED.

Replace B unmarked:
- A RETAINED;
- B LOST, detected on POST B group `[0,1]`.

The trace test follows the re-associated referent rather than its earlier presentation coordinates.

### Perfect-copy hostile
Both evaluator generations change, but all organism-visible affordance signatures and both trace-retention tests match the persistent world.

Therefore full operational-history copying still cannot establish numerical identity.

### Aliased post hostile
All post-gap action-response boundaries become symmetric. Boundary nomination returns `UNKNOWN_INCOMPLETE` and trace tests are deliberately not used to guess a referent partition.

Earned policy:
`AMBIGUOUS_EVIDENCE -> UNKNOWN_INCOMPLETE_NO_GUESS`.

## Earned
`AFFORDANCE_RELATIVE_REASSOCIATION_PLUS_IDEMPOTENT_INTERVENTION_TRACE_TESTS_CAN_PRESERVE_OPERATIONAL_MULTI_REFERENT_CONTINUITY_THROUGH_PRESENTATION_CROSSING_OCCLUSION_AND_APPEARANCE_CHANGE_WHILE_DEFERRING_ON_ALIASED_EVIDENCE`.

Authority ceiling:
- crossing/reassociation: operational only;
- occlusion: defer under insufficient visible partition evidence;
- ambiguity: explicit unknown, no guess;
- numerical identity: NONE;
- semantic reference: NONE;
- language: NONE.

## Mechanism verdict
No new referent-core mechanism is required for this boundary.

Existing affordance-relative signatures already carry the invariance needed for channel permutation. Existing intervention traces can be tested by current action effect rather than raw-value equality. Existing nomination already refuses symmetric evidence.

A persistent object tracker or object-ID manager would therefore still be premature.

## Remaining boundary
The next high-value question is no longer simple presentation crossing. It is whether developmental pressure can construct useful intervention/probe candidates from learned opaque structure and already-qualified primitives without caller-supplied semantic action names, while keeping candidate construction separate from execution permission.

Longer many-referent partial-observability campaigns remain needed as rich-world falsifiers.

## Final verification
- direct MS1995 boundary execution: PASS;
- focused referent regression through MS1995: `job-e68615bd6252` -> **17/17 PASS in 2.67s**, stderr empty;
- whole cleanup-neutral embodiment suite: `job-845b93c2ac68` -> **792/792 PASS in 613.52s**, stderr empty;
- Microseed self-test: **81/81 PASS**;
- compileall: PASS;
- `git diff --check`: PASS;
- executable/test candidate hashes remained unchanged from before the whole-suite run through seal preparation.

A later duplicate whole-suite run (`job-ce55bbc849ab`) was deliberately terminated after the stronger earlier whole-suite witness completed successfully; it is not used as a seal witness.

## Seal/publication gate
The pass is eligible to seal. Publication still requires local Git seal, exact research-branch push, and independent remote ref readback matching the seal.
