# MS1972 — Process-Backed Representation Alias Growth

Date: 2026-08-29 ET
Status: reality embodiment of MS1971 generic representation-growth route; no new core mutation
Parent: MS1971 `6e60f78aa8a4dd908f03d526eb19d8f1b4a7692e`

## Discriminator
Can the generic MS1971 history-refinement admission route operate on actual process-backed action/outcome history where the incumbent visible representation provably aliases behaviorally distinct situations?

## Reality world
Server:
`research/substrate_shadow/representation_alias_world_server.py`

The world exposes two externally selectable starting visible contexts:
- `s0`;
- `r`.

Action `PREP` maps either context to the same visible state `s1`, preserving only a hidden process-side context.

Action `B` from the aliased visible state `s1` produces:
- prior visible context `s0` -> `sx`;
- prior visible context `r` -> `s2`.

The current visible state/action pair `(s1,B)` alone is therefore inadequate.

## History acquisition authority
MS1972 does not claim autonomous first-probe authority.

Lawful action execution is explicitly EQUIPPED:
- separate external probe processes generate one-step rehearsal seed observations;
- the live Microseed instance uses those bounded seeds only to nominate lawful action intents;
- the live external process is then acted on through registered EFFECT capabilities;
- `execute_bounded_action(...)` performs the effect;
- `record_bounded_action_outcome_via_observation_basis(...)` authenticates the actual observed result.

Representation discovery later consumes only the resulting owned action/outcome history, not caller-supplied context labels or seed predictions.

Assistance label:
`EXTERNALLY_EQUIPPED_REHEARSAL_SEEDS_FROM_SEPARATE_PROCESS_PROBES`.

## Actual history
Four live two-step chains were executed:
- two `s0 -> PREP -> s1 -> B -> sx`;
- two `r -> PREP -> s1 -> B -> s2`.

Each current `B` intent is bound to the exact preceding `PREP` outcome evidence, preserving the previous-visible-state lineage required by the existing refinement owner.

## Endogenous derivation
`derive_admitted_one_step_visible_history_refinements()` re-derived exactly one current refinement for `(s1,B)`:
- `s0 -> sx`, support 2;
- `r -> s2`, support 2.

Candidate id:
`opaque-one-step-refinement-25544ab0ad1812b4f010`

Candidate SHA-256:
`e43fbc2bc9e74106a061b922b7b7216d1ad677cbb694e10e7671fc83dcad82f9`.

No hidden context was supplied to the derivation. The discriminator is previous **visible** state only.

## External qualification
A separate set of process probes produced held-out outcomes:
- four `s0/s1/B -> sx`, effect 1.2;
- four `r/s1/B -> s2`, effect 1.2.

The external harness verified these rows against the candidate's operational context/outcome split, then appended bounded external qualification evidence.

`ExternalProjectionQualifier` issued a SHADOW_QUALIFIED ticket bound to exact candidate id/digest.

## Generic admission
`admit_one_step_visible_history_refinement_projection(...)` admitted:
- projection id `P-MS1972`;
- origin `ENDOGENOUS_PROPOSAL_EXTERNALLY_QUALIFIED`;
- current frame `F@0`;
- exact candidate digest;
- no deficit ancestry.

## Execution
Durable job:
`job-8decc0b4329a`

Result: PASS / rc=0.

Earned:
`PROCESS_BACKED_ACTUAL_ACTION_HISTORY_CAN_GROW_AND_EXTERNALLY_QUALIFY_A_GENERIC_OPAQUE_PREVIOUS_VISIBLE_STATE_REFINEMENT_WITHOUT_REVISIT_OR_SEMANTIC_CATEGORY`.

## Authority ceiling
- history acquisition: explicitly externally equipped;
- representation derivation: owned actual history, bounded one-step visible context only;
- qualification: external;
- truth authority: NONE;
- hidden-state authority: NONE;
- semantic-category authority: NONE;
- language authority: NONE.

## Scientific effect
`REPRESENTATION_INADEQUACY != NEED_FOR_LANGUAGE` now has direct reality embodiment for this bounded class.

The organism can enlarge one inadequate coarse visible representation using operational history before language is admitted.

## Next discriminator
MS1973 restart/currentness:
After the process, frame and capability bindings disappear at restart, does the persisted refinement/projection remain correctly unusable until current world premises are explicitly reattached? Can compatible reattachment recover the same derived representation without semantic reinstatement?